#!/usr/bin/env python3
import os
import json
import time
import glob
import random
from openai import OpenAI
import concurrent.futures
import argparse

# API key provided by user
API_KEY = "xai-YNpFliClAqJwU3OKJLd1SOhemfZ9yY3oEOQqrAxaLivnZptzsgkkCSwN5oQ1yxD1XhYIVK1yhEfXeArk"

# Configure the OpenAI client to use X.AI's API
client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.x.ai/v1"
)

def generate_multiple_personas(article_text, article_title, num_personas=3, model="grok-3-fast"):
    """Generate multiple unique, attractive female personas for an article"""
    print(f"Generating {num_personas} unique female personas for '{article_title}'...")
    
    prompt = f"""
Create {num_personas} UNIQUE, ATTRACTIVE FEMALE CHARACTER PERSONAS that would be perfect for summarizing the following article.
Each persona should have a distinct personality, speech pattern, and style.

ARTICLE TITLE: {article_title}

ARTICLE SNIPPET:
{article_text[:800]}... (article continues)

INSTRUCTIONS:
1. Create {num_personas} different attractive, interesting female characters with distinctive personalities, voices, and traits.
2. Each should be very different from the others - diverse in age, background, style, and speech patterns.
3. All should be appealing, charismatic, and have an interesting connection to the article's subject.
4. Make each character feel realistic and three-dimensional.
5. Each character should have a unique speech pattern or verbal quirk.

IMPORTANT: Your response should be in JSON format with an array of personas:
{{
  "personas": [
    {{
      "name": "character_type_name_1",
      "description": "Detailed description of the character and how she speaks",
      "example": "A brief example of how she would talk about a technical topic"
    }},
    {{
      "name": "character_type_name_2",
      "description": "Detailed description of the character and how she speaks",
      "example": "A brief example of how she would talk about a technical topic"
    }},
    ... (more personas)
  ]
}}

Make each character INTERESTING, DISTINCTIVE, and ATTRACTIVE in different ways.
"""
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert creative writer who specializes in developing unique, attractive female character personas."},
                {"role": "user", "content": prompt}
            ],
            temperature=1.0,  # High temperature for creative outputs
            max_tokens=1500   # Allowing enough space for multiple detailed personas
        )
        
        persona_json = response.choices[0].message.content.strip()
        
        # Extract the JSON object (handling potential formatting issues)
        import re
        json_match = re.search(r'\{[\s\S]*\}', persona_json)
        if json_match:
            persona_json = json_match.group(0)
        
        try:
            persona_data = json.loads(persona_json)
            personas = persona_data.get("personas", [])
            print(f"Created {len(personas)} personas:")
            for persona in personas:
                print(f"  - {persona['name']}")
            return personas
        except json.JSONDecodeError as e:
            print(f"Error parsing persona JSON: {e}")
            return []
            
    except Exception as e:
        print(f"Error generating personas: {e}")
        return []

def generate_summary(article_text, article_title, persona, model="grok-3-fast"):
    """Generate a persona-based summary of the article"""
    print(f"Generating {persona['name']} summary for '{article_title}'...")
    
    prompt = f"""
You are a content summarizer who takes on the personality of different female character types. You need to write a SHORT 1-3 sentence summary of a technical article in the character style described below.

CHARACTER: {persona['description']}
EXAMPLE STYLE: "{persona['example']}"

ARTICLE TITLE: {article_title}

ARTICLE CONTENT:
{article_text[:1500]}... (article continues)

Write a SHORT (1-3 sentence), catchy summary of this article in the described character style. 
Capture the key topic of the article while fully embracing the character persona. 
IMPORTANT: Keep it under 280 characters (Twitter-length).
DO NOT use quotation marks around the summary.
"""
    
    try:
        start_time = time.time()
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a creative writer who can create engaging character-based summaries in different female personas."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,  # Higher temperature for creative outputs
            max_tokens=300    # Ensuring we get a short response
        )
        end_time = time.time()
        
        summary = response.choices[0].message.content.strip()
        
        print(f"  Generated {persona['name']} summary in {end_time - start_time:.2f} seconds")
        print(f"  Summary length: {len(summary)} characters")
        print(f"  Summary: {summary}")
        
        return summary, end_time - start_time, response.usage
        
    except Exception as e:
        print(f"Error generating summary: {e}")
        return None, 0, None

def process_article(file_path, num_personas=3, output_dir="/root/multiple_personas_summaries"):
    """Process a single article to generate multiple persona summaries"""
    try:
        print(f"\nProcessing article: {file_path}")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Read the article file
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Get article title from first line (assumes markdown with # Title format)
        lines = content.split('\n')
        title = None
        for line in lines:
            if line.strip().startswith('# '):
                title = line.lstrip('#').strip()
                break
                
        if not title:
            # Try to get title from the first paragraph
            for i, line in enumerate(lines):
                if line.strip() and i > 0:  # Skip empty lines and find first non-empty line
                    title = line.strip()[:100]  # Use first 100 chars of first non-empty line
                    break
        
        if not title:
            title = os.path.basename(file_path).replace('.md', '').replace('_', ' ')
        
        article_results = {
            "file_path": file_path,
            "title": title,
            "summaries": {},
            "stats": {},
            "personas": {}
        }
        
        # Generate multiple personas
        personas = generate_multiple_personas(content, title, num_personas=num_personas)
        
        # Store the generated personas in the results
        for persona in personas:
            article_results["personas"][persona["name"]] = {
                "description": persona["description"],
                "example": persona["example"]
            }
        
        # Generate summary for each persona
        for persona in personas:
            try:
                summary, processing_time, usage = generate_summary(content, title, persona)
                
                if summary:
                    article_results["summaries"][persona["name"]] = summary
                    article_results["stats"][persona["name"]] = {
                        "time_seconds": processing_time,
                        "total_tokens": usage.total_tokens if usage else 0,
                        "prompt_tokens": usage.prompt_tokens if usage else 0,
                        "completion_tokens": usage.completion_tokens if usage else 0
                    }
            except Exception as e:
                print(f"  Error generating {persona['name']} summary: {e}")
        
        # Save the results
        output_file = os.path.join(output_dir, os.path.basename(file_path).replace('.md', '_multi_summaries.json'))
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(article_results, f, indent=2)
        
        print(f"Multiple persona summaries saved to {output_file}")
        return article_results
        
    except Exception as e:
        print(f"Error processing article {file_path}: {e}")
        return None

def process_articles_batch(article_files, num_personas=3, max_workers=3, output_dir="/root/multiple_personas_summaries"):
    """Process multiple articles in parallel"""
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(process_article, file_path, num_personas, output_dir): file_path for file_path in article_files}
        
        for future in concurrent.futures.as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                result = future.result()
                if result:
                    results.append(result)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
    
    # Save a summary of all processed articles
    summary_file = os.path.join(output_dir, "multi_personas_index.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump({
            "processed_articles": len(results),
            "article_files": [r["file_path"] for r in results],
            "personas_per_article": num_personas,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }, f, indent=2)
    
    print(f"\nProcessed {len(results)} out of {len(article_files)} articles with {num_personas} personas each.")
    print(f"Summary index saved to {summary_file}")
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Generate multiple attractive female persona summaries for each blog article")
    parser.add_argument("--all", action="store_true", help="Process all articles")
    parser.add_argument("--limit", type=int, default=3, help="Limit the number of articles to process")
    parser.add_argument("--personas", type=int, default=3, help="Number of personas to generate per article")
    parser.add_argument("--workers", type=int, default=2, help="Number of parallel workers")
    parser.add_argument("--output", type=str, default="/root/multiple_personas_summaries", help="Output directory")
    args = parser.parse_args()
    
    print("=== Multiple AI-Generated Attractive Female Personas Summary Generator ===")
    
    # Find all markdown files
    article_files = glob.glob("/root/organized-blogs/blogs/**/*.md", recursive=True)
    
    # Skip the index.md if it exists
    article_files = [f for f in article_files if not f.endswith('/index.md')]
    
    print(f"Found {len(article_files)} markdown files")
    
    if not args.all:
        # Limit the number of articles for testing
        article_files = article_files[:args.limit]
        print(f"Processing the first {len(article_files)} articles (use --all to process all)")
    
    print(f"Generating {args.personas} unique female personas for each article")
    
    # Process articles in parallel
    process_articles_batch(article_files, num_personas=args.personas, max_workers=args.workers, output_dir=args.output)

if __name__ == "__main__":
    main()