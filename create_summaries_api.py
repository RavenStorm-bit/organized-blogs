#!/usr/bin/env python3
"""
Create a JSON API for accessing blog article summaries by different female characters.

This script generates JSON files that can be used as a simple API to access
the character-based summaries for blog articles.
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

# Output directory for API files
API_DIR = "/root/summaries_api"

def load_summaries():
    """Load all summaries from the summary directories"""
    all_articles = {}
    all_personas = {}
    
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
                
                # Get the article title and ID
                title = data.get("title", os.path.basename(summary_file).replace("_summaries.json", "").replace("_multi_summaries.json", "").replace("_mixed_summaries.json", "").replace("_single_summaries.json", "").replace("_dynamic_summaries.json", "").replace("_fixed_summaries.json", "").replace("_", " ").replace("-", " "))
                article_id = title.lower().replace(" ", "-").replace("'", "").replace('"', "").replace(":", "").replace(",", "").replace(".", "").replace("(", "").replace(")", "").replace("&", "and")
                file_path = data.get("file_path", "")
                
                # Create article entry if it doesn't exist
                if article_id not in all_articles:
                    all_articles[article_id] = {
                        "id": article_id,
                        "title": title,
                        "file_path": file_path,
                        "summaries": {},
                        "personas": {}
                    }
                
                # Add summaries for each persona
                for persona_name, summary in data.get("summaries", {}).items():
                    all_articles[article_id]["summaries"][persona_name] = summary
                    
                    # Add to personas list if not already there
                    if persona_name not in all_personas:
                        persona_description = ""
                        persona_example = ""
                        
                        # Try to get persona description from the article data
                        if "personas" in data and persona_name in data["personas"]:
                            persona_info = data["personas"][persona_name]
                            if isinstance(persona_info, dict) and "description" in persona_info:
                                persona_description = persona_info.get("description", "")
                                persona_example = persona_info.get("example", "")
                            elif isinstance(persona_info, str):
                                persona_description = persona_info
                        
                        all_personas[persona_name] = {
                            "name": persona_name,
                            "display_name": persona_name.replace('_', ' ').title(),
                            "description": persona_description,
                            "example": persona_example,
                            "article_count": 0
                        }
                    
                    # Increment article count for this persona
                    all_personas[persona_name]["article_count"] += 1
                    
                # Store persona information in article data
                if "personas" in data:
                    for persona_name, persona_info in data.get("personas", {}).items():
                        if persona_name in all_articles[article_id]["summaries"]:
                            # Only add description if we have a summary for this persona
                            if "description" not in all_articles[article_id]["personas"]:
                                all_articles[article_id]["personas"][persona_name] = {}
                                
                            # For persona objects with description field
                            if isinstance(persona_info, dict) and "description" in persona_info:
                                all_articles[article_id]["personas"][persona_name]["description"] = persona_info.get("description", "")
                                if "example" in persona_info:
                                    all_articles[article_id]["personas"][persona_name]["example"] = persona_info.get("example", "")
                            # For string descriptions
                            elif isinstance(persona_info, str):
                                all_articles[article_id]["personas"][persona_name]["description"] = persona_info
            
            except Exception as e:
                print(f"Error processing {summary_file}: {e}")
    
    return all_articles, all_personas

def categorize_article(file_path):
    """Categorize the article based on its file path"""
    if not file_path:
        return "Uncategorized"
    
    if "technical/" in file_path:
        return "Technical"
    elif "academic-historical/" in file_path:
        return "Academic & Historical"
    elif "reverse-engineering/" in file_path:
        return "Reverse Engineering"
    elif "chinese-studies/" in file_path:
        return "Chinese Studies"
    elif "media-analysis/" in file_path:
        return "Media Analysis"
    elif "dev-tutorials/" in file_path:
        return "Development Tutorials"
    else:
        return "General"

def create_api_files(articles, personas):
    """Create JSON API files"""
    # Create API directory if it doesn't exist
    os.makedirs(API_DIR, exist_ok=True)
    
    # Create index file with all articles
    index_data = {
        "articles": [],
        "personas": [],
        "categories": []
    }
    
    # Process articles
    categories = set()
    for article_id, article_data in articles.items():
        # Get category
        category = categorize_article(article_data.get("file_path", ""))
        categories.add(category)
        
        # Add to index
        index_data["articles"].append({
            "id": article_id,
            "title": article_data["title"],
            "category": category,
            "persona_count": len(article_data["summaries"])
        })
        
        # Create article detail file
        detail_data = {
            "id": article_id,
            "title": article_data["title"],
            "category": category,
            "summaries": article_data["summaries"]
        }
        
        article_file = os.path.join(API_DIR, f"article_{article_id}.json")
        with open(article_file, 'w', encoding='utf-8') as f:
            json.dump(detail_data, f, indent=2)
    
    # Add categories to index
    for category in categories:
        index_data["categories"].append({
            "name": category,
            "id": category.lower().replace(" & ", "-").replace(" ", "-"),
            "article_count": sum(1 for article in articles.values() if categorize_article(article.get("file_path", "")) == category)
        })
    
    # Process personas
    for persona_name, persona_data in personas.items():
        # Add to index
        index_data["personas"].append({
            "name": persona_name,
            "display_name": persona_data["display_name"],
            "article_count": persona_data["article_count"]
        })
        
        # Create persona detail file
        persona_articles = []
        for article_id, article_data in articles.items():
            if persona_name in article_data.get("summaries", {}):
                persona_articles.append({
                    "id": article_id,
                    "title": article_data["title"],
                    "summary": article_data["summaries"][persona_name]
                })
        
        detail_data = {
            "name": persona_name,
            "display_name": persona_data["display_name"],
            "description": persona_data["description"],
            "example": persona_data["example"],
            "article_count": persona_data["article_count"],
            "articles": persona_articles
        }
        
        persona_file = os.path.join(API_DIR, f"persona_{persona_name.replace(' ', '_').lower()}.json")
        with open(persona_file, 'w', encoding='utf-8') as f:
            json.dump(detail_data, f, indent=2)
    
    # Write index file
    index_file = os.path.join(API_DIR, "index.json")
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2)
    
    # Create a README file
    readme_content = """# Blog Summaries API

This directory contains JSON files that serve as a simple API for accessing blog article summaries written from the perspective of different female characters.

## API Structure

### Main Index

- `index.json`: List of all articles, personas, and categories

### Article Details

- `article_[id].json`: Details for a specific article, including all character summaries

### Persona Details

- `persona_[name].json`: Details for a specific persona, including all their article summaries

## Example Usage

To get all articles and personas:
```
GET /index.json
```

To get details for a specific article:
```
GET /article_foundational-principles-of-data-structures.json
```

To get all summaries by a specific persona:
```
GET /persona_catgirl.json
```
"""
    
    readme_file = os.path.join(API_DIR, "README.md")
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)

def main():
    """Main function"""
    print("Loading character summaries...")
    articles, personas = load_summaries()
    print(f"Found summaries for {len(articles)} articles and {len(personas)} personas")
    
    print("Creating API files...")
    create_api_files(articles, personas)
    
    print(f"API files created in {API_DIR}")

if __name__ == "__main__":
    main()