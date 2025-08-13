# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

yyiki is a git-based personal wiki system built with Flask. It stores all content as markdown files in a git repository, providing version control and portability. The wiki supports private pages, fuzzy search, and is compatible with external markdown editors like Obsidian.

## Development Commands

### Setup
```bash
# Install dependencies using uv
uv sync

# Add new dependencies
uv add <package-name>

# Add development dependencies
uv add --dev <package-name>

# Initial setup
cp settings_template.py settings.py
cp templates/layout_template.html templates/layout.html
# Create hashed_admin_password.dat with bcrypt-hashed password
```

### Running the Application
```bash
# Run with uv
uv run python yyiki.py

# Or activate the virtual environment first
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
python yyiki.py
```
The app runs in debug mode on port 5000 by default.

### Code Quality
```bash
# Run linting with uv
uv run ruff check .
uv run flake8 .

# Sort imports
uv run isort .
```

## Architecture Overview

### Core Components

1. **yyiki.py**: Main Flask application containing all routes and authentication logic
   - Routes: `/wiki/<path>/`, `/edit/<path>/`, `/create/<path>`, `/delete/<path>/`, `/search/<path>`, `/list/`
   - Uses Flask-Login for single admin user authentication
   - Integrates Flask-FlatPages to serve markdown files from git

2. **utils.py**: Helper functions for git operations and file handling
   - `commit_and_push_changes()`: Handles git commits asynchronously
   - `write_page()`: Writes content and metadata to markdown files
   - `path2filename()`: Converts wiki paths to filesystem paths

3. **forms.py**: WTForms definitions for search, edit, and login functionality

### Key Design Patterns

1. **Git-Based Storage**: All pages stored as markdown files in a git repository
   - Automatic pull on startup
   - Async commit/push on changes
   - No database required

2. **Privacy Model**: Pages can have `private: true` in YAML frontmatter
   - Private pages require authentication
   - Search respects privacy settings

3. **Markdown Processing**: Extensive markdown extension support
   - KaTeX for math rendering
   - Wikilinks for internal links
   - Syntax highlighting with codehilite
   - Auto-linking URLs with mdx_linkify

### Important Notes

- **Security TODO**: There's a comment about potential security issues with path handling that should be addressed
- **Hardcoded Values**: Git commits use hardcoded author "YY Ahn <yongyeol@gmail.com>"
- **Single User**: Authentication supports only one admin user
- **No Tests**: No test suite currently exists
- **Keyboard Shortcuts**: The UI includes Mousetrap.js for keyboard navigation (h=home, e=edit, /=search, etc.)

### File Structure
```
yyiki.py          # Main application with all routes
forms.py          # Form definitions
utils.py          # Git and file utilities
settings.py       # Configuration (copy from template)
static/           # CSS files (main.css, tufte.css)
templates/        # Jinja2 templates
pages/            # Git repository containing wiki markdown files
```

### Working with Pages

Pages are markdown files with optional YAML frontmatter:
```markdown
---
title: Page Title
private: true  # Optional, makes page require authentication
---

Page content in markdown...
```

The wiki supports various markdown extensions configured in settings.py, including math notation, tables, footnotes, and more.