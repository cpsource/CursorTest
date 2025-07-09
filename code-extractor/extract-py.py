# Simple Python script to extract code from notebooks
import json
import sys

def extract_code_from_notebook(notebook_path, output_path):
    with open(notebook_path, 'r') as f:
        nb = json.load(f)
    
    code_cells = []
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            code_cells.append(''.join(cell['source']))
    
    with open(output_path, 'w') as f:
        f.write('\n\n'.join(code_cells))

# Usage: python extract_code.py notebook.ipynb output.py
extract_code_from_notebook(sys.argv[1], sys.argv[2])

