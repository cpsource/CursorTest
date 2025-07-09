import json
import os
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado
from tornado.web import RequestHandler


class CodeExportHandler(APIHandler):
    """Handler for exporting code from notebooks to Python files."""
    
    @tornado.web.authenticated
    def post(self):
        """Export code blocks to a Python file."""
        try:
            # Parse the request data
            data = json.loads(self.request.body)
            filename = data.get('filename', 'exported_code.py')
            code_blocks = data.get('code_blocks', [])
            
            if not code_blocks:
                self.set_status(400)
                self.finish(json.dumps({'error': 'No code blocks provided'}))
                return
            
            # Get the current working directory (where Jupyter is running)
            current_dir = os.getcwd()
            output_path = os.path.join(current_dir, filename)
            
            # Create the Python file content
            python_content = self._create_python_file_content(code_blocks)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(python_content)
            
            # Return success response
            self.finish(json.dumps({
                'status': 'success',
                'message': f'Code exported to {filename}',
                'path': output_path,
                'blocks_exported': len(code_blocks)
            }))
            
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({'error': str(e)}))
    
    def _create_python_file_content(self, code_blocks):
        """Create the content for the Python file."""
        header = '''#!/usr/bin/env python3
"""
Code extracted from Jupyter notebook
Generated automatically by code-extractor extension
"""

'''
        
        # Join all code blocks with separators
        separator = '\n' + '='*50 + '\n'
        content = header + separator.join(code_blocks)
        
        return content


def setup_handlers(web_app):
    """Setup the API handlers."""
    host_pattern = ".*$"
    base_url = web_app.settings["base_url"]
    
    # Define the route pattern
    route_pattern = url_path_join(base_url, "code-extractor", "export-code")
    
    # Add the handler
    handlers = [(route_pattern, CodeExportHandler)]
    web_app.add_handlers(host_pattern, handlers)

