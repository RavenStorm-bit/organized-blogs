#!/usr/bin/env python3
"""
Create an HTML gallery to browse blog articles with character-based summaries.

This script generates an attractive HTML interface that showcases the blog
articles with their various female persona summaries.
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

# Output HTML file
OUTPUT_HTML = "/root/blog_summaries_gallery.html"

# Path to blog content
BLOG_DIR = "/root/organized-blogs/blogs"

def load_summaries():
    """Load all summaries from the summary directories"""
    all_articles = {}
    
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
                
                # Get the article title 
                title = data.get("title", os.path.basename(summary_file).replace("_summaries.json", "").replace("_multi_summaries.json", "").replace("_mixed_summaries.json", "").replace("_single_summaries.json", "").replace("_dynamic_summaries.json", "").replace("_fixed_summaries.json", "").replace("_", " ").replace("-", " "))
                file_path = data.get("file_path", "")
                
                # Create article entry if it doesn't exist
                if title not in all_articles:
                    all_articles[title] = {
                        "title": title,
                        "file_path": file_path,
                        "summaries": {},
                        "personas": {}
                    }
                
                # Add summaries for each persona
                for persona_name, summary in data.get("summaries", {}).items():
                    all_articles[title]["summaries"][persona_name] = summary
                    
                # If available, also store persona descriptions
                if "personas" in data:
                    for persona_name, persona_info in data.get("personas", {}).items():
                        if persona_name in all_articles[title]["summaries"]:
                            # Only add description if we have a summary for this persona
                            if "description" not in all_articles[title]:
                                all_articles[title]["personas"][persona_name] = {}
                                
                            # For persona objects with description field
                            if isinstance(persona_info, dict) and "description" in persona_info:
                                all_articles[title]["personas"][persona_name]["description"] = persona_info.get("description", "")
                                if "example" in persona_info:
                                    all_articles[title]["personas"][persona_name]["example"] = persona_info.get("example", "")
                            # For string descriptions
                            elif isinstance(persona_info, str):
                                all_articles[title]["personas"][persona_name]["description"] = persona_info
            
            except Exception as e:
                print(f"Error processing {summary_file}: {e}")
    
    return all_articles

def extract_excerpt(file_path, max_length=300):
    """Extract a brief excerpt from the original article"""
    if not file_path or not os.path.exists(file_path):
        return ""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove markdown headings
        content = re.sub(r'^#.*$', '', content, flags=re.MULTILINE)
        
        # Remove blank lines
        content = re.sub(r'\n\s*\n', '\n', content)
        
        # Get the first paragraph
        first_paragraph = content.strip().split('\n')[0]
        
        # Truncate if needed and add ellipsis
        if len(first_paragraph) > max_length:
            return first_paragraph[:max_length] + "..."
        return first_paragraph
        
    except Exception as e:
        print(f"Error extracting excerpt from {file_path}: {e}")
        return ""

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

def generate_html(articles):
    """Generate an HTML gallery of articles with persona summaries"""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blog Articles with Character Summaries</title>
    <style>
        :root {
            --primary-color: #6d4c41;
            --secondary-color: #8d6e63;
            --accent-color: #ff7043;
            --light-bg: #f5f5f5;
            --card-bg: #ffffff;
            --text-color: #333333;
            --header-bg: #5d4037;
            --header-text: #ffffff;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--light-bg);
            margin: 0;
            padding: 0;
        }
        
        header {
            background-color: var(--header-bg);
            color: var(--header-text);
            padding: 2rem;
            text-align: center;
        }
        
        h1 {
            margin: 0;
            font-size: 2.5rem;
        }
        
        .subtitle {
            font-style: italic;
            margin-top: 0.5rem;
            font-size: 1.2rem;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .filters {
            margin-bottom: 2rem;
            text-align: center;
        }
        
        button {
            background-color: var(--secondary-color);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            margin: 0.25rem;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        
        button:hover {
            background-color: var(--primary-color);
        }
        
        button.active {
            background-color: var(--accent-color);
        }
        
        .articles {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 2rem;
        }
        
        .article-card {
            background-color: var(--card-bg);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .article-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }
        
        .article-header {
            background-color: var(--primary-color);
            color: white;
            padding: 1rem;
            position: relative;
        }
        
        .category-tag {
            position: absolute;
            top: 0;
            right: 0;
            background-color: var(--accent-color);
            color: white;
            font-size: 0.8rem;
            padding: 0.25rem 0.5rem;
            border-bottom-left-radius: 4px;
        }
        
        .article-title {
            margin: 0;
            font-size: 1.3rem;
        }
        
        .article-excerpt {
            padding: 1rem;
            border-bottom: 1px solid #eee;
            font-style: italic;
            color: #666;
            font-size: 0.9rem;
        }
        
        .persona-tabs {
            display: flex;
            overflow-x: auto;
            background-color: var(--secondary-color);
        }
        
        .persona-tab {
            padding: 0.5rem 1rem;
            color: white;
            border: none;
            background: none;
            cursor: pointer;
            white-space: nowrap;
        }
        
        .persona-tab.active {
            background-color: var(--accent-color);
        }
        
        .summaries {
            padding: 0;
        }
        
        .summary {
            display: none;
            padding: 1rem;
        }
        
        .summary.active {
            display: block;
            animation: fadeIn 0.5s;
        }
        
        .summary-content {
            margin-bottom: 1rem;
        }
        
        .persona-info {
            font-size: 0.9rem;
            color: #666;
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px dashed #ddd;
        }
        
        .persona-name {
            font-weight: bold;
            color: var(--accent-color);
        }
        
        .show-persona-info {
            background: none;
            border: none;
            color: var(--accent-color);
            cursor: pointer;
            font-size: 0.9rem;
            padding: 0;
            margin-top: 0.5rem;
            text-decoration: underline;
        }
        
        .persona-description {
            display: none;
            margin-top: 0.5rem;
            font-style: italic;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        footer {
            text-align: center;
            padding: 2rem;
            background-color: var(--header-bg);
            color: var(--header-text);
            margin-top: 3rem;
            font-size: 0.9rem;
        }
        
        /* Responsive adjustments */
        @media (max-width: 768px) {
            .articles {
                grid-template-columns: 1fr;
            }
            
            .container {
                padding: 1rem;
            }
        }
    </style>
</head>
<body>
    <header>
        <h1>Blog Articles with Character Summaries</h1>
        <div class="subtitle">Explore technical blog articles from different female perspectives</div>
    </header>
    
    <div class="container">
        <div class="filters">
            <h2>Filter by Category</h2>
            <div class="category-buttons">
                <button class="filter-btn active" data-category="all">All Categories</button>
"""

    # Get unique categories
    categories = set()
    for article_data in articles.values():
        category = categorize_article(article_data.get("file_path", ""))
        categories.add(category)
    
    # Add category buttons
    for category in sorted(categories):
        html += f'                <button class="filter-btn" data-category="{category.lower().replace(" & ", "-").replace(" ", "-")}">{category}</button>\n'
    
    html += """            </div>
        </div>
        
        <div class="articles">
"""
    
    # Add articles
    for title, article_data in sorted(articles.items(), key=lambda x: x[0]):
        category = categorize_article(article_data.get("file_path", ""))
        category_class = category.lower().replace(" & ", "-").replace(" ", "-")
        excerpt = extract_excerpt(article_data.get("file_path", ""))
        
        # Skip if no summaries
        if not article_data.get("summaries", {}):
            continue
            
        html += f"""            <div class="article-card" data-category="{category_class}">
                <div class="article-header">
                    <div class="category-tag">{category}</div>
                    <h3 class="article-title">{title}</h3>
                </div>
                <div class="article-excerpt">
                    <p>{excerpt}</p>
                </div>
                <div class="persona-tabs">
"""
        
        # Add persona tabs
        for i, persona_name in enumerate(article_data["summaries"].keys()):
            display_name = persona_name.replace('_', ' ').title()
            active_class = "active" if i == 0 else ""
            html += f'                    <button class="persona-tab {active_class}" data-persona="{persona_name}">{display_name}</button>\n'
        
        html += """                </div>
                <div class="summaries">
"""
        
        # Add persona summaries
        for i, (persona_name, summary) in enumerate(article_data["summaries"].items()):
            display_name = persona_name.replace('_', ' ').title()
            active_class = "active" if i == 0 else ""
            
            # Get persona description if available
            persona_description = ""
            if persona_name in article_data.get("personas", {}):
                persona_info = article_data["personas"][persona_name]
                if isinstance(persona_info, dict) and "description" in persona_info:
                    persona_description = persona_info.get("description", "")
                elif isinstance(persona_info, str):
                    persona_description = persona_info
            
            html += f"""                    <div class="summary {active_class}" data-persona="{persona_name}">
                        <div class="summary-content">
                            {summary}
                        </div>
                        <div class="persona-info">
                            <span class="persona-name">{display_name}</span>
"""
            
            if persona_description:
                html += f"""                            <button class="show-persona-info">Show character info</button>
                            <div class="persona-description">{persona_description[:300]}...</div>
"""
            
            html += """                        </div>
                    </div>
"""
        
        html += """                </div>
            </div>
"""
    
    html += """        </div>
    </div>
    
    <footer>
        <p>Created with Grok Large Language Model</p>
        <p>© 2025 All Rights Reserved</p>
    </footer>
    
    <script>
        // Filter articles by category
        const filterButtons = document.querySelectorAll('.filter-btn');
        const articles = document.querySelectorAll('.article-card');
        
        filterButtons.forEach(button => {
            button.addEventListener('click', () => {
                // Update active button
                filterButtons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
                
                const category = button.getAttribute('data-category');
                
                // Show/hide articles
                articles.forEach(article => {
                    if (category === 'all' || article.getAttribute('data-category') === category) {
                        article.style.display = 'block';
                    } else {
                        article.style.display = 'none';
                    }
                });
            });
        });
        
        // Handle persona tabs
        const personaTabs = document.querySelectorAll('.persona-tab');
        
        personaTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                const personaName = tab.getAttribute('data-persona');
                const articleCard = tab.closest('.article-card');
                
                // Update active tab
                articleCard.querySelectorAll('.persona-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                // Show related summary
                articleCard.querySelectorAll('.summary').forEach(summary => {
                    if (summary.getAttribute('data-persona') === personaName) {
                        summary.classList.add('active');
                    } else {
                        summary.classList.remove('active');
                    }
                });
            });
        });
        
        // Handle show persona info buttons
        const infoButtons = document.querySelectorAll('.show-persona-info');
        
        infoButtons.forEach(button => {
            button.addEventListener('click', () => {
                const description = button.nextElementSibling;
                if (description.style.display === 'block') {
                    description.style.display = 'none';
                    button.textContent = 'Show character info';
                } else {
                    description.style.display = 'block';
                    button.textContent = 'Hide character info';
                }
            });
        });
    </script>
</body>
</html>
"""
    
    return html

def main():
    """Main function"""
    print("Loading character summaries...")
    articles = load_summaries()
    print(f"Found summaries for {len(articles)} articles")
    
    print("Generating HTML gallery...")
    html_content = generate_html(articles)
    
    # Write HTML file
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"HTML gallery created at {OUTPUT_HTML}")
    print("Open this file in a web browser to view the character summaries gallery")

if __name__ == "__main__":
    main()