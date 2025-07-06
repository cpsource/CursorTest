Yes, you can import code from another Jupyter notebook! Here are the main ways:

**Method 1: Convert to .py file (easiest)**
```python
# Save your other notebook as a .py file, then:
import my_other_notebook
# or
from my_other_notebook import my_function, my_variable
```

**Method 2: Use nbimporter (import .ipynb directly)**
```python
# Install: pip install nbimporter
import nbimporter
import my_notebook  # imports my_notebook.ipynb
```

**Method 3: Manual import using importlib**
```python
import importlib.util
import sys

# Load the notebook as a module
spec = importlib.util.spec_from_file_location("my_module", "/path/to/notebook.py")
my_module = importlib.util.module_from_spec(spec)
sys.modules["my_module"] = my_module
spec.loader.exec_module(my_module)

# Now use it
my_module.my_function()
```

**Method 4: Use %run magic command**
```python
# This executes the entire notebook in your current namespace
%run ./my_other_notebook.ipynb
# Now all variables/functions from that notebook are available
```

**Best practice example:**
```python
# In notebook A, save as "helper_functions.py"
def process_data(data):
    return data * 2

MODEL_NAME = "gpt-4"
```

```python
# In notebook B
from helper_functions import process_data, MODEL_NAME

result = process_data([1, 2, 3])
print(f"Using model: {MODEL_NAME}")
```

**Python analogy**: It's like having a toolbox (another notebook) and bringing specific tools into your current workspace, rather than carrying the whole toolbox around.

The `.py` conversion method is most reliable and follows standard Python import conventions.

