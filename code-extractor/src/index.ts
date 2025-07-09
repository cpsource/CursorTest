import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ICommandPalette } from '@jupyterlab/apputils';

import { INotebookTracker } from '@jupyterlab/notebook';

import { requestAPI } from './handler';

import { ILauncher } from '@jupyterlab/launcher';

/**
 * The command IDs used by the extension.
 */
namespace CommandIDs {
  export const exportCode = 'code-extractor:export';
}

/**
 * Initialization data for the code-extractor extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'code-extractor:plugin',
  autoStart: true,
  requires: [ICommandPalette, INotebookTracker],
  optional: [ILauncher],
  activate: (
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    notebookTracker: INotebookTracker,
    launcher: ILauncher | null
  ) => {
    console.log('JupyterLab extension code-extractor is activated!');

    // Add command to extract code
    const { commands } = app;
    
    commands.addCommand(CommandIDs.exportCode, {
      label: 'Export Code to Python File',
      execute: async () => {
        const current = notebookTracker.currentWidget;
        
        if (!current) {
          console.error('No notebook is currently open');
          return;
        }

        const notebook = current.content;
        const notebookModel = current.context.model;
        
        if (!notebookModel) {
          console.error('No notebook model available');
          return;
        }

        // Get the notebook filename without extension
        const notebookPath = current.context.path;
        const notebookName = notebookPath.split('/').pop()?.replace('.ipynb', '') || 'untitled';
        
        // Extract code cells
        const codeCells: string[] = [];
        const cells = notebook.model?.cells;
        
        if (cells) {
          for (let i = 0; i < cells.length; i++) {
            const cell = cells.get(i);
            if (cell.type === 'code') {
              const source = cell.value.text;
              if (source.trim()) {
                codeCells.push(`# Cell ${i + 1}\n${source}\n`);
              }
            }
          }
        }

        if (codeCells.length === 0) {
          console.warn('No code cells found in the notebook');
          return;
        }

        // Send to backend to write file
        try {
          const response = await requestAPI<any>('export-code', {
            method: 'POST',
            body: JSON.stringify({
              filename: `${notebookName}.py`,
              code_blocks: codeCells
            })
          });
          
          console.log('Code exported successfully:', response);
          
          // Show success message
          const message = `Code exported to ${notebookName}.py`;
          app.commands.execute('apputils:notify', {
            message: message,
            type: 'success'
          });
          
        } catch (error) {
          console.error('Error exporting code:', error);
          app.commands.execute('apputils:notify', {
            message: 'Error exporting code',
            type: 'error'
          });
        }
      }
    });

    // Add command to palette
    palette.addItem({
      command: CommandIDs.exportCode,
      category: 'Code Tools'
    });

    // Add to launcher if available
    if (launcher) {
      launcher.add({
        command: CommandIDs.exportCode,
        category: 'Code Tools',
        rank: 1
      });
    }
  }
};

export default plugin;
