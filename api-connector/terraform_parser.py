"""
Terraform configuration parser.

Extracts infrastructure metadata from Terraform HCL/JSON configurations,
including API gateways, load balancers, routes, and services.
"""

import os
import json
import logging
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    import hcl2
except ImportError:
    hcl2 = None

from schema import InfrastructureComponent

logger = logging.getLogger(__name__)


class TerraformParser:
    """Parse Terraform configurations to extract infrastructure metadata."""
    
    def __init__(self):
        """Initialize Terraform parser."""
        if hcl2 is None:
            logger.warning("hcl2 library not installed. HCL parsing may be limited. Install with: pip install python-hcl2")
    
    def parse_hcl_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a Terraform HCL file.
        
        Args:
            file_path: Path to .tf file
            
        Returns:
            Parsed Terraform configuration as dict
        """
        if hcl2 is None:
            # Fallback: try to parse as JSON or return minimal structure
            logger.warning(f"hcl2 not available, limited parsing for {file_path}")
            return {}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse HCL2
            parsed = hcl2.loads(content)
            return parsed
        except Exception as e:
            logger.error(f"Failed to parse HCL file {file_path}: {e}")
            return {}
    
    def parse_json_file(self, file_path: str) -> Dict[str, Any]:
        """Parse a Terraform JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to parse JSON file {file_path}: {e}")
            return {}
    
    def extract_resource(self, resource_type: str, resource_name: str, resource_config: Dict[str, Any], 
                        resource_address: str, provider: str = "aws") -> Optional[InfrastructureComponent]:
        """Extract infrastructure component from Terraform resource."""
        
        # Generate ID
        resource_id = hashlib.md5(resource_address.encode()).hexdigest()[:12]
        
        # Extract attributes
        attrs = resource_config.get(resource_name, {})
        if isinstance(attrs, dict):
            attributes = attrs.copy()
        else:
            attributes = {"value": attrs}
        
        # Extract environment from tags or variables
        environment = None
        if isinstance(attributes, dict):
            tags = attributes.get('tags', {})
            if isinstance(tags, dict):
                environment = tags.get('Environment', tags.get('environment'))
        
        # Extract region
        region = None
        if isinstance(attributes, dict):
            region = attributes.get('region', attributes.get('location'))
        
        # Route extraction (for ALB, API Gateway, etc.)
        routes = []
        target_group = None
        listener_port = None
        listener_protocol = None
        
        # API Gateway specific
        if 'aws_api_gateway' in resource_type:
            routes = self._extract_api_gateway_routes(resource_config, resource_name)
        
        # Load Balancer specific
        elif 'aws_lb' in resource_type or 'aws_alb' in resource_type:
            target_group = attributes.get('target_group')
            listeners = attributes.get('listener', [])
            if listeners and isinstance(listeners, list) and len(listeners) > 0:
                listener = listeners[0] if isinstance(listeners[0], dict) else {}
                listener_port = listener.get('port')
                listener_protocol = listener.get('protocol')
        
        # Service extraction
        service_name = None
        service_arns = []
        if isinstance(attributes, dict):
            service_name = attributes.get('name', attributes.get('service_name'))
            if 'arn' in attributes:
                service_arns.append(attributes['arn'])
            if 'service_arns' in attributes:
                service_arns.extend(attributes['service_arns'])
        
        # Network extraction
        vpc_id = None
        subnet_ids = []
        security_group_ids = []
        if isinstance(attributes, dict):
            vpc_id = attributes.get('vpc_id')
            if 'subnet_ids' in attributes:
                subnet_ids = attributes['subnet_ids'] if isinstance(attributes['subnet_ids'], list) else [attributes['subnet_ids']]
            elif 'subnet_id' in attributes:
                subnet_ids = [attributes['subnet_id']]
            if 'security_group_ids' in attributes:
                security_group_ids = attributes['security_group_ids'] if isinstance(attributes['security_group_ids'], list) else [attributes['security_group_ids']]
            elif 'security_group_id' in attributes:
                security_group_ids = [attributes['security_group_id']]
        
        return InfrastructureComponent(
            id=resource_id,
            type=resource_type,
            provider=provider,
            resource_name=resource_name,
            resource_address=resource_address,
            attributes=attributes,
            routes=routes,
            target_group=target_group,
            listener_port=listener_port,
            listener_protocol=listener_protocol,
            service_name=service_name,
            service_arns=service_arns,
            vpc_id=vpc_id,
            subnet_ids=subnet_ids,
            security_group_ids=security_group_ids,
            extracted_at=datetime.utcnow(),
            environment=environment,
            region=region
        )
    
    def _extract_api_gateway_routes(self, resource_config: Dict[str, Any], resource_name: str) -> List[Dict[str, Any]]:
        """Extract routes from API Gateway configuration."""
        routes = []
        
        # Look for aws_api_gateway_resource and aws_api_gateway_method
        # This is simplified - real implementation would walk the resource tree
        if 'resource' in resource_config:
            for name, config in resource_config['resource'].items():
                if 'aws_api_gateway_resource' in name or 'aws_api_gateway_method' in name:
                    routes.append({
                        'resource': name,
                        'config': config
                    })
        
        return routes
    
    def parse_directory(self, terraform_dir: str) -> List[InfrastructureComponent]:
        """
        Parse all Terraform files in a directory.
        
        Args:
            terraform_dir: Directory containing Terraform files
            
        Returns:
            List of extracted infrastructure components
        """
        terraform_path = Path(terraform_dir)
        if not terraform_path.exists():
            raise ValueError(f"Terraform directory does not exist: {terraform_dir}")
        
        components = []
        
        # Parse .tf files
        for tf_file in terraform_path.rglob('*.tf'):
            if '.terraform' in str(tf_file) or '.git' in str(tf_file):
                continue
            
            try:
                parsed = self.parse_hcl_file(str(tf_file))
                
                # Extract resources
                if 'resource' in parsed:
                    for resource_type, resources in parsed['resource'].items():
                        if isinstance(resources, dict):
                            for resource_name, resource_config in resources.items():
                                resource_address = f"{resource_type}.{resource_name}"
                                component = self.extract_resource(
                                    resource_type,
                                    resource_name,
                                    resource_config,
                                    resource_address
                                )
                                if component:
                                    components.append(component)
                
            except Exception as e:
                logger.warning(f"Failed to parse {tf_file}: {e}")
                continue
        
        # Parse .tf.json files
        for tf_json_file in terraform_path.rglob('*.tf.json'):
            if '.terraform' in str(tf_json_file) or '.git' in str(tf_json_file):
                continue
            
            try:
                parsed = self.parse_json_file(str(tf_json_file))
                
                # Extract resources (JSON format)
                if 'resource' in parsed:
                    for resource_type, resources in parsed['resource'].items():
                        if isinstance(resources, dict):
                            for resource_name, resource_config in resources.items():
                                resource_address = f"{resource_type}.{resource_name}"
                                component = self.extract_resource(
                                    resource_type,
                                    resource_name,
                                    resource_config,
                                    resource_address
                                )
                                if component:
                                    components.append(component)
                
            except Exception as e:
                logger.warning(f"Failed to parse {tf_json_file}: {e}")
                continue
        
        logger.info(f"Extracted {len(components)} infrastructure components from {terraform_dir}")
        return components
