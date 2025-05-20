# Blog Summaries API

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
