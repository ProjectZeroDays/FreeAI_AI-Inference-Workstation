#!/usr/bin/env python3
"""Auto-generate API documentation from Flask routes.
Run with: python scripts/generate_api_docs.py
"""
import json
import os
import sys
from pathlib import Path


def generate_api_docs():
    """Generate API documentation from Flask app routes."""
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from dashboard import backend as dash
    
    docs = {
        "title": "FreeAI Dashboard API",
        "version": "1.0",
        "endpoints": []
    }
    
    for rule in dash.app.url_map.iter_rules():
        if rule.endpoint.startswith('static'):
            continue
        
        endpoint = {
            "path": rule.rule,
            "methods": list(rule.methods - {'HEAD', 'OPTIONS'}),
            "endpoint": rule.endpoint,
            "docstring": ""
        }
        
        # Get view function docstring
        view_func = dash.app.view_functions.get(rule.endpoint)
        if view_func and view_func.__doc__:
            endpoint["docstring"] = view_func.__doc__.strip().split('\n')[0]
        
        docs["endpoints"].append(endpoint)
    
    # Sort by path
    docs["endpoints"].sort(key=lambda x: x["path"])
    
    return docs


def generate_markdown(docs, output_path):
    """Generate Markdown API documentation."""
    lines = [
        "# FreeAI Dashboard API Reference",
        "",
        f"**Version:** {docs['version']}",
        f"**Total Endpoints:** {len(docs['endpoints'])}",
        "",
        "---",
        "",
    ]
    
    for ep in docs["endpoints"]:
        lines.append(f"## `{', '.join(ep['methods'])}` {ep['path']}")
        lines.append("")
        if ep["docstring"]:
            lines.append(f"{ep['docstring']}")
            lines.append("")
        lines.append(f"- **Endpoint:** `{ep['endpoint']}`")
        lines.append("")
        lines.append("---")
        lines.append("")
    
    with open(output_path, 'w') as f:
        f.write('\n'.join(lines))
    
    return output_path


def main():
    """Main entry point."""
    docs = generate_api_docs()
    
    output_dir = Path(__file__).parent.parent / "docs"
    output_dir.mkdir(exist_ok=True)
    
    # Generate Markdown
    md_path = output_dir / "api-reference.md"
    generate_markdown(docs, md_path)
    print(f"Generated: {md_path}")
    
    # Generate JSON
    json_path = output_dir / "api-reference.json"
    with open(json_path, 'w') as f:
        json.dump(docs, f, indent=2)
    print(f"Generated: {json_path}")
    
    print(f"\nTotal endpoints documented: {len(docs['endpoints'])}")


if __name__ == "__main__":
    main()
