"""
CLI entry point for API connector.
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from extractor import LLMAPIExtractor
from terraform_parser import TerraformParser
from unifier import Unifier
from visualizer import generate_html
from schema import UnifiedOutput

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def extract_apis(source_dir: str, output_path: str, model: str = "gpt-4o-mini"):
    """Extract APIs from source code."""
    logger.info(f"Extracting APIs from {source_dir}")
    
    extractor = LLMAPIExtractor(model=model)
    apis = extractor.extract_from_directory(source_dir)
    
    # Save to file
    apis_json = [api.model_dump() for api in apis]
    with open(output_path, 'w') as f:
        json.dump(apis_json, f, indent=2, default=str)
    
    logger.info(f"Extracted {len(apis)} APIs, saved to {output_path}")
    return apis


def parse_terraform(terraform_dir: str, output_path: str):
    """Parse Terraform configurations."""
    logger.info(f"Parsing Terraform from {terraform_dir}")
    
    parser = TerraformParser()
    infrastructure = parser.parse_directory(terraform_dir)
    
    # Save to file
    infra_json = [comp.model_dump() for comp in infrastructure]
    with open(output_path, 'w') as f:
        json.dump(infra_json, f, indent=2, default=str)
    
    logger.info(f"Extracted {len(infrastructure)} infrastructure components, saved to {output_path}")
    return infrastructure


def unify_and_visualize(apis_path: str, terraform_path: str, 
                       output_path: str, html_path: str,
                       environment: str = None):
    """Unify all sources and generate visualization."""
    logger.info("Unifying outputs and generating visualization")
    
    # Load data
    with open(apis_path, 'r') as f:
        apis_data = json.load(f)
    
    with open(terraform_path, 'r') as f:
        infra_data = json.load(f)
    
    # Convert to model objects
    from schema import APIDefinition, InfrastructureComponent
    
    apis = [APIDefinition(**api) for api in apis_data]
    infrastructure = [InfrastructureComponent(**infra) for infra in infra_data]
    
    # Unify
    unifier = Unifier()
    unified = unifier.unify(
        apis=apis,
        infrastructure=infrastructure,
        source_directories=[Path(apis_path).parent.as_posix()],
        terraform_directories=[Path(terraform_path).parent.as_posix()],
        environment=environment
    )
    
    # Save unified output
    with open(output_path, 'w') as f:
        f.write(unified.model_dump_json(indent=2))
    
    logger.info(f"Unified output saved to {output_path}")
    
    # Generate HTML
    generate_html(unified, html_path)
    
    return unified


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Generic API Extraction Connector',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract APIs from source code
  python -m api_connector extract --source-dir ./apps --output apis.json
  
  # Parse Terraform configurations
  python -m api_connector terraform --terraform-dir ./terraform --output infra.json
  
  # Unify and visualize
  python -m api_connector unify --apis apis.json --terraform infra.json --output unified.json --html dashboard.html
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract APIs from source code')
    extract_parser.add_argument('--source-dir', required=True, help='Source code directory')
    extract_parser.add_argument('--output', required=True, help='Output JSON file')
    extract_parser.add_argument('--model', default='gpt-4o-mini', help='LLM model to use')
    
    # Terraform command
    terraform_parser = subparsers.add_parser('terraform', help='Parse Terraform configurations')
    terraform_parser.add_argument('--terraform-dir', required=True, help='Terraform directory')
    terraform_parser.add_argument('--output', required=True, help='Output JSON file')
    
    # Unify command
    unify_parser = subparsers.add_parser('unify', help='Unify outputs and generate visualization')
    unify_parser.add_argument('--apis', required=True, help='APIs JSON file')
    unify_parser.add_argument('--terraform', required=True, help='Terraform JSON file')
    unify_parser.add_argument('--output', required=True, help='Unified output JSON file')
    unify_parser.add_argument('--html', required=True, help='HTML visualization output file')
    unify_parser.add_argument('--environment', help='Environment name (dev, test, prod)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'extract':
            extract_apis(args.source_dir, args.output, args.model)
        
        elif args.command == 'terraform':
            parse_terraform(args.terraform_dir, args.output)
        
        elif args.command == 'unify':
            unify_and_visualize(
                args.apis,
                args.terraform,
                args.output,
                args.html,
                args.environment
            )
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
