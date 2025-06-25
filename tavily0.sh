# 1. Clear pip cache
pip cache purge

# 2. Remove both Tavily packages (ignore errors if not installed)
pip uninstall tavily-python -y
pip uninstall langchain-tavily -y

# 3. Reinstall both packages
pip install tavily-python
pip install langchain-tavily

# 4. Verify installations
echo "Testing tavily-python..."
python3 -c "from tavily import TavilyClient; print('✅ tavily-python installed successfully')"

echo "Testing langchain-tavily..."
python3 -c "from langchain_tavily import TavilySearchAPIWrapper; print('✅ langchain-tavily installed successfully')" 2>/dev/null || echo "❌ langchain-tavily import failed"

