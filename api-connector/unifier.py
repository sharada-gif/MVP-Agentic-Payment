"""
Unified output generator.

Combines API extraction, Terraform analysis, and future log enrichment
into a single normalized JSON output.
"""

import json
import logging
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from schema import (
    UnifiedOutput,
    APIDefinition,
    InfrastructureComponent,
    ServiceDefinition
)
from extractor import LLMAPIExtractor
from terraform_parser import TerraformParser

logger = logging.getLogger(__name__)


class Unifier:
    """Unify all extraction sources into a single output."""
    
    def __init__(self):
        """Initialize unifier."""
        pass
    
    def infer_services(self, apis: List[APIDefinition], infrastructure: List[InfrastructureComponent]) -> List[ServiceDefinition]:
        """Infer service definitions from APIs and infrastructure."""
        services = {}
        
        # Group APIs by service
        for api in apis:
            service_name = api.service_name or 'unknown'
            if service_name not in services:
                services[service_name] = {
                    'name': service_name,
                    'type': api.service_type or 'api',
                    'language': None,
                    'framework': None,
                    'api_ids': [],
                    'infrastructure_ids': []
                }
            services[service_name]['api_ids'].append(api.id)
        
        # Map infrastructure to services
        for infra in infrastructure:
            if infra.service_name:
                if infra.service_name not in services:
                    services[infra.service_name] = {
                        'name': infra.service_name,
                        'type': 'infrastructure',
                        'api_ids': [],
                        'infrastructure_ids': []
                    }
                services[infra.service_name]['infrastructure_ids'].append(infra.id)
        
        # Infer language/framework from API handlers
        for service_name, service_data in services.items():
            service_apis = [api for api in apis if api.service_name == service_name]
            if service_apis:
                handler_files = [api.handler_file for api in service_apis if api.handler_file]
                if handler_files:
                    # Infer language from file extensions
                    exts = [Path(f).suffix for f in handler_files]
                    if '.py' in exts:
                        service_data['language'] = 'Python'
                    elif '.js' in exts or '.ts' in exts:
                        service_data['language'] = 'JavaScript' if '.js' in exts else 'TypeScript'
                    elif '.java' in exts:
                        service_data['language'] = 'Java'
                    elif '.go' in exts:
                        service_data['language'] = 'Go'
                    
                    # Infer directory
                    if handler_files:
                        common_path = Path(handler_files[0]).parent
                        service_data['source_directory'] = str(common_path)
        
        return [ServiceDefinition(**service_data) for service_data in services.values()]
    
    def correlate_apis_and_infrastructure(self, apis: List[APIDefinition], 
                                         infrastructure: List[InfrastructureComponent]) -> tuple:
        """Correlate APIs with infrastructure components."""
        
        # Update API infrastructure refs
        for api in apis:
            # Match by service name
            matching_infra = [
                infra for infra in infrastructure
                if infra.service_name == api.service_name
            ]
            
            if matching_infra:
                api.infrastructure_refs = [infra.id for infra in matching_infra]
        
        # Update infrastructure service ARNs based on APIs
        for infra in infrastructure:
            if infra.service_name:
                matching_apis = [
                    api for api in apis
                    if api.service_name == infra.service_name
                ]
                if matching_apis and not infra.service_arns:
                    # Create synthetic service references
                    infra.service_arns = [api.id for api in matching_apis]
        
        return apis, infrastructure
    
    def generate_stats(self, apis: List[APIDefinition], 
                      infrastructure: List[InfrastructureComponent],
                      services: List[ServiceDefinition]) -> dict:
        """Generate statistics about the extraction."""
        from collections import Counter
        
        # API stats
        methods = Counter([api.method.value for api in apis])
        services_count = len(set([api.service_name for api in apis if api.service_name]))
        
        # Infrastructure stats
        infra_types = Counter([infra.type for infra in infrastructure])
        
        return {
            'total_apis': len(apis),
            'total_infrastructure': len(infrastructure),
            'total_services': len(services),
            'api_methods': dict(methods),
            'services_count': services_count,
            'infrastructure_types': dict(infra_types),
            'extraction_timestamp': datetime.utcnow().isoformat()
        }
    
    def unify(self, apis: List[APIDefinition],
              infrastructure: List[InfrastructureComponent],
              source_directories: Optional[List[str]] = None,
              terraform_directories: Optional[List[str]] = None,
              environment: Optional[str] = None) -> UnifiedOutput:
        """
        Unify all sources into a single output.
        
        Args:
            apis: Extracted API definitions
            infrastructure: Extracted infrastructure components
            source_directories: Source code directories scanned
            terraform_directories: Terraform directories scanned
            environment: Environment name (dev, test, prod)
            
        Returns:
            Unified output with all data
        """
        # Infer services
        services = self.infer_services(apis, infrastructure)
        
        # Correlate APIs and infrastructure
        apis, infrastructure = self.correlate_apis_and_infrastructure(apis, infrastructure)
        
        # Generate statistics
        stats = self.generate_stats(apis, infrastructure, services)
        
        # Create unified output
        output = UnifiedOutput(
            apis=apis,
            infrastructure=infrastructure,
            services=services,
            extracted_at=datetime.utcnow(),
            environment=environment,
            source_directories=source_directories or [],
            terraform_directories=terraform_directories or [],
            stats=stats
        )
        
        logger.info(f"Generated unified output: {len(apis)} APIs, {len(infrastructure)} infrastructure, {len(services)} services")
        return output
