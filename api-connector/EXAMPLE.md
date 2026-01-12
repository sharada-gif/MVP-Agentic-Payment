# Example Usage

This guide demonstrates how to use the API Connector to extract APIs from your codebase.

## Prerequisites

1. Install dependencies:
```bash
cd api-connector
pip install -r requirements.txt
```

2. Set OpenAI API key:
```bash
export OPENAI_API_KEY=sk-your-key-here
```

## Example 1: Extract APIs from Source Code

Extract APIs from the `apps` directory:

```bash
python -m api_connector extract \
    --source-dir ../apps \
    --output apis.json \
    --model gpt-4o-mini
```

**Output**: `apis.json` with extracted API definitions.

**Example Output**:
```json
[
  {
    "id": "abc123def456",
    "method": "POST",
    "path": "/charge",
    "handler_name": "create_charge",
    "handler_file": "apps/payment-api/main.py",
    "handler_line": 66,
    "service_name": "payment-api",
    "summary": "Create a new charge",
    "parameters": [
      {
        "name": "amount",
        "type": "float",
        "location": "body",
        "required": true
      }
    ],
    "responses": [
      {
        "status_code": 200,
        "description": "Charge created successfully"
      }
    ]
  }
]
```

## Example 2: Parse Terraform Configurations

Parse Terraform files to extract infrastructure metadata:

```bash
python -m api_connector terraform \
    --terraform-dir ../terraform \
    --output infrastructure.json
```

**Output**: `infrastructure.json` with infrastructure components.

**Example Output**:
```json
[
  {
    "id": "xyz789abc123",
    "type": "aws_lb",
    "provider": "aws",
    "resource_name": "main",
    "resource_address": "module.alb.aws_lb.main",
    "service_name": "payment-api",
    "listener_port": 443,
    "listener_protocol": "HTTPS",
    "environment": "production",
    "region": "us-east-1"
  }
]
```

## Example 3: Unify and Visualize

Combine API extraction and Terraform analysis into a unified output with visualization:

```bash
python -m api_connector unify \
    --apis apis.json \
    --terraform infrastructure.json \
    --output unified.json \
    --html dashboard.html \
    --environment production
```

**Outputs**:
- `unified.json`: Complete unified output
- `dashboard.html`: Interactive HTML dashboard

## Example 4: Complete Workflow

Run all steps in sequence:

```bash
# Step 1: Extract APIs
python -m api_connector extract \
    --source-dir ../apps \
    --output apis.json

# Step 2: Parse Terraform
python -m api_connector terraform \
    --terraform-dir ../terraform \
    --output infrastructure.json

# Step 3: Unify and visualize
python -m api_connector unify \
    --apis apis.json \
    --terraform infrastructure.json \
    --output unified.json \
    --html dashboard.html \
    --environment production

# Step 4: Open dashboard
open dashboard.html
```

## Example 5: Using with the Current Project

Extract APIs from the payment project:

```bash
# From project root
cd api-connector

# Extract APIs from apps directory
python -m api_connector extract \
    --source-dir ../apps/payment-api \
    --output payment-apis.json

# Parse Terraform
python -m api_connector terraform \
    --terraform-dir ../terraform \
    --output payment-infra.json

# Generate unified output
python -m api_connector unify \
    --apis payment-apis.json \
    --terraform payment-infra.json \
    --output payment-unified.json \
    --html payment-dashboard.html \
    --environment development

# View dashboard
open payment-dashboard.html
```

## Expected Results

### APIs Extracted

From `apps/payment-api/main.py`, you should see:
- `GET /health` - Health check endpoint
- `POST /charge` - Create charge endpoint
- `POST /refund` - Create refund endpoint
- `POST /webhooks/stripe` - Stripe webhook endpoint

### Infrastructure Extracted

From `terraform/`, you should see:
- VPC resources
- ALB (Application Load Balancer)
- ECS services
- RDS database
- SQS queues
- S3 buckets
- Security groups

### Dashboard Features

The HTML dashboard will show:
- **APIs Tab**: All extracted endpoints with method, path, description
- **Services Tab**: Services (payment-api, payment-worker, agent-runner)
- **Infrastructure Tab**: Infrastructure components
- **Search**: Filter APIs, services, infrastructure
- **Statistics**: Total APIs, services, infrastructure count

## Troubleshooting

### LLM API Errors

If you get API errors:
- Check your `OPENAI_API_KEY` is set correctly
- Verify you have API credits/quota
- Try a different model: `--model gpt-3.5-turbo`

### Terraform Parsing Errors

If Terraform parsing fails:
- Install hcl2: `pip install python-hcl2`
- Check Terraform syntax is valid
- Some resources may not parse perfectly (expected)

### No APIs Extracted

If no APIs are found:
- Verify source directory path is correct
- Check file extensions are supported (.py, .js, .ts, etc.)
- Review LLM response in logs
- Try with a smaller file first

### Dashboard Not Loading

If HTML dashboard has issues:
- Open in a modern browser (Chrome, Firefox, Safari)
- Check browser console for errors
- Verify JSON files are valid

## Advanced Usage

### Custom Model

Use a different LLM model:

```bash
python -m api_connector extract \
    --source-dir ../apps \
    --output apis.json \
    --model gpt-4
```

### Large Codebases

For large codebases:
- Process subdirectories separately
- Merge JSON outputs manually
- Consider caching LLM responses

### Multiple Environments

Compare across environments:

```bash
# Development
python -m api_connector unify ... --environment development

# Production
python -m api_connector unify ... --environment production
```

## Next Steps

1. **Review Extracted APIs**: Check `unified.json` for accuracy
2. **Explore Dashboard**: Use HTML dashboard for visual exploration
3. **Enrich with Logs**: See `EXTENSIBILITY.md` for log integration
4. **Extend**: Add custom extractors or formatters
