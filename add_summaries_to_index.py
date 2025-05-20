#!/usr/bin/env python3
"""
Add character-based summaries to the blog index.md file.

This script reads all generated character-based summaries from the 
various output directories and adds them to the appropriate blog entries
in the index.md file.
"""

import os
import re
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

# Path to index.md
INDEX_MD_PATH = "/root/organized-blogs/blogs/index.md"

def clean_filename(filename):
    """Clean a filename for matching with blog entries"""
    return filename.replace('_', ' ').replace('-', ' ').lower()

def extract_title_from_path(path):
    """Extract a clean title from a file path"""
    filename = os.path.basename(path)
    title = os.path.splitext(filename)[0]
    return title.replace('_', ' ').replace('-', ' ')

def load_summaries():
    """Load all summaries from the summary directories"""
    all_summaries = {}
    
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
                
                # Get the clean title for matching
                if "title" in data:
                    title = data["title"]
                else:
                    title = extract_title_from_path(data.get("file_path", summary_file))
                
                clean_title = clean_filename(title)
                
                # Store the summaries with title as key
                if clean_title not in all_summaries:
                    all_summaries[clean_title] = {
                        "title": title,
                        "file_path": data.get("file_path", ""),
                        "personas": {}
                    }
                
                # Add summaries for each persona
                for persona_name, summary in data.get("summaries", {}).items():
                    all_summaries[clean_title]["personas"][persona_name] = summary
                    
                # If available, also store persona descriptions
                if "personas" in data:
                    for persona_name, persona_info in data.get("personas", {}).items():
                        if persona_name in all_summaries[clean_title]["personas"]:
                            # Only add description if we have a summary for this persona
                            if "description" not in all_summaries[clean_title]:
                                all_summaries[clean_title]["descriptions"] = {}
                            all_summaries[clean_title]["descriptions"][persona_name] = persona_info.get("description", "")
            
            except Exception as e:
                print(f"Error processing {summary_file}: {e}")
    
    return all_summaries

def update_index_md(summaries):
    """Update the index.md file with character summaries"""
    if not os.path.exists(INDEX_MD_PATH):
        print(f"Error: Index file not found at {INDEX_MD_PATH}")
        return
    
    with open(INDEX_MD_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split the content into sections based on the horizontal rule (---)
    sections = content.split('---\n')
    
    # Process each section
    for i, section in enumerate(sections):
        if i == 0 or not section.strip():
            continue
            
        # Try to extract the title
        title_match = re.search(r'###\s+\[(?:\*\*)?([^*\]]+)(?:\*\*)?\]', section)
        if not title_match:
            continue
            
        title = title_match.group(1).strip()
        clean_title = clean_filename(title)
        
        # Try to find matching summaries
        matched_summaries = None
        
        # Exact match
        if clean_title in summaries:
            matched_summaries = summaries[clean_title]
        else:
            # Partial match
            for summary_title, summary_data in summaries.items():
                if clean_title in summary_title or summary_title in clean_title:
                    matched_summaries = summary_data
                    break
        
        if not matched_summaries:
            continue
            
        # Check if we already have character summaries in this section
        if "Character Summaries" in section:
            # Skip if already has summaries
            continue
            
        # Add character summaries
        if matched_summaries["personas"]:
            # Create summary section
            summary_section = "\n\n**Character Summaries:**\n\n"
            
            # Add a subset of personas (maximum 4 to keep things manageable)
            persona_count = 0
            
            # Priority order for persona types
            persona_types = [
                # Dynamic custom personas based on content
                [p for p in matched_summaries["personas"].keys() if p not in ["catgirl", "sweet_girl", "elegant_mature", "teacher", "wife"]],
                # Fixed anime-inspired personas
                ["catgirl", "sweet_girl", "elegant_mature", "teacher", "wife"]
            ]
            
            # Add summaries based on priority
            for persona_list in persona_types:
                for persona in persona_list:
                    if persona in matched_summaries["personas"] and persona_count < 4:
                        summary = matched_summaries["personas"][persona]
                        
                        # Format the persona name nicely
                        display_name = persona.replace('_', ' ').title()
                        
                        # Add the summary
                        summary_section += f"- *{display_name}*: {summary}\n\n"
                        persona_count += 1
                        
                        # Stop after 4 personas
                        if persona_count >= 4:
                            break
                
                # Stop if we have enough personas
                if persona_count >= 4:
                    break
            
            # Add the summary section to the end of the article section
            new_section = section.rstrip() + summary_section
            sections[i] = new_section
    
    # Join the sections back together
    new_content = '---\n'.join(sections)
    
    # Write the updated content back to the file
    with open(INDEX_MD_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Updated index.md with character summaries")

def main():
    """Main function"""
    print("Loading character summaries...")
    summaries = load_summaries()
    print(f"Found summaries for {len(summaries)} articles")
    
    print("Updating index.md...")
    update_index_md(summaries)
    
    print("Done!")

if __name__ == "__main__":
    main()