# Female Character-Based Blog Summaries

This project uses the X.AI Grok LLM to generate summaries of technical blog articles from the perspectives of different female character personas.

## Overview

The project creates diverse, attractive female personas (from anime-inspired archetypes to custom-generated characters) and uses them to summarize technical blog articles with unique voices and perspectives.

## Key Features

- **Multiple Persona Types**: Includes both fixed anime-inspired archetypes (catgirl, sweet girl/甜妹, elegant mature woman/御姐, etc.) and dynamically generated female characters tailored to each article's content
  
- **Character Variety**: Generated over 300 unique female personas, each with distinct personalities, speech patterns, and perspectives
  
- **Flexible Generation**: Various modes for persona creation:
  - `fixed`: Uses predefined anime-inspired archetypes
  - `dynamic`: Generates multiple custom personas for each article
  - `single`: Creates one tailored persona per article
  - `mixed`: Combines fixed archetypes with custom personas

- **HTML Gallery**: Interactive web gallery to browse articles and their character summaries

- **JSON API**: Clean API structure for accessing summaries programmatically

## Scripts

- `generate_character_summaries.py`: Generates summaries using either fixed or custom personas
- `generate_multiple_personas.py`: Creates multiple unique personas for each article
- `unified_female_personas.py`: Combined script with all persona generation approaches
- `add_summaries_to_index.py`: Adds character summaries to blog index.md
- `create_html_gallery.py`: Creates interactive HTML browser for summaries
- `create_summaries_api.py`: Builds JSON API for accessing summaries
- `list_personas.py`: Utility to display all created personas

## Output Files

- `/character_summaries/`: Summaries using fixed anime archetypes
- `/character_summaries_custom/`: Summaries with single custom personas
- `/multiple_personas_summaries/`: Summaries with multiple custom personas
- `/unified_summaries/`: Combined approach summaries
- `blog_summaries_gallery.html`: Interactive HTML gallery
- `/summaries_api/`: JSON API files

## Project Statistics

- **Total Articles**: 98 blog posts summarized
- **Total Personas**: 319 unique female characters created
- **Character Summaries**: 1088 article summaries created
- **Top Personas**:
  - Wife (人妻): 106 articles
  - Sweet Girl (甜妹): 100 articles
  - Catgirl: 88 articles
  - Teacher (老師): 86 articles
  - Elegant Mature Woman (御姐): 82 articles

## Example Characters

1. **Catgirl**
   - "Ooh, data structures are so interesting nya~! I've been pouncing through the basics and they're purr-fect for organizing information!"

2. **Jade 'Cipher' Lin** (Cybersecurity Expert)
   - "Yo crew, let's crack the code on Xray configs for mainland China! This guide spills the deets on dodging the Great Firewall with slick protocols like VLESS and sneaky transports like XTLS."

3. **Dr. Eleanor Voss** (Sophisticated Academic)
   - "Darling, let me unveil the allure of AES-128, a cryptographic masterpiece that guards our digital secrets with unrivaled elegance."

4. **Lila 'Byte' Martinez** (Quirky Tech Vlogger)
   - "Okaaaay, so like, AES-128 is the ultimate digital bodyguard, protecting everything from your bank deets to gov secrets! It's got this super cool 10-round scramble that turns data into total chaos!"

## Usage

```bash
# Generate summaries with multiple custom personas
python3 unified_female_personas.py --mode dynamic --personas 3 --limit 5

# Use predefined anime archetypes
python3 unified_female_personas.py --mode fixed --limit 5

# Process all blog files with mixed personas
python3 unified_female_personas.py --mode mixed --all

# Create HTML gallery of all summaries
python3 create_html_gallery.py

# Create JSON API
python3 create_summaries_api.py
```

## License

This project is for educational and demonstration purposes only.