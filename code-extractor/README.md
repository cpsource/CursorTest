# JupyterLab Code Extractor Extension

A JupyterLab extension that extracts code blocks from the currently open notebook and saves them to a Python file with the same name.

## Features

- 🔍 Scans the currently open Jupyter notebook
- 📝 Extracts all code cells (ignoring markdown and raw cells)
- 💾 Saves extracted code to a `.py` file with the same name as the notebook
- 🏷️ Adds cell numbers as comments for easy reference
- 🎨 Integrates with JupyterLab's command palette and launcher

## Installation

### Development Installation

1. **Clone and setup the project:**
```bash
git clone https://github.com/your-username/code-extractor.git
cd code-extractor
```

2. **Install Python dependencies:**
```bash
pip install -e .
```

3. **Install Node.js dependencies:**
```bash
npm install
# or
jlpm install
```

4. **Build the extension:**
```bash
jlpm run build
```

5. **Install the extension in JupyterLab:**
```bash
jupyter labextension develop . --overwrite
```

6. **Enable the server extension:**
```bash
jupyter server extension enable code_extractor
```

### Production Installation

Once published to PyPI:
```bash
pip install code-extractor
```

## Usage

### Method 1: Command Palette
1. Open a Jupyter notebook in JupyterLab
2. Press `Ctrl+Shift+C` (or `Cmd+Shift+C` on Mac) to open the command palette
3. Type "Export Code to Python File" and select it
4. The code will be extracted and saved as `notebook_name.py`

### Method 2: Launcher
1. Open the JupyterLab launcher
2. Look for "Export Code to Python File" in the "Code Tools" section
3. Click it to extract code from the currently active notebook

## How It Works

The extension:
1. **Scans** the currently open notebook file
2. **Identifies** all code cells (skips markdown, raw, and empty cells)
3. **Extracts** the code content from each cell
4. **Formats** the output with cell numbers as comments
5. **Saves** to a Python file in the same directory as the notebook

### Example Output

If you have a notebook `data_analysis.ipynb` with these cells:

**Cell 1 (Code):**
```python
import pandas as pd
import numpy as np
```

**Cell 2 (Markdown):**
```markdown
# Data Loading
```

**Cell 3 (Code):**
```python
df = pd.read_csv('data.csv')
df.head()
```

The extension will create `data_analysis.py`:
```python
#!/usr/bin/env python3
"""
Code extracted from Jupyter notebook
Generated automatically by code-extractor extension
"""

==================================================
# Cell 1
import pandas as pd
import numpy as np

==================================================
# Cell 3
df = pd.read_csv('data.csv')
df.head()

==================================================
```

## Development

### Project Structure
```
code-extractor/
├── src/
│   ├── index.ts          # Main extension logic
│   └── handler.ts        # API helper functions
├── code_extractor/
│   ├── __init__.py       # Python package init
│   └── handlers.py       # Server-side handlers
├── package.json          # Node.js dependencies
├── setup.py             # Python package setup
└── README.md            # This file
```

### Building and Testing

```bash
# Build the extension
jlpm run build

# Watch for changes during development
jlpm run watch

# Clean build artifacts
jlpm run clean

# Lint the code
jlpm run eslint
```

### Rebuilding After Changes

```bash
# After making changes to TypeScript files
jlpm run build
jupyter labextension develop . --overwrite

# After making changes to Python files
pip install -e .
```

## Technical Details

### Frontend (TypeScript)
- Uses `@jupyterlab/notebook` to access the current notebook
- Extracts code from cells using the notebook model
- Sends extracted code to the backend via REST API

### Backend (Python)
- Tornado-based request handler
- Receives code blocks and filename from frontend
- Writes formatted Python file to disk
- Returns success/error status

### API Endpoint
- **POST** `/code-extractor/export-code`
- **Body:** `{filename: string, code_blocks: string[]}`
- **Response:** `{status: string, message: string, path: string}`

## Troubleshooting

### Extension Not Loading
```bash
# Check if extension is installed
jupyter labextension list

# Check if server extension is enabled
jupyter server extension list

# Restart JupyterLab
jupyter lab --reload
```

### Build Errors
```bash
# Clear cache and rebuild
jlpm run clean:all
jlpm install
jlpm run build
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

