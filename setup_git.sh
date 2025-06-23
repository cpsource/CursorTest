#!/bin/bash
#
## Initialize git repository in current directory
git init

# Add the remote repository (your GitHub repo)
git remote add origin git@github.com:cpsource/CursorTest.git

# Create a .gitignore file to exclude sensitive files
#echo ".env" >> .gitignore
#echo "__pycache__/" >> .gitignore
#echo "*.pyc" >> .gitignore
#echo ".DS_Store" >> .gitignore

# Add all files to staging area
git add .

# Make your first commit
git commit -m "Initial commit: Add LangChain security analyzer"

# Create and switch to main branch (if not already on main)
git branch -M main

# Push to GitHub repository
git push -u origin main

# Verify the remote is set correctly
git remote -v

