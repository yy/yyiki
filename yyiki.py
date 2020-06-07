"""A minimal wiki app."""
import glob
import os
import subprocess
from datetime import datetime

import fuzzywuzzy
import yaml
from flask import Flask, redirect, render_template, url_for
from flask_bcrypt import Bcrypt
from flask_flatpages import FlatPages, pygments_style_defs
from flask_login import (LoginManager, UserMixin, current_user, login_required,
                         login_user, logout_user)
from fuzzywuzzy import process as fuzzprocess

from forms import EditForm, LoginForm, SearchForm
from utils import (commit_and_push_changes, get_non_private_page_paths,
                   path2filename, write_page)

app = Flask(__name__)

# Configuration
app.config.from_object("default_settings")

# Initialization
subprocess.run(["git", "-C", "pages", "pull"])
pages = FlatPages(app)
bcrypt = Bcrypt(app)
hashed_password = open("hashed_admin_password.dat", "rb").read()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):
    def __init__(self, user_id, email, hashed_password):
        self.id = user_id
        self.email = email
        self.hashed_password = hashed_password

    @classmethod
    def get(cls, user_id):
        if user_id == "0":
            return admin_user
        else:
            return None


admin_user = User(
    user_id="0", email="yongyeol@gmail.com", hashed_password=hashed_password
)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


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
        if page.meta.get("private", False) and not current_user.is_authenticated:
            return redirect(url_for("login"))
        form = SearchForm()
        template = page.meta.get("template", "page.html")
        return render_template(template, page=page, form=form)
    else:
        return redirect(url_for("search_page", path=path))


@app.route("/edit/<path:path>/")
@login_required
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


@app.route("/delete/<path:path>/")
@login_required
def delete_page(path):
    filename = path2filename(pages, path)
    if glob.glob(filename):
        subprocess.run(["rm", filename])
    pages.reload()
    return redirect(url_for("home"))


@app.route("/create/<path:path>")
@login_required
def create_page(path):
    filename = path2filename(pages, path)
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
    pages.reload()
    return redirect(url_for("edit_page", path=path))


@app.route("/search/<path:path>")
def search_page(path):
    form = SearchForm()
    if current_user.is_authenticated:
        page_paths = pages._pages.keys()
    else:
        page_paths = get_non_private_page_paths(pages)
    matches = [
        match
        for match, score in fuzzprocess.extract(
            path, page_paths, limit=10, scorer=fuzzywuzzy.fuzz.partial_ratio
        )
    ]
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
@login_required
def update_page():
    """Update page based on the information coming from the from the edit page.
    """
    form = EditForm()
    if form.validate_on_submit():
        page = pages.get(form.path.data)
        page.body = form.content.data
        page.meta = yaml.safe_load(form.pagemeta.data)
        write_page(pages, page)
        commit_and_push_changes()
    pages.reload()
    return redirect(url_for("show_page", path=page.path))


@app.route("/list/")
def page_list():
    form = SearchForm()
    articles = []
    for page in pages:
        if not current_user.is_authenticated and page.meta.get("private", False):
            continue
        filename = path2filename(pages, page.path)
        if not glob.glob(filename):
            continue
        mtime = os.path.getmtime(filename)
        isotime = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
        if "published" in page.meta:
            articles.append((mtime, isotime, page))

    sorted_article_list = sorted(articles, reverse=True, key=lambda p: p[0])
    return render_template("list.html", pages=sorted_article_list, form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == admin_user.email and bcrypt.check_password_hash(
            admin_user.hashed_password, form.password.data
        ):
            login_user(admin_user, remember=form.remember.data)
            return redirect(url_for("home"))
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
