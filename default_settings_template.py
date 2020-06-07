SECRET_KEY = "your secret key here"
FLATPAGES_ROOT = "pages"
FLATPAGES_EXTENSION = ".md"
FLATPAGES_MARKDOWN_EXTENSIONS = [
    "codehilite",
    "markdown_katex",
    "mdx_wikilink_plus",
    "mdx_linkify",
    "mdx_headdown",
    "footnotes",
]
FLATPAGES_EXTENSION_CONFIGS = {
    "mdx_wikilink_plus": {
        "base_url": "/wiki/",
        "url_whitespace": " ",
        "label_case": "none",
    }
}
