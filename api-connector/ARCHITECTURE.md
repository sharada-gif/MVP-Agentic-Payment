# API Connector Architecture

## Overview

The Generic API Extraction Connector is a framework-agnostic, LLM-powered system for extracting APIs from arbitrary codebases and correlating them with infrastructure definitions.

## Core Principles

1. **Framework Agnostic**: No hard-coded patterns or framework-specific logic
2. **LLM-Powered**: Uses LLM reasoning to infer APIs instead of pattern matching
3. **Cloud Agnostic**: Works across AWS, GCP, Azure, and on-premises
4. **Environment Independent**: Consistent outputs across dev, test, prod
5. **Extensible**: Clear extension points for future enhancements

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    API Connector Pipeline                     │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   LLM API    │    │  Terraform   │    │ Future Log   │
│  Extractor   │    │   Parser     │    │  Ingestor    │
│              │    │              │    │              │
│ • Language   │    │ • HCL/JSON   │    │ • CloudWatch │
│   Detection  │    │   Parser     │    │ • API Gateway│
│ • Framework  │    │ • Resource   │    │ • App Logs   │
│   Inference  │    │   Extraction │    │ • Enrichment │
│ • LLM        │    │ • Metadata   │    │ • Metrics    │
│   Prompting  │    │   Extraction │    │ • Correlation│
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
                    ┌──────────────┐
                    │   Normalized │
                    │     Schema   │
                    │              │
                    │ • APIDefinition│
                    │ • Infrastructure│
                    │ • Service    │
                    │ • LogEnrichment│
                    └──────────────┘
                              │
                              ▼
                    ┌──────────────┐
                    │   Unifier    │
                    │              │
                    │ • Correlation│
                    │ • Service    │
                    │   Inference  │
                    │ • Relationship│
                    │   Mapping    │
                    └──────────────┘
                              │
                              ▼
                    ┌──────────────┐
                    │   Unified    │
                    │    Output    │
                    │              │
                    │ • All APIs   │
                    │ • All Infra  │
                    │ • Services   │
                    │ • Metadata   │
                    └──────────────┘
                              │
                              ▼
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│     JSON     │    │     HTML     │    │   Future:    │
│   Output     │    │ Visualization│    │   OpenAPI    │
│              │    │              │    │   GraphQL    │
│ • Normalized │    │ • Dashboard  │    │   Other      │
│ • Structured │    │ • Search     │    │   Formats    │
│ • Queryable  │    │ • Filter     │    │              │
│              │    │ • Interactive│    │              │
└──────────────┘    └──────────────┘    └──────────────┘
```

## Component Details

### 1. LLM API Extractor (`extractor.py`)

**Purpose**: Extract API definitions from arbitrary source code using LLM reasoning.

**Key Features**:
- Language detection (Python, Node.js, Java, Go, Ruby, PHP, etc.)
- Framework inference (FastAPI, Flask, Express, Spring Boot, etc.)
- LLM-based extraction (no hard-coded patterns)
- Batch processing for large codebases

**Process**:
1. Scan directory for source files
2. Detect language from file extension
3. Detect framework from imports/patterns
4. For each file:
   - Send code to LLM with extraction prompt
   - Parse JSON response
   - Normalize to APIDefinition schema
5. Enrich with service context
6. Deduplicate and correlate

**LLM Prompt Design**:
- System prompt: Expert API extraction assistant
- User prompt: File path, language, framework, source code
- Response format: JSON array of API definitions
- Temperature: 0.1 (low for consistency)

### 2. Terraform Parser (`terraform_parser.py`)

**Purpose**: Extract infrastructure metadata from Terraform configurations.

**Key Features**:
- HCL2 and JSON parsing
- Resource type detection
- Metadata extraction (routes, services, network)
- Provider agnostic (AWS, GCP, Azure)

**Process**:
1. Scan directory for `.tf` and `.tf.json` files
2. Parse HCL/JSON using python-hcl2
3. Extract resources:
   - API Gateways
   - Load Balancers
   - Services (ECS, Lambda, etc.)
   - Network (VPC, subnets, security groups)
4. Normalize to InfrastructureComponent schema

**Supported Resources**:
- `aws_api_gateway_*` - API Gateway routes
- `aws_lb`, `aws_alb` - Load balancers and listeners
- `aws_ecs_service` - ECS services
- `aws_lambda_function` - Lambda functions
- Network resources (VPC, subnets, security groups)
- Any other resource (generic extraction)

### 3. Schema Normalization (`schema.py`)

**Purpose**: Define normalized, environment-independent data structures.

**Key Schemas**:
- `APIDefinition`: Complete API endpoint definition
- `InfrastructureComponent`: Infrastructure resource metadata
- `ServiceDefinition`: Service/component definition
- `LogEnrichment`: Runtime log data (future)
- `UnifiedOutput`: Combined output from all sources

**Design Principles**:
- Environment-independent fields
- Cloud provider agnostic
- Extensible (optional fields, versioning)
- Supports future log enrichment

### 4. Unifier (`unifier.py`)

**Purpose**: Combine and correlate all extraction sources.

**Key Features**:
- Service inference from APIs and infrastructure
- API-infrastructure correlation
- Relationship mapping
- Statistics generation

**Process**:
1. Group APIs by service
2. Map infrastructure to services
3. Correlate APIs with infrastructure
4. Infer service definitions
5. Generate statistics
6. Create unified output

### 5. Visualizer (`visualizer.py`)

**Purpose**: Generate interactive HTML dashboard.

**Key Features**:
- Tabbed interface (APIs, Services, Infrastructure)
- Search and filter
- Card-based layout
- Color-coded by type
- Statistics display

**Visualization Sections**:
- **APIs Tab**: All extracted endpoints with details
- **Services Tab**: Service definitions and relationships
- **Infrastructure Tab**: Infrastructure components

### 6. CLI Interface (`__main__.py`)

**Purpose**: Command-line interface for all operations.

**Commands**:
- `extract`: Extract APIs from source code
- `terraform`: Parse Terraform configurations
- `unify`: Unify outputs and generate visualization

## Data Flow

### Extraction Flow

```
Source Code → LLM Extractor → Raw APIs → Normalization → APIDefinition[]
Terraform → HCL Parser → Raw Resources → Normalization → InfrastructureComponent[]
```

### Unification Flow

```
APIDefinition[] + InfrastructureComponent[] → Unifier → Service Inference → Correlation → UnifiedOutput
```

### Output Flow

```
UnifiedOutput → JSON Writer → unified.json
UnifiedOutput → HTML Generator → dashboard.html
```

## LLM Prompt Design

### Extraction Prompt Structure

1. **System Prompt**: Defines role and capabilities
   - Expert API extraction assistant
   - Framework agnostic
   - Thorough extraction requirements

2. **User Prompt Template**:
   - File path and language
   - Framework (if detected)
   - Source code content
   - Extraction requirements

3. **Response Format**: JSON array of API definitions

4. **Error Handling**:
   - JSON parsing fallbacks
   - Markdown code block extraction
   - Validation and normalization

### Prompt Engineering Considerations

- **Temperature**: Low (0.1) for consistency
- **Context Window**: Handle large files (truncation)
- **Response Format**: JSON structure defined in prompt
- **Error Recovery**: Multiple parsing strategies

## Terraform Ingestion Design

### Parsing Strategy

1. **HCL Files** (`.tf`):
   - Use `python-hcl2` library
   - Parse resource blocks
   - Extract attributes

2. **JSON Files** (`.tf.json`):
   - Direct JSON parsing
   - Same extraction logic

3. **Resource Extraction**:
   - Generic: Extract all resource types
   - Specific: Special handling for API Gateway, ALB
   - Metadata: Tags, environment, region

### Normalization Strategy

- Convert provider-specific formats to generic schema
- Extract common attributes (service name, network, etc.)
- Preserve provider-specific attributes in `attributes` field
- Generate unique IDs for correlation

## Extensibility Points

### 1. Log Ingestion (Future)

**Location**: `schema.py` - `LogEnrichment` already defined

**Extension**:
- Create `log_parser.py`
- Implement parsers for different log sources
- Add to unifier pipeline
- Update CLI with `logs` command

### 2. Additional Output Formats

**Location**: `visualizer.py` or new formatters

**Extension**:
- OpenAPI 3.0 generator
- GraphQL schema generator
- Markdown documentation generator

### 3. Additional Infrastructure Sources

**Location**: `terraform_parser.py` or new parsers

**Extension**:
- Kubernetes manifest parser
- Docker Compose parser
- CloudFormation parser
- Serverless Framework parser

### 4. Enhanced Correlation

**Location**: `unifier.py`

**Extension**:
- ML-based service matching
- Dependency graph construction
- Security analysis
- Performance metrics aggregation

## Error Handling

### LLM Errors
- JSON parsing failures → Fallback parsing
- Context window limits → Truncation
- API errors → Retry with exponential backoff

### Terraform Parsing Errors
- HCL syntax errors → Skip file, log warning
- Missing attributes → Use defaults
- Invalid JSON → Skip file, log warning

### File I/O Errors
- Missing files → Clear error messages
- Permission errors → Helpful guidance
- Encoding issues → UTF-8 with fallback

## Performance Considerations

### LLM API Calls
- Batch similar files when possible
- Cache responses for identical files
- Rate limiting for API calls
- Parallel processing (future)

### Terraform Parsing
- Efficient HCL parsing
- Skip `.terraform` and `.git` directories
- Process large files incrementally

### Memory Management
- Stream large outputs when possible
- Clear intermediate results
- Efficient data structures

## Security Considerations

### API Keys
- Read from environment variables
- Never log or expose keys
- Support credential providers

### Source Code
- No code transmission beyond LLM API
- Local processing where possible
- Respect `.gitignore` patterns

### Output Data
- Sanitize sensitive data
- Optional redaction features
- Access control for outputs

## Future Enhancements

1. **Real-time Log Streaming**: WebSocket-based ingestion
2. **Historical Analysis**: Track API changes over time
3. **Multi-Environment Comparison**: Compare across environments
4. **Dependency Graph**: Visual dependency mapping
5. **Security Analysis**: Detect security issues
6. **Performance Metrics**: Aggregate from logs
7. **OpenAPI Export**: Generate OpenAPI specs
8. **CI/CD Integration**: Automated extraction in pipelines
