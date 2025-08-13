import os
import re

import git
import yaml


def is_safe_path(path):
    """Check if a path is safe for use as a wiki page path.
    
    Returns True if the path contains only allowed characters.
    Allows Unicode characters (accents, n-dashes, etc.) while preventing
    path traversal and filesystem-problematic characters.
    """
    if not path:
        return False
    
    # Check for path traversal attempts
    if '..' in path or path.startswith('/'):
        return False
    
    # Disallow control characters and problematic filesystem characters
    # \x00-\x1f are control characters
    # \x7f is DEL character
    # < > : " | ? * are problematic on Windows/some filesystems
    # \ is problematic as a path separator
    forbidden_chars = r'[\x00-\x1f\x7f<>:"|?*\\]'
    if re.search(forbidden_chars, path):
        return False
    
    return True


def path2filename(pages, path):
    """Convert path to physical file path safely.
    
    Prevents directory traversal attacks by ensuring the resolved path
    stays within the pages.root directory.
    """
    # Validate the path first
    if not is_safe_path(path):
        raise ValueError(f"Invalid path: {path}")
    
    # Remove any leading/trailing slashes and normalize the path
    safe_path = os.path.normpath(path.strip('/'))
    
    # Reject paths that try to go up directories
    if '..' in safe_path.split(os.sep):
        raise ValueError(f"Invalid path: {path}")
    
    # Construct the full path
    full_path = os.path.abspath(os.path.join(pages.root, safe_path + '.md'))
    
    # Ensure the resolved path is within pages.root
    pages_root = os.path.abspath(pages.root)
    if not full_path.startswith(pages_root + os.sep):
        raise ValueError(f"Path outside pages directory: {path}")
    
    return full_path


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
    # Path safety is now handled by path2filename() which validates
    # and sanitizes the path to prevent directory traversal attacks
    filename = path2filename(pages, page.path)
    with open(filename, "w") as f:
        f.write(yaml.dump(page.meta))
        f.write("\n")
        f.write(page.body.replace("\r", ""))
