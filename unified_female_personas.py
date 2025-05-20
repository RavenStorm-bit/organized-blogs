#!/usr/bin/env python3
"""
Unified Female Persona Blog Summary Generator

This script combines the best elements of all our previous scripts to:
1. Generate summaries of blog articles using different attractive female personas
2. Allow the LLM to choose appropriate personas for each article
3. Provide flexibility in how many personas to use per article
4. Allow fixed character types or dynamic, customized ones

Usage examples:
- Generate summaries with multiple AI-chosen female personas for each article:
  python3 unified_female_personas.py --mode dynamic --personas 3 --limit 5
  
- Use the predefined character archetypes:
  python3 unified_female_personas.py --mode fixed --limit 5
  
- Process all blog files with a mix of fixed and dynamic personas:
  python3 unified_female_personas.py --mode mixed --all
"""

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

# Base female personas (fixed character archetypes)
FIXED_PERSONAS = [
    {
        "name": "catgirl",
        "description": "A cute, playful catgirl who adds 'nya~' at the end of sentences, is curious about technology, and speaks in a sweet, slightly mischievous manner with cat-like expressions.",
        "example": "Ooh, data structures are so interesting nya~! I've been pouncing through the basics and they're purr-fect for organizing information! *wiggles ears* Learning about trees and stacks makes me so curious I could chase them all day~!"
    },
    {
        "name": "sweet_girl",
        "description": "A sweet, innocent young girl (甜妹) who speaks in a gentle, kind manner with some shyness. She uses soft expressions, speaks with warmth, and occasionally adds cute emoticons.",
        "example": "Umm... I was reading about programming today and it's actually quite interesting! (◕ᴗ◕✿) The way computers follow instructions is amazing... I hope I can learn more about it! It seems difficult but I'll try my best!"
    },
    {
        "name": "elegant_mature",
        "description": "A confident, sophisticated mature woman (御姐) who speaks with authority and elegance. She's knowledgeable, slightly flirtatious, and has a commanding yet warm presence.",
        "example": "Darling, let me tell you about this fascinating cryptography system I've been studying. It's quite... stimulating to see how complex security protocols work together. Perhaps I could show you sometime? *slight smile* The elegance of modern encryption is truly captivating."
    },
    {
        "name": "teacher",
        "description": "A patient, knowledgeable female teacher (老師) who explains complex topics in an accessible way. She's encouraging, kind but firm, and uses examples to illustrate her points.",
        "example": "Class, today we're going to learn about algorithms. Think of them as recipes for computers - step-by-step instructions to solve problems. Remember how we broke down that math problem yesterday? It's similar! Who would like to share an example from everyday life?"
    },
    {
        "name": "wife",
        "description": "A caring, mature housewife/wife (人妻) who relates topics to family life, speaks with warmth and wisdom, and has a nurturing yet somewhat knowing attitude.",
        "example": "Oh my, I was just reading about internet security while preparing dinner! It reminds me of how we need to protect our home - it's all about creating safe boundaries. I've already updated our family's passwords and showed the children how to spot those suspicious emails. Better safe than sorry, right? *warm smile*"
    }
]

# Additional female character inspiration for the LLM
CHARACTER_INSPIRATION = """
These are examples only - feel free to create attractive female characters:

- College Girl: A bright, enthusiastic college student who's excited about learning
- Career Woman: A sharp, driven professional woman who's stylish and confident
- Artist: A creative, expressive woman with poetic language and metaphors
- Gamer Girl: An energetic, tech-savvy girl who uses gaming references
- Fitness Instructor: A motivational, health-conscious woman with a positive attitude
- Cosplayer: A fun, imaginative woman who relates topics to pop culture and anime
- Cheerleader: An upbeat, encouraging woman who uses playful expressions
- Bookworm: A thoughtful, analytical woman who references literature
- Fashionista: A trendy, style-conscious woman who uses fashion analogies
- Barista: A warm, friendly woman who relates topics to coffee and cafe life
"""

def generate_single_persona(article_text, article_title, model="grok-3-fast"):
    """Generate a single custom persona based on article content"""
    print(f"Generating a custom female persona for '{article_title}'...")
    
    prompt = f"""
Based on the following article, create a UNIQUE, ATTRACTIVE FEMALE CHARACTER PERSONA that would be perfect for summarizing it. 
The persona should have a distinct personality, speech pattern, and style suitable for a captivating, engaging summary.

ARTICLE TITLE: {article_title}

ARTICLE SNIPPET:
{article_text[:800]}... (article continues)

INSTRUCTION:
1. Create an attractive, interesting female character with a distinctive personality, voice, and traits.
2. Include her name, age range (young adult to mature), and key personality traits.
3. Describe her speech pattern, vocabulary style, and any expressions she commonly uses.
4. Make her appealing, charismatic, and someone who would connect well with the article's subject.
5. Ensure the character feels realistic and three-dimensional.

IMPORTANT: Your response should be in JSON format with the following structure:
{{
  "name": "character_type_name",
  "description": "Detailed description of the character and how she speaks",
  "example": "A brief example of how she would talk about a technical topic"
}}

Make the character INTERESTING and DISTINCTIVE - avoid generic personalities.
"""
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert creative writer who specializes in developing unique, attractive female character personas."},
                {"role": "user", "content": prompt}
            ],
            temperature=1.0,  # High temperature for creative outputs
            max_tokens=800    # Allowing enough space for a detailed persona
        )
        
        persona_json = response.choices[0].message.content.strip()
        
        # Extract the JSON object (handling potential formatting issues)
        import re
        json_match = re.search(r'\{[\s\S]*\}', persona_json)
        if json_match:
            persona_json = json_match.group(0)
        
        try:
            persona = json.loads(persona_json)
            print(f"Created persona: {persona['name']}")
            print(f"Description: {persona['description'][:100]}...")
            return persona
        except json.JSONDecodeError as e:
            print(f"Error parsing persona JSON: {e}")
            # Fallback to a random fixed persona
            return random.choice(FIXED_PERSONAS)
            
    except Exception as e:
        print(f"Error generating persona: {e}")
        # Fallback to a random fixed persona
        return random.choice(FIXED_PERSONAS)

def generate_multiple_personas(article_text, article_title, num_personas=3, model="grok-3-fast"):
    """Generate multiple custom personas based on article content"""
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
            print(f"Error parsing personas JSON: {e}")
            # Return a subset of fixed personas as fallback
            return random.sample(FIXED_PERSONAS, min(num_personas, len(FIXED_PERSONAS)))
            
    except Exception as e:
        print(f"Error generating personas: {e}")
        # Return a subset of fixed personas as fallback
        return random.sample(FIXED_PERSONAS, min(num_personas, len(FIXED_PERSONAS)))

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

def process_article(file_path, mode="dynamic", num_personas=3, output_dir="/root/unified_summaries"):
    """Process a single article to generate persona-based summaries"""
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
        
        # Choose personas based on the selected mode
        personas = []
        
        if mode == "fixed":
            # Use the predefined fixed personas
            personas = FIXED_PERSONAS
        
        elif mode == "dynamic":
            # Generate multiple dynamic personas based on the article
            personas = generate_multiple_personas(content, title, num_personas)
        
        elif mode == "single":
            # Generate a single dynamic persona based on the article
            custom_persona = generate_single_persona(content, title)
            personas = [custom_persona]
            
        elif mode == "mixed":
            # Use a mix of fixed and dynamic personas
            # Include 2 fixed personas and generate the rest dynamically
            fixed_sample = random.sample(FIXED_PERSONAS, 2)
            custom_personas = generate_multiple_personas(content, title, num_personas - 2)
            personas = fixed_sample + custom_personas
        
        # Store the personas in the results
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
        clean_title = os.path.basename(file_path).replace('.md', '')
        output_file = os.path.join(output_dir, f"{clean_title}_{mode}_summaries.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(article_results, f, indent=2)
        
        print(f"Summaries saved to {output_file}")
        return article_results
        
    except Exception as e:
        print(f"Error processing article {file_path}: {e}")
        return None

def process_articles_batch(article_files, mode="dynamic", num_personas=3, max_workers=3, output_dir="/root/unified_summaries"):
    """Process multiple articles in parallel"""
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(process_article, file_path, mode, num_personas, output_dir): file_path 
                          for file_path in article_files}
        
        for future in concurrent.futures.as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                result = future.result()
                if result:
                    results.append(result)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
    
    # Save a summary of all processed articles
    summary_file = os.path.join(output_dir, f"summary_index_{mode}.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump({
            "processed_articles": len(results),
            "article_files": [r["file_path"] for r in results],
            "mode": mode,
            "personas_per_article": num_personas if mode in ["dynamic", "mixed"] else len(FIXED_PERSONAS) if mode == "fixed" else 1,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }, f, indent=2)
    
    print(f"\nProcessed {len(results)} out of {len(article_files)} articles in {mode} mode.")
    print(f"Summary index saved to {summary_file}")
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Unified Female Persona Blog Summary Generator")
    parser.add_argument("--all", action="store_true", help="Process all articles")
    parser.add_argument("--limit", type=int, default=3, help="Limit the number of articles to process")
    parser.add_argument("--personas", type=int, default=3, help="Number of personas to generate per article (for dynamic/mixed modes)")
    parser.add_argument("--workers", type=int, default=3, help="Number of parallel workers")
    parser.add_argument("--output", type=str, default="/root/unified_summaries", help="Output directory")
    parser.add_argument("--mode", type=str, choices=["fixed", "dynamic", "single", "mixed"], default="mixed",
                      help="Mode: fixed (predefined personas), dynamic (multiple AI-chosen personas), single (one AI-chosen persona), mixed (combination)")
    args = parser.parse_args()
    
    print("=== Unified Female Persona Blog Summary Generator ===")
    
    # Find all markdown files
    article_files = glob.glob("/root/organized-blogs/blogs/**/*.md", recursive=True)
    
    # Skip the index.md if it exists
    article_files = [f for f in article_files if not f.endswith('/index.md')]
    
    print(f"Found {len(article_files)} markdown files")
    
    if not args.all:
        # Limit the number of articles for testing
        article_files = article_files[:args.limit]
        print(f"Processing the first {len(article_files)} articles (use --all to process all)")
    
    # Print mode information
    mode_descriptions = {
        "fixed": "Using predefined female character archetypes",
        "dynamic": f"Generating {args.personas} unique female personas for each article",
        "single": "Generating one custom female persona per article",
        "mixed": f"Using a mix of fixed and {args.personas-2} custom-generated personas"
    }
    print(f"Mode: {mode_descriptions[args.mode]}")
    
    # Process articles in parallel
    process_articles_batch(
        article_files, 
        mode=args.mode, 
        num_personas=args.personas, 
        max_workers=args.workers, 
        output_dir=args.output
    )

if __name__ == "__main__":
    main()