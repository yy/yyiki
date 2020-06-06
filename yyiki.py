"""A minimal wiki app."""
import difflib
import glob
import os
import subprocess
from datetime import datetime

import yaml
from flask import Flask, redirect, render_template, url_for
from flask_flatpages import FlatPages, pygments_style_defs

from forms import EditForm, SearchForm


def path2filename(path):
    """Convert path to physical file path."""
    return "{}.md".format(os.path.join(pages.root, path))  # TODO: may not be safe


def commit_and_push_changes():
    GIT_COMMAND = ["git", "-C", "pages"]
    subprocess.run(GIT_COMMAND + ["add", "*"])
    subprocess.run(GIT_COMMAND + ["commit", "-m", "edited via yyiki"])
    os.spawnlp(os.P_NOWAIT, "git", *GIT_COMMAND, "push")


def write_page(page):
    # TODO: check the safety of page.path when there's a space or other
    # characters in the page.path.
    filename = path2filename(page.path)
    with open(filename, "w") as f:
        f.write(yaml.dump(page.meta))
        f.write("\n")
        f.write(page.body.replace("\r", ""))


app = Flask(__name__)

# Configuration
app.config["SECRET_KEY"] = "98e3fee0a08d82be883a324c47f3fee1"

app.config["FLATPAGES_ROOT"] = "pages"
app.config["FLATPAGES_EXTENSION"] = ".md"
app.config["FLATPAGES_MARKDOWN_EXTENSIONS"] = [
    "codehilite",
    "markdown_katex",
    "mdx_wikilink_plus",
    "mdx_linkify",
    "mdx_headdown",
]
app.config["FLATPAGES_EXTENSION_CONFIGS"] = {
    "mdx_wikilink_plus": {"base_url": "/wiki/"}
}

# Initialization
subprocess.run(["git", "-C", "pages", "pull"])
pages = FlatPages(app)


@app.route("/pygments.css")
def pygments_css():
    return pygments_style_defs("tango"), 200, {"Content-Type": "text/css"}


@app.route("/")
def home():
    return redirect(url_for("show_page", path="Home"))


@app.route("/wiki/<path:path>/")
def show_page(path):
    page = pages.get(path)
    if page:
        form = SearchForm()
        template = page.meta.get("template", "page.html")
        return render_template(template, page=page, form=form)
    else:
        return redirect(url_for("search_page", path=path))


@app.route("/edit/<path:path>/")
def edit_page(path):
    page = pages.get(path)
    if page:
        form = EditForm()
        form.path.data = page.path
        form.content.data = page.body
        form.pagemeta.data = yaml.dump(page.meta, allow_unicode=True)
        return render_template("edit.html", page=page, form=form)
    else:
        redirect(url_for("create_page", path=path))


@app.route("/create/<path:path>")
def create_page(path):
    filename = path2filename(path)
    if glob.glob(filename):
        redirect(url_for("edit_page", path=path))
    today_iso = datetime.today().strftime("%Y-%m-%d")
    with open(filename, "w") as fout:
        fout.write(
            "\n".join(
                [
                    "title: {}".format(path),
                    "author: y",
                    "published: {}\n".format(today_iso),
                    "content",
                ]
            )
        )
    return redirect(url_for("edit_page", path=path))


@app.route("/search/<path:path>")
def search_page(path):
    form = SearchForm()
    matches = difflib.get_close_matches(path, pages._pages.keys(), n=10, cutoff=0.5)
    page = pages.get(path, {"path": path, "title": path, "page_found": False})
    try:
        page_found = page.get("page_found")
    except AttributeError:
        page_found = True
    return render_template(
        "search.html", page_found=page_found, page=page, matches=matches, form=form
    )


@app.route("/search", methods=["GET", "POST"])
def search_page_from_form():
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(url_for("search_page", path=form.query.data))
    else:
        return redirect(url_for("show_page", path="Home"))


@app.route("/save", methods=["GET", "POST"])
def update_page():
    """Update page based on the information coming from the from the edit page.
    """
    form = EditForm()
    if form.validate_on_submit():
        page = pages.get(form.path.data)
        page.body = form.content.data
        page.meta = yaml.safe_load(form.pagemeta.data)
        write_page(page)
        commit_and_push_changes()
    return redirect(url_for("show_page", path=page.path))


@app.route("/list/")
def page_list():
    form = SearchForm()
    articles = []
    for page in pages:
        filename = path2filename(page.path)
        mtime = os.path.getmtime(filename)
        isotime = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
        if "published" in page.meta:
            articles.append((mtime, isotime, page))

    sorted_article_list = sorted(articles, reverse=True, key=lambda p: p[0])
    return render_template("list.html", pages=sorted_article_list, form=form)


if __name__ == "__main__":
    app.run(debug=True)
