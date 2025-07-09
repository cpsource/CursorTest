"""
JupyterLab Code Extractor Extension
"""

from .handlers import setup_handlers

__version__ = "0.1.0"


def _jupyter_labextension_paths():
    """Return metadata for the JupyterLab extension."""
    return [{
        "src": "labextension",
        "dest": "code-extractor"
    }]


def _jupyter_server_extension_points():
    """Return metadata for the Jupyter server extension."""
    return [{
        "module": "code_extractor"
    }]


def _load_jupyter_server_extension(server_app):
    """Load the Jupyter server extension."""
    setup_handlers(server_app.web_app)
    server_app.log.info("Registered code-extractor extension")

