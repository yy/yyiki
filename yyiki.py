from flask import Flask, redirect, render_template, url_for
from flask_flatpages import FlatPages, pygments_style_defs

from forms import SearchForm

app = Flask(__name__)

app.config["SECRET_KEY"] = "98e3fee0a08d82be883a324c47f3fee1"

app.config["FLATPAGES_ROOT"] = "pages"
app.config["FLATPAGES_EXTENSION"] = ".md"
app.config["FLATPAGES_MARKDOWN_EXTENSIONS"] = [
    "codehilite",
    "markdown_katex",
    "mdx_wikilink_plus",
    "mdx_linkify",
]
app.config["FLATPAGES_EXTENSION_CONFIGS"] = {
    "mdx_wikilink_plus": {"base_url": "/wiki/"}
}

pages = FlatPages(app)


@app.route("/")
def home():
    return render_template("home.html", page={"title": "Home", "content": "home"})


@app.route("/pygments.css")
def pygments_css():
    return pygments_style_defs("tango"), 200, {"Content-Type": "text/css"}


@app.route("/new/<path:path>/")
def create_page(path):
    pass


@app.route("/wiki/<path:path>/")
def page(path):
    page = pages.get_or_404(path)
    form = SearchForm()
    template = page.meta.get("template", "page.html")
    return render_template(template, page=page, form=form)


@app.route("/search", methods=["GET", "POST"])
def search():
    form = SearchForm()
    print(form.query)
    if form.validate_on_submit():
        return redirect(f"/wiki/{form.query.data}")
    return redirect("/wiki/Home")


if __name__ == "__main__":
    app.run(debug=True)
