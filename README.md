# yyiki

A git-based wiki written in Python. Create/Clone a git repository into `FLATPAGES_ROOT` directory and create markdown files. Because the wiki pages are simply markdown files, you can use other tools such as [Obsidian](https://obsidian.md/).

# Design principles

yyiki is designed as a personal wiki software and simplicity is the primary principle. 

- Markdown: yyiki only supports markdown, which is probably the most widely used, versatile, and simple document format. 
- Git and flatfiles: yyiki is also a git repository. This removes the complexity of database and makes back-up straightforward. It also opens up the possibility of using other offline apps (e.g. [Obsidian](https://obsidian.md). 
- Python (https://xkcd.com/353/) + [Flaks](https://palletsprojects.com/p/flask/) + [Flask-FlatPages](https://pythonhosted.org/Flask-FlatPages/) allows concise code. 

