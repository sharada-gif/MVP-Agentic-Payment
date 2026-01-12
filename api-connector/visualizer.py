"""
HTML visualization generator.

Creates an interactive dashboard showing:
- APIs with details
- Services/modules
- Infrastructure relationships
- Dependencies between APIs and components
"""

import json
from typing import List
from pathlib import Path
from schema import UnifiedOutput, APIDefinition, InfrastructureComponent, ServiceDefinition


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API Extraction Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }}
        
        .stats {{
            display: flex;
            gap: 2rem;
            margin-top: 1rem;
            flex-wrap: wrap;
        }}
        
        .stat-card {{
            background: rgba(255,255,255,0.2);
            padding: 1rem;
            border-radius: 8px;
            backdrop-filter: blur(10px);
        }}
        
        .stat-value {{
            font-size: 2rem;
            font-weight: bold;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 2rem auto;
            padding: 0 1rem;
        }}
        
        .tabs {{
            display: flex;
            gap: 0.5rem;
            margin-bottom: 2rem;
            border-bottom: 2px solid #ddd;
        }}
        
        .tab {{
            padding: 1rem 2rem;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 1rem;
            color: #666;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }}
        
        .tab:hover {{
            color: #667eea;
        }}
        
        .tab.active {{
            color: #667eea;
            border-bottom-color: #667eea;
            font-weight: 600;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 1.5rem;
        }}
        
        .card {{
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid #f0f0f0;
        }}
        
        .method-badge {{
            padding: 0.25rem 0.75rem;
            border-radius: 4px;
            font-weight: 600;
            font-size: 0.85rem;
        }}
        
        .method-GET {{ background: #e3f2fd; color: #1976d2; }}
        .method-POST {{ background: #e8f5e9; color: #388e3c; }}
        .method-PUT {{ background: #fff3e0; color: #f57c00; }}
        .method-DELETE {{ background: #ffebee; color: #d32f2f; }}
        .method-PATCH {{ background: #f3e5f5; color: #7b1fa2; }}
        
        .path {{
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 0.95rem;
            color: #333;
            word-break: break-all;
        }}
        
        .description {{
            color: #666;
            margin: 0.5rem 0;
        }}
        
        .details {{
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid #f0f0f0;
        }}
        
        .detail-item {{
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0;
            font-size: 0.9rem;
        }}
        
        .detail-label {{
            color: #999;
        }}
        
        .detail-value {{
            font-weight: 500;
        }}
        
        .tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 1rem;
        }}
        
        .tag {{
            background: #f0f0f0;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.85rem;
            color: #666;
        }}
        
        .service-card {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }}
        
        .service-card .card-header {{
            border-bottom-color: rgba(255,255,255,0.3);
        }}
        
        .infra-card {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }}
        
        .infra-card .card-header {{
            border-bottom-color: rgba(255,255,255,0.3);
        }}
        
        .search-box {{
            width: 100%;
            padding: 1rem;
            font-size: 1rem;
            border: 2px solid #ddd;
            border-radius: 8px;
            margin-bottom: 2rem;
        }}
        
        .search-box:focus {{
            outline: none;
            border-color: #667eea;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔌 API Extraction Dashboard</h1>
        <p>Framework-agnostic API and Infrastructure Discovery</p>
        <div class="stats">
            <div class="stat-card">
                <div class="stat-label">APIs</div>
                <div class="stat-value">{total_apis}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Services</div>
                <div class="stat-value">{total_services}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Infrastructure</div>
                <div class="stat-value">{total_infrastructure}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Environment</div>
                <div class="stat-value">{environment}</div>
            </div>
        </div>
    </div>
    
    <div class="container">
        <input type="text" class="search-box" id="searchBox" placeholder="Search APIs, services, infrastructure...">
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('apis')">APIs ({total_apis})</button>
            <button class="tab" onclick="showTab('services')">Services ({total_services})</button>
            <button class="tab" onclick="showTab('infrastructure')">Infrastructure ({total_infrastructure})</button>
        </div>
        
        <div id="apis" class="tab-content active">
            <div class="grid" id="apisGrid">
                {apis_html}
            </div>
        </div>
        
        <div id="services" class="tab-content">
            <div class="grid" id="servicesGrid">
                {services_html}
            </div>
        </div>
        
        <div id="infrastructure" class="tab-content">
            <div class="grid" id="infrastructureGrid">
                {infrastructure_html}
            </div>
        </div>
    </div>
    
    <script>
        const data = {data_json};
        
        function showTab(tabName) {{
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});
            document.querySelectorAll('.tab').forEach(btn => {{
                btn.classList.remove('active');
            }});
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }}
        
        function filterCards(searchTerm) {{
            const cards = document.querySelectorAll('.card');
            const term = searchTerm.toLowerCase();
            
            cards.forEach(card => {{
                const text = card.textContent.toLowerCase();
                if (text.includes(term)) {{
                    card.style.display = '';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }}
        
        document.getElementById('searchBox').addEventListener('input', (e) => {{
            filterCards(e.target.value);
        }});
    </script>
</body>
</html>
"""


def generate_html(output: UnifiedOutput, output_path: str):
    """
    Generate HTML visualization from unified output.
    
    Args:
        output: Unified output containing all extracted data
        output_path: Path to save HTML file
    """
    # Generate API cards HTML
    apis_html = ""
    for api in output.apis:
        method_badge = f'<span class="method-badge method-{api.method.value}">{api.method.value}</span>'
        path = f'<div class="path">{api.path}</div>'
        description = f'<div class="description">{api.description or api.summary or "No description"}</div>' if (api.description or api.summary) else ""
        
        details = f"""
            <div class="details">
                <div class="detail-item">
                    <span class="detail-label">Service:</span>
                    <span class="detail-value">{api.service_name or 'N/A'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Handler:</span>
                    <span class="detail-value">{api.handler_name or 'N/A'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">File:</span>
                    <span class="detail-value">{api.handler_file or 'N/A'}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Auth:</span>
                    <span class="detail-value">{'Required' if api.auth_required else 'Not Required'}</span>
                </div>
            </div>
        """
        
        tags_html = ""
        if api.tags:
            tags_html = '<div class="tags">' + ''.join([f'<span class="tag">{tag}</span>' for tag in api.tags]) + '</div>'
        
        apis_html += f"""
            <div class="card">
                <div class="card-header">
                    {method_badge}
                </div>
                {path}
                {description}
                {details}
                {tags_html}
            </div>
        """
    
    # Generate service cards HTML
    services_html = ""
    for service in output.services:
        service_html = f"""
            <div class="card service-card">
                <div class="card-header">
                    <h3>{service.name}</h3>
                </div>
                <div class="details">
                    <div class="detail-item">
                        <span class="detail-label">Type:</span>
                        <span class="detail-value">{service.type}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Language:</span>
                        <span class="detail-value">{service.language or 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">APIs:</span>
                        <span class="detail-value">{len(service.api_ids)}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Infrastructure:</span>
                        <span class="detail-value">{len(service.infrastructure_ids)}</span>
                    </div>
                </div>
            </div>
        """
        services_html += service_html
    
    # Generate infrastructure cards HTML
    infrastructure_html = ""
    for infra in output.infrastructure:
        infra_html = f"""
            <div class="card infra-card">
                <div class="card-header">
                    <h3>{infra.resource_name}</h3>
                </div>
                <div class="path">{infra.type}</div>
                <div class="details">
                    <div class="detail-item">
                        <span class="detail-label">Provider:</span>
                        <span class="detail-value">{infra.provider}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Service:</span>
                        <span class="detail-value">{infra.service_name or 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Environment:</span>
                        <span class="detail-value">{infra.environment or 'N/A'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Region:</span>
                        <span class="detail-value">{infra.region or 'N/A'}</span>
                    </div>
                </div>
            </div>
        """
        infrastructure_html += infra_html
    
    # Generate data JSON for client-side use
    data_json = output.model_dump_json(indent=2)
    
    # Format HTML
    html = HTML_TEMPLATE.format(
        total_apis=len(output.apis),
        total_services=len(output.services),
        total_infrastructure=len(output.infrastructure),
        environment=output.environment or 'unknown',
        apis_html=apis_html,
        services_html=services_html,
        infrastructure_html=infrastructure_html,
        data_json=data_json
    )
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"HTML visualization generated: {output_path}")
