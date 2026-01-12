# Generic API Extraction Connector

An LLM-based, framework-agnostic connector for extracting APIs from arbitrary codebases and correlating them with infrastructure definitions.

## Architecture

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
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
                    ┌──────────────┐
                    │   Unified    │
                    │  JSON Output │
                    └──────────────┘
                              │
                              ▼
                    ┌──────────────┐
                    │    HTML      │
                    │ Visualization│
                    └──────────────┘
```

## Components

1. **LLM API Extractor** - Framework-agnostic API extraction from source code
2. **Terraform Parser** - Infrastructure metadata extraction (HCL/JSON)
3. **Schema Normalizer** - Unified JSON schema across all sources
4. **Visualization Generator** - Interactive HTML dashboard
5. **Extensibility Layer** - Plugin architecture for future log ingestion

## Features

- ✅ Language/framework agnostic (Python, Node.js, Java, Go, etc.)
- ✅ Cloud provider agnostic (AWS, GCP, Azure)
- ✅ Environment independent (dev, test, prod)
- ✅ Extensible for runtime log enrichment
- ✅ Interactive visualization

## Usage

```bash
# Extract APIs from codebase
python -m api_connector extract --source-dir ./apps --output apis.json

# Parse Terraform configurations
python -m api_connector terraform --terraform-dir ./terraform --output infra.json

# Generate unified output and visualization
python -m api_connector unify \
    --apis apis.json \
    --terraform infra.json \
    --output unified.json \
    --html dashboard.html
```

## Schema

All outputs use a normalized JSON schema defined in `schema.py`, supporting:
- Static API definitions
- Infrastructure metadata
- Future log enrichment
- Cross-references and relationships
