# 1. Search for potential API keys in your files
echo "Searching for potential Anthropic API keys..."
grep -r "sk-ant" . --exclude-dir=.git
grep -r "ANTHROPIC_API_KEY" . --exclude-dir=.git
grep -r "api_key" . --exclude-dir=.git

echo -e "\n=== Checking for hardcoded API keys ==="
# Look for patterns that might be API keys
grep -r "sk-[a-zA-Z0-9]" . --exclude-dir=.git
grep -r "anthropic" . --exclude-dir=.git --ignore-case

echo -e "\n=== Files currently staged for commit ==="
git status

echo -e "\n=== Show what's in your staged files ==="
git diff --cached

# 2. If you find API keys, here's how to fix:

echo -e "\n=== SOLUTION STEPS ==="
echo "If you found API keys above, follow these steps:"
echo ""
echo "Step 1: Remove the problematic file from git tracking"
echo "git rm --cached filename_with_api_key"
echo ""
echo "Step 2: Add the file to .gitignore"
echo "echo 'filename_with_api_key' >> .gitignore"
echo ""
echo "Step 3: If it's a .env file, make sure it's in .gitignore"
echo "echo '.env' >> .gitignore"
echo ""
echo "Step 4: Clean the file (remove actual API key, replace with placeholder)"
echo "# Edit the file and replace real key with: your_api_key_here"
echo ""
echo "Step 5: Commit the changes"
echo "git add .gitignore"
echo "git add filename_with_cleaned_content"
echo "git commit -m 'Remove API keys and add to gitignore'"
echo ""
echo "Step 6: Try pushing again"
echo "git push -u origin main"

echo -e "\n=== Quick fix for common issues ==="
echo "# If your Python file has hardcoded API key:"
echo "# Replace lines like: api_key='sk-ant-actual-key'"
echo "# With: api_key=os.environ.get('ANTHROPIC_API_KEY')"
echo ""
echo "# Make sure .env is in .gitignore:"
echo "grep -q '.env' .gitignore || echo '.env' >> .gitignore"

