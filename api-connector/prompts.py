"""
LLM prompts for API extraction from source code.

These prompts are designed to work with arbitrary languages and frameworks,
using LLM reasoning to infer API definitions without hard-coded patterns.
"""

EXTRACTION_SYSTEM_PROMPT = """You are an expert API extraction assistant. Your task is to analyze source code and extract API endpoint definitions in a structured format.

You must identify:
1. HTTP methods and paths
2. Request handlers (functions, classes, methods)
3. Parameters (query, path, body, headers)
4. Response definitions
5. Authentication/authorization requirements
6. Related services or components

You should work with ANY language or framework:
- Python (FastAPI, Flask, Django, Tornado)
- Node.js (Express, Koa, NestJS, Fastify)
- Java (Spring Boot, JAX-RS, Spark)
- Go (Gin, Echo, Fiber, chi)
- Ruby (Rails, Sinatra)
- PHP (Laravel, Symfony)
- And any other web frameworks

Extract APIs even when:
- Framework decorators/routes are not standard
- Code is incomplete or has errors
- Multiple frameworks are mixed
- APIs are defined in configuration files
- Dynamic routing is used

Be thorough and extract all identifiable API endpoints. If you're uncertain, include it with a lower confidence score."""


EXTRACTION_USER_PROMPT_TEMPLATE = """Analyze the following source code file and extract all API endpoint definitions.

File path: {file_path}
Language: {language}
Framework (if identifiable): {framework}

Source code:
```
{source_code}
```

Provide a JSON array of API definitions. Each API must include:
- method: HTTP method (GET, POST, PUT, DELETE, PATCH, etc.)
- path: Endpoint path (e.g., "/api/v1/users/{id}")
- handler_name: Name of the function/method handling this endpoint
- handler_line: Line number where handler starts
- summary: Brief description of what this endpoint does
- parameters: Array of parameter objects with {name, type, location, required}
- responses: Array of response objects with {status_code, description}
- auth_required: Boolean indicating if authentication is required
- tags: Array of relevant tags/categories

Be precise with paths - include path parameters in curly braces like {id}.
Include all relevant endpoints even if they're defined in middleware, decorators, or configuration.

Return ONLY valid JSON, no additional text."""


CONTEXT_ENRICHMENT_PROMPT = """Given the following API endpoints extracted from a codebase, enrich them with:
1. Service/component context (infer from directory structure and imports)
2. Relationships between APIs (common patterns, shared resources)
3. Missing metadata that can be inferred from context

APIs:
{apis_json}

Additional context:
- Source directory: {source_directory}
- Files in directory: {files_list}

Return the enriched API definitions as a JSON array with the same structure, but with additional fields:
- service_name: Inferred service/component name
- handler_module: Module/package name
- related_apis: IDs of related endpoints (for now, use method+path as ID)
- description: Enhanced description if missing

Return ONLY valid JSON."""


BATCH_EXTRACTION_PROMPT = """You have analyzed multiple files from a codebase. Now consolidate and deduplicate the API definitions, resolve conflicts, and identify relationships.

API definitions from all files:
{all_apis_json}

Tasks:
1. Deduplicate identical endpoints
2. Merge metadata when endpoints appear in multiple files
3. Identify related APIs (group by path prefix, shared handlers, etc.)
4. Infer service boundaries based on directory structure
5. Add cross-references in related_apis field

Return a consolidated JSON array with:
- Unique API definitions (deduplicated)
- Enriched metadata
- Service assignments
- Related API references

Return ONLY valid JSON."""


SCHEMA_INFERENCE_PROMPT = """Analyze the request/response code for this API endpoint and infer the schema.

Endpoint: {method} {path}
Handler code:
```
{handler_code}
```

Infer:
1. Request body schema (if applicable)
2. Response schema
3. Parameter types and constraints

Return a JSON object with:
- request_body_schema: JSON schema object (if applicable)
- response_schema: JSON schema object
- inferred_types: Object mapping parameter names to inferred types

Return ONLY valid JSON."""
