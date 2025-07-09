Great question! The files are automatically included in the pull request based on the commits in your branch. Here's how it works:

## The Key Concept
When you create a pull request, GitHub compares your `head` branch with the `base` branch and includes **all the differences** between them. PyGithub doesn't send individual files - it references the branch, and GitHub figures out what changed.

## Example Workflow

```python
# This is what you do BEFORE creating the PR
import subprocess
from github import Github

# 1. Make your changes to 3 files locally
# (edit file1.py, file2.py, file3.py)

# 2. Commit the changes to your branch
subprocess.run(["git", "add", "file1.py", "file2.py", "file3.py"])
subprocess.run(["git", "commit", "-m", "Update three files for new feature"])
subprocess.run(["git", "push", "origin", "feature-branch"])

# 3. NOW create the pull request
g = Github("your_token")
repo = g.get_repo("owner/repo")

pr = repo.create_pull(
    title="Update three files for new feature",
    body="Modified file1.py, file2.py, and file3.py",
    head="feature-branch",    # This branch contains your 3 changed files
    base="main"
)

print(f"PR created with all changes from feature-branch: {pr.html_url}")
```

## Checking What Files Are in Your PR

```python
# After creating the PR, you can see what files are included
files = pr.get_files()

print("Files in this pull request:")
for file in files:
    print(f"  {file.filename} ({file.status})")
    print(f"    +{file.additions} lines, -{file.deletions} lines")
```

Think of it like a package delivery - you don't tell the delivery service about each individual item in the box. Instead, you give them the box (your branch) and they deliver everything inside it. The pull request contains all commits (and therefore all file changes) that exist in your `head` branch but not in the `base` branch.

## The Git Commands Behind the Scenes
```bash
# What you typically do first:
git checkout -b feature-branch
# Edit your 3 files
git add file1.py file2.py file3.py
git commit -m "Updated three files"
git push origin feature-branch
# THEN create PR with PyGithub
```

The pull request will automatically include all three files because they're part of the commits in your `feature-branch` that aren't in `main`.

Does this clarify how the file inclusion works?
