#!/usr/bin/env python3
"""
Script to convert JSON data to markdown table for README.md
"""

import json
import sys
from pathlib import Path
from municipalutils.geo_ref import *

def json_to_markdown_table(json_file_path, vars_col={}):
    """
    Convert JSON data to markdown table format
    
    Args:
        json_file_path (str): Path to the JSON file
        output_section (str): Section header for the markdown
    
    Returns:
        str: Formatted markdown table
    """
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        return f"Error: File {json_file_path} not found"
    except json.JSONDecodeError:
        return f"Error: Invalid JSON in {json_file_path}"
    
    if 'sources' not in data:
        return "Error: No 'sources' key found in JSON"
    
    markdown_lines = []
    
    # Table headers
    markdown_header = "| Country | Years |"
    markdown_header_lines = "| --- | --- |"
    if vars_col != {}:
        markdown_header += ' | '.join(col for col in vars_col.values()) + ' |'
        markdown_header_lines += ' | '.join('---' for _ in vars_col.values()) + ' |'
    markdown_header += " Sources | Comments |"
    markdown_header_lines += " --- | --- |"
    markdown_lines.append(markdown_header)
    markdown_lines.append(markdown_header_lines)
    
    # Table rows
    for source in data['sources']:
        iso3 = source.get('iso3', '')
        years = source.get('years', '')
        institution = source.get('institution', '')
        # age_groups = source.get('age_groups', [])
        # age_groups = ', '.join(age_groups)
        comments = source.get('comments', '')
        public = source.get('public', True)
        # place = source.get('place', '')

        # Handle multiple sources
        source_links = []
        if 'sources' in source and isinstance(source['sources'], list):
            for src in source['sources']:
                title = src.get('title', '')
                url = src.get('url', '')
                if url != "":
                    source_link_k = f"<a href=\"{url}\">{title}</a>"
                else:
                    source_link_k = title
                source_links.append(source_link_k)

        sources_cell = '; '.join(source_links) if source_links else ''
        if institution != '':
            sources_cell += f', {institution}'

        # Escape pipe characters in cell content
        sources_cell = sources_cell.replace('|', '\\|')

        markdown_line = f"| {iso3} | {years} | "
        for var, col in vars_col.items():
            markdown_line += f" {source.get(var, '')} | "
        markdown_line += f"{sources_cell} | {comments} | "
        
        if public:
            markdown_lines.append(
                markdown_line
            )
    
    return '\n'.join(markdown_lines)

def main():
    """Main function to generate markdown table"""
    vars_col = {
        'update': "Last update",

    }
    # Default paths
    for cat in ['childcare_poi', 
                'schools_poi',
                ]:
        json_file = Path(__file__).parent / f"{cat}.json"
        
        if len(sys.argv) > 1:
            json_file = Path(sys.argv[1])
        
        markdown_table = json_to_markdown_table(json_file, vars_col)
        
        
        output_file = f"{cat}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_table)

if __name__ == "__main__":
    main()
