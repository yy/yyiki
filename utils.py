import os

import git
import yaml


def path2filename(pages, path):
    """Convert path to physical file path."""
    return "{}.md".format(os.path.join(pages.root, path))  # TODO: may not be safe


def get_non_private_page_paths(pages):
    non_private_page_paths = []
    for page_path in pages._pages.keys():
        page = pages.get(page_path)
        if page.meta.get("private", False): 
            continue
        non_private_page_paths.append(page_path)
    return non_private_page_paths


def commit_and_push_changes():
    repo = git.Repo("pages")
    repo.git.add(A=True)
    repo.git.commit(m="edited via yyiki", author="YY Ahn <yongyeol@gmail.com>")
    # repo.git.push()

    GIT_COMMAND = ["git", "-C", "pages"]
    # subprocess.run(GIT_COMMAND + ["add", "*"])
    # subprocess.run(
    # GIT_COMMAND
    # + ["commit", "--author='YY Ahn <yongyeol@gmail.com>'", "-m", "edited via yyiki"]
    # )
    os.spawnlp(os.P_NOWAIT, "git", *GIT_COMMAND, "push")


def write_page(pages, page):
    # TODO: check the safety of page.path when there's a space or other
    # characters in the page.path.
    filename = path2filename(pages, page.path)
    with open(filename, "w") as f:
        f.write(yaml.dump(page.meta))
        f.write("\n")
        f.write(page.body.replace("\r", ""))
