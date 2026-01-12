"""
LLM-based API extractor for arbitrary source code.

Framework-agnostic extraction using LLM reasoning instead of hard-coded patterns.
"""

import os
import json
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

import openai
from schema import APIDefinition, HTTPMethod
from prompts import (
    EXTRACTION_SYSTEM_PROMPT,
    EXTRACTION_USER_PROMPT_TEMPLATE,
    CONTEXT_ENRICHMENT_PROMPT,
    BATCH_EXTRACTION_PROMPT
)

logger = logging.getLogger(__name__)


class LLMAPIExtractor:
    """LLM-based API extractor."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize LLM API extractor.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model to use (gpt-4o-mini, gpt-4, gpt-3.5-turbo)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY env var or pass api_key.")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = model
        
        # Language detection patterns (simple heuristics)
        self.language_patterns = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.go': 'Go',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.rs': 'Rust',
            '.cs': 'C#',
        }
        
        # Framework detection (basic patterns)
        self.framework_patterns = {
            'Python': {
                'from fastapi import': 'FastAPI',
                'from flask import': 'Flask',
                'from django': 'Django',
                'from tornado': 'Tornado',
            },
            'JavaScript': {
                'express()': 'Express',
                'require(\'koa\')': 'Koa',
                '@nestjs': 'NestJS',
                'fastify': 'Fastify',
            },
            'TypeScript': {
                '@nestjs': 'NestJS',
                'express()': 'Express',
            },
        }
    
    def detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension."""
        ext = Path(file_path).suffix.lower()
        return self.language_patterns.get(ext, 'Unknown')
    
    def detect_framework(self, language: str, source_code: str) -> Optional[str]:
        """Detect framework from source code."""
        patterns = self.framework_patterns.get(language, {})
        for pattern, framework in patterns.items():
            if pattern in source_code:
                return framework
        return None
    
    def extract_from_file(self, file_path: str, source_code: str) -> List[Dict[str, Any]]:
        """
        Extract APIs from a single source file.
        
        Args:
            file_path: Path to source file
            source_code: Content of source file
            
        Returns:
            List of extracted API definitions (raw dicts)
        """
        logger.info(f"Extracting APIs from {file_path}")
        
        language = self.detect_language(file_path)
        framework = self.detect_framework(language, source_code[:1000])  # Check first 1000 chars
        
        # Truncate source code if too long (context window limits)
        max_chars = 30000  # Leave room for prompt and response
        if len(source_code) > max_chars:
            logger.warning(f"Source code too long ({len(source_code)} chars), truncating to {max_chars}")
            source_code = source_code[:max_chars] + "\n... [truncated]"
        
        # Build prompt
        user_prompt = EXTRACTION_USER_PROMPT_TEMPLATE.format(
            file_path=file_path,
            language=language,
            framework=framework or "Unknown",
            source_code=source_code
        )
        
        try:
            # Call LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,  # Low temperature for consistency
                response_format={"type": "json_object"} if self.model != "gpt-4o-mini" else None
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse response
            # Handle both JSON object and JSON array responses
            if content.startswith('{'):
                data = json.loads(content)
                # If wrapped in object, look for 'apis' or 'endpoints' key
                apis = data.get('apis', data.get('endpoints', [data]))
            elif content.startswith('['):
                apis = json.loads(content)
            else:
                # Try to extract JSON from markdown code blocks
                if '```json' in content:
                    json_start = content.find('```json') + 7
                    json_end = content.find('```', json_start)
                    content = content[json_start:json_end].strip()
                elif '```' in content:
                    json_start = content.find('```') + 3
                    json_end = content.find('```', json_start)
                    content = content[json_start:json_end].strip()
                
                data = json.loads(content)
                apis = data.get('apis', data.get('endpoints', [data]))
            
            # Ensure it's a list
            if not isinstance(apis, list):
                apis = [apis]
            
            # Add file context to each API
            for api in apis:
                api['handler_file'] = file_path
                api['_extracted_at'] = datetime.utcnow().isoformat()
            
            logger.info(f"Extracted {len(apis)} APIs from {file_path}")
            return apis
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"Response content: {content}")
            return []
        except Exception as e:
            logger.error(f"Error extracting APIs from {file_path}: {e}")
            return []
    
    def enrich_with_context(self, apis: List[Dict[str, Any]], source_directory: str) -> List[Dict[str, Any]]:
        """Enrich APIs with service/component context."""
        if not apis:
            return apis
        
        # Infer service name from directory structure
        path_parts = Path(source_directory).parts
        service_name = None
        for part in reversed(path_parts):
            if part in ['apps', 'services', 'src', 'api']:
                break
            service_name = part
        
        # Add inferred context
        for api in apis:
            if 'service_name' not in api or not api['service_name']:
                api['service_name'] = service_name
        
        return apis
    
    def normalize_api(self, api_dict: Dict[str, Any], file_path: str) -> APIDefinition:
        """Convert raw API dict to normalized APIDefinition."""
        # Generate ID from method + path
        method = api_dict.get('method', 'GET').upper()
        path = api_dict.get('path', '/')
        
        # Ensure method and path exist
        if not method or not path:
            raise ValueError(f"API definition missing method or path: {api_dict}")
        
        api_id = hashlib.md5(f"{method}:{path}".encode()).hexdigest()[:12]
        
        # Validate method
        try:
            http_method = HTTPMethod(method) if method in [m.value for m in HTTPMethod] else HTTPMethod.GET
        except (ValueError, AttributeError):
            http_method = HTTPMethod.GET
        
        return APIDefinition(
            id=api_id,
            method=http_method,
            path=path,
            handler_name=api_dict.get('handler_name'),
            handler_file=api_dict.get('handler_file', file_path),
            handler_line=api_dict.get('handler_line'),
            handler_module=api_dict.get('handler_module'),
            service_name=api_dict.get('service_name'),
            service_type=api_dict.get('service_type'),
            summary=api_dict.get('summary'),
            description=api_dict.get('description'),
            tags=api_dict.get('tags', []),
            deprecated=api_dict.get('deprecated', False),
            parameters=api_dict.get('parameters', []),
            request_body_schema=api_dict.get('request_body_schema'),
            responses=api_dict.get('responses', []),
            auth_required=api_dict.get('auth_required', False),
            auth_type=api_dict.get('auth_type'),
            scopes=api_dict.get('scopes', []),
            extracted_at=datetime.fromisoformat(api_dict.get('_extracted_at', datetime.utcnow().isoformat())),
            source='llm',
            confidence=api_dict.get('confidence', 0.8)
        )
    
    def extract_from_directory(self, source_dir: str, extensions: Optional[List[str]] = None) -> List[APIDefinition]:
        """
        Extract APIs from all files in a directory.
        
        Args:
            source_dir: Root directory to scan
            extensions: File extensions to include (default: .py, .js, .ts, .java, .go, .rb)
            
        Returns:
            List of normalized API definitions
        """
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.java', '.go', '.rb', '.php', '.rs', '.cs']
        
        source_path = Path(source_dir)
        if not source_path.exists():
            raise ValueError(f"Source directory does not exist: {source_dir}")
        
        all_apis = []
        files_processed = 0
        
        # Walk directory tree
        for file_path in source_path.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in extensions:
                # Skip test files, migrations, etc.
                if any(skip in str(file_path) for skip in ['test', '__pycache__', '.git', 'migrations', 'node_modules']):
                    continue
                
                try:
                    source_code = file_path.read_text(encoding='utf-8')
                    raw_apis = self.extract_from_file(str(file_path.relative_to(source_path)), source_code)
                    
                    # Enrich with context
                    enriched = self.enrich_with_context(raw_apis, str(source_path))
                    
                    # Normalize
                    for api_dict in enriched:
                        try:
                            api_def = self.normalize_api(api_dict, str(file_path.relative_to(source_path)))
                            all_apis.append(api_def)
                        except Exception as e:
                            logger.warning(f"Failed to normalize API {api_dict}: {e}")
                    
                    files_processed += 1
                    
                except Exception as e:
                    logger.warning(f"Failed to process {file_path}: {e}")
                    continue
        
        logger.info(f"Processed {files_processed} files, extracted {len(all_apis)} APIs")
        return all_apis
