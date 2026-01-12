"""
Normalized JSON schema for API extraction connector.

This schema is environment-independent and supports:
- Static API extraction (LLM-based)
- Terraform infrastructure metadata
- Future log enrichment
- Cross-references and relationships
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class HTTPMethod(str, Enum):
    """HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


class ParameterLocation(str, Enum):
    """Where parameters are defined."""
    QUERY = "query"
    PATH = "path"
    HEADER = "header"
    BODY = "body"
    COOKIE = "cookie"


class APIParameter(BaseModel):
    """API parameter definition."""
    name: str
    type: str  # string, integer, float, boolean, object, array
    location: ParameterLocation
    required: bool = False
    description: Optional[str] = None
    default_value: Optional[Any] = None
    schema_ref: Optional[str] = None  # Reference to schema definition


class APIResponse(BaseModel):
    """API response definition."""
    status_code: int
    content_type: Optional[str] = None
    description: Optional[str] = None
    schema_ref: Optional[str] = None


class APIDefinition(BaseModel):
    """Extracted API endpoint definition."""
    # Core identification
    id: str = Field(..., description="Unique identifier for this API")
    method: HTTPMethod
    path: str = Field(..., description="Endpoint path (e.g., /api/v1/users/{id})")
    
    # Handler information
    handler_name: Optional[str] = Field(None, description="Function/class name handling this endpoint")
    handler_file: Optional[str] = Field(None, description="Source file path")
    handler_line: Optional[int] = Field(None, description="Line number in source file")
    handler_module: Optional[str] = Field(None, description="Module/package name")
    
    # Service context
    service_name: Optional[str] = Field(None, description="Service/component name")
    service_type: Optional[str] = Field(None, description="Service type (api, worker, batch, etc.)")
    
    # API details
    summary: Optional[str] = Field(None, description="Brief description")
    description: Optional[str] = Field(None, description="Detailed description")
    tags: List[str] = Field(default_factory=list, description="API tags/categories")
    deprecated: bool = False
    
    # Request/Response
    parameters: List[APIParameter] = Field(default_factory=list)
    request_body_schema: Optional[Dict[str, Any]] = None
    responses: List[APIResponse] = Field(default_factory=list)
    
    # Authentication & Authorization
    auth_required: bool = False
    auth_type: Optional[str] = None  # bearer, api_key, oauth2, etc.
    scopes: List[str] = Field(default_factory=list)
    
    # Metadata
    extracted_at: datetime = Field(default_factory=datetime.utcnow)
    source: str = Field(..., description="Source of extraction (llm, static_analysis, logs)")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Confidence score (0-1)")
    
    # Relationships
    related_apis: List[str] = Field(default_factory=list, description="IDs of related APIs")
    infrastructure_refs: List[str] = Field(default_factory=list, description="Infrastructure component IDs")


class InfrastructureComponent(BaseModel):
    """Infrastructure component from Terraform."""
    # Core identification
    id: str = Field(..., description="Unique identifier")
    type: str = Field(..., description="Resource type (aws_lb, aws_api_gateway, etc.)")
    provider: str = Field(..., description="Cloud provider (aws, gcp, azure)")
    
    # Resource details
    resource_name: str = Field(..., description="Terraform resource name")
    resource_address: str = Field(..., description="Full Terraform resource address")
    
    # Attributes
    attributes: Dict[str, Any] = Field(default_factory=dict, description="Resource attributes")
    
    # API Gateway / Load Balancer specific
    routes: List[Dict[str, Any]] = Field(default_factory=list, description="Routes/endpoints configured")
    target_group: Optional[str] = None
    listener_port: Optional[int] = None
    listener_protocol: Optional[str] = None
    
    # Service mapping
    service_name: Optional[str] = None
    service_arns: List[str] = Field(default_factory=list, description="Associated service ARNs")
    
    # Network
    vpc_id: Optional[str] = None
    subnet_ids: List[str] = Field(default_factory=list)
    security_group_ids: List[str] = Field(default_factory=list)
    
    # Metadata
    extracted_at: datetime = Field(default_factory=datetime.utcnow)
    environment: Optional[str] = None
    region: Optional[str] = None


class LogEnrichment(BaseModel):
    """Future: Runtime log data for API enrichment."""
    api_id: str
    timestamp: datetime
    endpoint: str
    method: str
    status_code: int
    response_time_ms: float
    request_size_bytes: int
    response_size_bytes: int
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    trace_id: Optional[str] = None
    additional_fields: Dict[str, Any] = Field(default_factory=dict)


class ServiceDefinition(BaseModel):
    """Service/component definition."""
    name: str
    type: str  # api, worker, batch, etc.
    language: Optional[str] = None
    framework: Optional[str] = None
    source_directory: Optional[str] = None
    docker_image: Optional[str] = None
    
    # Relationships
    api_ids: List[str] = Field(default_factory=list)
    infrastructure_ids: List[str] = Field(default_factory=list)


class UnifiedOutput(BaseModel):
    """Unified output combining all sources."""
    # Core data
    apis: List[APIDefinition] = Field(default_factory=list)
    infrastructure: List[InfrastructureComponent] = Field(default_factory=list)
    services: List[ServiceDefinition] = Field(default_factory=list)
    
    # Future: Log enrichment
    log_enrichments: List[LogEnrichment] = Field(default_factory=list)
    
    # Metadata
    extracted_at: datetime = Field(default_factory=datetime.utcnow)
    environment: Optional[str] = None
    source_directories: List[str] = Field(default_factory=list)
    terraform_directories: List[str] = Field(default_factory=list)
    
    # Statistics
    stats: Dict[str, Any] = Field(default_factory=dict, description="Extraction statistics")
    
    # Version
    schema_version: str = "1.0.0"
