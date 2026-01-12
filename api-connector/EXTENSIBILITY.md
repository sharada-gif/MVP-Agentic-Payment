# Extensibility Guide

This document describes how to extend the API connector for future log ingestion and other enhancements.

## Architecture Overview

The connector is designed with clear separation of concerns:

```
┌─────────────────────────────────────────────────┐
│           Extensibility Points                   │
└─────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────┐    ┌──────────┐    ┌──────────┐
│   Log    │    │  Schema  │    │  Output  │
│ Ingestor │    │ Extension│    │ Formatter│
└──────────┘    └──────────┘    └──────────┘
```

## 1. Log Ingestion Extensibility

### Current Schema Support

The `UnifiedOutput` schema already includes `log_enrichments: List[LogEnrichment]` field, which is currently empty but ready for future use.

### Adding Log Ingestion

#### Step 1: Create Log Parser

Create `api-connector/log_parser.py`:

```python
from typing import List
from schema import LogEnrichment, UnifiedOutput
import json

class LogParser:
    """Parse logs from various sources."""
    
    def parse_cloudwatch_logs(self, log_stream: str) -> List[LogEnrichment]:
        """Parse AWS CloudWatch logs."""
        enrichments = []
        # Parse logs, extract API calls
        # Match to existing APIs by endpoint/method
        return enrichments
    
    def parse_api_gateway_logs(self, logs: List[dict]) -> List[LogEnrichment]:
        """Parse API Gateway access logs."""
        enrichments = []
        # Extract: endpoint, method, status_code, response_time
        return enrichments
    
    def enrich_apis(self, apis: List[APIDefinition], 
                   enrichments: List[LogEnrichment]) -> List[APIDefinition]:
        """Enrich API definitions with runtime data."""
        # Match enrichments to APIs
        # Add runtime metrics to API definitions
        return apis
```

#### Step 2: Update Unifier

Modify `unifier.py` to accept log enrichments:

```python
def unify(self, apis, infrastructure, log_enrichments=None, ...):
    # Match log enrichments to APIs
    if log_enrichments:
        apis = self.enrich_with_logs(apis, log_enrichments)
    
    # Update output
    output = UnifiedOutput(
        ...
        log_enrichments=log_enrichments or []
    )
```

#### Step 3: Extend CLI

Add log parsing command:

```python
log_parser = subparsers.add_parser('logs', help='Parse logs')
log_parser.add_argument('--logs-dir', help='Directory with log files')
log_parser.add_argument('--output', help='Output JSON file')
```

### Log Sources to Support

1. **AWS CloudWatch Logs**
   - Parse JSON log streams
   - Extract API Gateway access logs
   - Extract application logs (structured JSON)

2. **API Gateway Access Logs**
   - Parse standard access log format
   - Extract: endpoint, method, status, latency

3. **Application Logs**
   - Parse structured JSON logs
   - Extract trace IDs, request IDs
   - Match to API definitions

4. **Load Balancer Logs**
   - Parse ALB/ELB access logs
   - Extract upstream service mappings

## 2. Schema Extensions

### Adding New Fields

All schemas use Pydantic models, making them easy to extend:

```python
# In schema.py
class APIDefinition(BaseModel):
    # ... existing fields ...
    
    # New field (optional for backward compatibility)
    rate_limit: Optional[int] = None
    cache_ttl: Optional[int] = None
```

### Adding New Data Sources

Create new schema classes:

```python
class KubernetesResource(BaseModel):
    """Kubernetes resource definition."""
    kind: str
    name: str
    namespace: str
    # ... other fields

class UnifiedOutput(BaseModel):
    # ... existing fields ...
    kubernetes_resources: List[KubernetesResource] = Field(default_factory=list)
```

## 3. Output Format Extensions

### Custom Formatters

Create new formatter classes:

```python
class OpenAPIGenerator:
    """Generate OpenAPI 3.0 spec from unified output."""
    
    def generate(self, output: UnifiedOutput) -> dict:
        # Convert unified output to OpenAPI format
        pass

class GraphQLSchemaGenerator:
    """Generate GraphQL schema from unified output."""
    
    def generate(self, output: UnifiedOutput) -> str:
        # Convert to GraphQL SDL
        pass
```

## 4. Visualization Extensions

### Adding New Views

Extend `visualizer.py`:

```python
def generate_network_graph(output: UnifiedOutput, output_path: str):
    """Generate network graph visualization."""
    # Use D3.js or similar for interactive graph
    # Show relationships between APIs, services, infrastructure
    pass

def generate_timeline(output: UnifiedOutput, output_path: str):
    """Generate timeline of API changes."""
    # Show API evolution over time (if log data available)
    pass
```

## 5. LLM Prompt Extensions

### Custom Extraction Rules

Extend `prompts.py` for domain-specific extraction:

```python
DOMAIN_SPECIFIC_PROMPT = """
Extract APIs with additional domain-specific metadata:
- Business domain classification
- Data sensitivity levels
- Compliance requirements
...
"""
```

## 6. Terraform Parser Extensions

### Additional Providers

Support other Terraform providers:

```python
# In terraform_parser.py
def extract_azure_resource(self, resource_type, resource_config):
    """Extract Azure resource."""
    pass

def extract_gcp_resource(self, resource_type, resource_config):
    """Extract GCP resource."""
    pass
```

## Best Practices

1. **Backward Compatibility**: Always make new fields optional
2. **Schema Versioning**: Update `schema_version` when making breaking changes
3. **Testing**: Add tests for new extensions
4. **Documentation**: Update README and examples
5. **Incremental Loading**: Support partial updates when adding logs

## Example: Complete Log Integration

```python
# 1. Parse logs
log_parser = LogParser()
enrichments = log_parser.parse_cloudwatch_logs('logs/cloudwatch.json')

# 2. Unify with existing data
unifier = Unifier()
output = unifier.unify(
    apis=apis,
    infrastructure=infrastructure,
    log_enrichments=enrichments
)

# 3. Generate enriched visualization
visualizer.generate_html(output, 'dashboard.html')
```

## Future Enhancements

- **Real-time Log Streaming**: WebSocket-based log ingestion
- **Historical Analysis**: Track API changes over time
- **Performance Metrics**: Aggregate response times, error rates
- **Security Analysis**: Detect security issues from logs
- **Dependency Graph**: Build complete dependency map
- **Multi-Environment Comparison**: Compare APIs across environments
