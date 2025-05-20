#!/usr/bin/env python3
"""
List all the female personas created for blog summaries
"""

import os
import json
import glob
from collections import defaultdict

# Paths to summary directories
SUMMARY_DIRS = [
    "/root/character_summaries",
    "/root/character_summaries_custom",
    "/root/multiple_personas_summaries",
    "/root/unified_summaries"
]

def list_all_personas():
    """List all personas created across different summary directories"""
    all_personas = {}
    persona_count = defaultdict(int)
    
    for summary_dir in SUMMARY_DIRS:
        if not os.path.exists(summary_dir):
            continue
            
        # Find all JSON summary files
        summary_files = glob.glob(f"{summary_dir}/*_summaries.json")
        summary_files += glob.glob(f"{summary_dir}/*_multi_summaries.json")
        summary_files += glob.glob(f"{summary_dir}/*_mixed_summaries.json")
        summary_files += glob.glob(f"{summary_dir}/*_dynamic_summaries.json")
        summary_files += glob.glob(f"{summary_dir}/*_single_summaries.json")
        summary_files += glob.glob(f"{summary_dir}/*_fixed_summaries.json")
        
        for summary_file in summary_files:
            try:
                with open(summary_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Extract article title
                title = data.get("title", os.path.basename(summary_file))
                
                # Process persona information
                for persona_name, description in data.get("personas", {}).items():
                    if persona_name not in all_personas:
                        # For persona objects with description field
                        if isinstance(description, dict) and "description" in description:
                            all_personas[persona_name] = description.get("description", "")
                        # For string descriptions
                        elif isinstance(description, str):
                            all_personas[persona_name] = description
                
                # Count how many times each persona was used
                for persona_name in data.get("summaries", {}).keys():
                    persona_count[persona_name] += 1
            
            except Exception as e:
                print(f"Error processing {summary_file}: {e}")
    
    # Print results
    print(f"Found {len(all_personas)} unique female personas across all summaries:")
    print("\n" + "="*80 + "\n")
    
    # Sort by usage count (most used first)
    sorted_personas = sorted(persona_count.items(), key=lambda x: x[1], reverse=True)
    
    for i, (persona_name, count) in enumerate(sorted_personas, 1):
        display_name = persona_name.replace('_', ' ').title()
        print(f"{i}. {display_name} (used in {count} articles)")
        
        # Show description if available
        if persona_name in all_personas and all_personas[persona_name]:
            # Truncate long descriptions
            description = all_personas[persona_name]
            if len(description) > 200:
                description = description[:197] + "..."
            print(f"   Description: {description}")
        
        print()
    
    # Print some statistics
    print("="*80)
    print(f"Most popular personas:")
    for persona_name, count in sorted_personas[:5]:
        display_name = persona_name.replace('_', ' ').title()
        print(f"- {display_name}: {count} articles")
    
    print("\nLeast popular personas:")
    for persona_name, count in sorted_personas[-5:]:
        display_name = persona_name.replace('_', ' ').title()
        print(f"- {display_name}: {count} articles")
    
    print("\n" + "="*80)
    print(f"Total: {len(all_personas)} unique personas used in {sum(persona_count.values())} article summaries")

if __name__ == "__main__":
    list_all_personas()