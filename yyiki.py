import os
from datetime import datetime

import yaml
from flask import Flask, redirect, render_template
from flask_flatpages import FlatPages, pygments_style_defs

from forms import EditForm, SearchForm

app = Flask(__name__)

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

pages = FlatPages(app)


@app.route("/")
def home():
    return redirect("/wiki/Home")


@app.route("/pygments.css")
def pygments_css():
    return pygments_style_defs("tango"), 200, {"Content-Type": "text/css"}


@app.route("/new/<path:path>/")
def create_page(path):
    pass


@app.route("/wiki/<path:path>/")
def show_page(path):
    page = pages.get_or_404(path)
    form = SearchForm()
    template = page.meta.get("template", "page.html")
    return render_template(template, page=page, form=form)


@app.route("/edit/<path:path>/")
def edit_page(path):
    page = pages.get(path)
    form = EditForm()
    form.path.data = page.path
    form.content.data = page.body
    form.pagemeta.data = yaml.dump(page.meta)
    # filename = "{}.md".format(os.path.join(pages.root, page.path))
    return render_template("edit.html", page=page, form=form)


def write_page(page):
    filename = "{}.md".format(os.path.join(pages.root, page.path))
    with open(filename, "w") as f:
        f.write(yaml.dump(page.meta))
        f.write("\n")
        f.write(page.body.replace("\r", ""))


@app.route("/save", methods=["GET", "POST"])
def save_page():
    form = EditForm()
    if form.validate_on_submit():
        page = pages.get(form.path.data)
        page.body = form.content.data
        page.meta = yaml.safe_load(form.pagemeta.data)
        write_page(page)
    return redirect(f"/wiki/{page.path}")


@app.route("/search", methods=["GET", "POST"])
def search_page():
    form = SearchForm()
    if form.validate_on_submit():
        return redirect(f"/wiki/{form.query.data}")
    return redirect("/wiki/Home")


@app.route("/list/")
def page_list():
    form = SearchForm()
    articles = []
    for page in pages:
        filename = "{}.md".format(os.path.join(pages.root, page.path))
        mtime = os.path.getmtime(filename)
        isotime = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
        if "published" in page.meta:
            articles.append((mtime, isotime, page))

    sorted_article_list = sorted(articles, reverse=True, key=lambda p: p[0])
    return render_template("list.html", pages=sorted_article_list, form=form)


if __name__ == "__main__":
    app.run(debug=True)
