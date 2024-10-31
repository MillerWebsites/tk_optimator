import os
import nbformat as nbf
from nbformat.v4 import new_notebook, new_code_cell
from typing import List

def combine_py_files_to_notebook(directory_path: str, output_file: str) -> None:
    """Combine multiple .py files into one Jupyter notebook."""
    # Create a new notebook
    nb = new_notebook()
    
    # Iterate through all .py files in the directory
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                # Read the content of the .py file
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Create a new code cell with the file content
                cell_content = f"# {file_path}\n\n{content}"
                cell = new_code_cell(cell_content)
                
                # Add the cell to the notebook
                nb.cells.append(cell)
    
    # Write the notebook to a file
    with open(output_file, 'w', encoding='utf-8') as f:
        nbf.write(nb, f, version=4)

if __name__ == "__main__":
    import sys
    import argparse
    import os

    parser = argparse.ArgumentParser(description='Combine Python files into a Jupyter notebook')
    parser.add_argument('-o', '--output_file', help='Output notebook file', default=None)
    args = parser.parse_args()

    input_dir = os.getcwd()

    if args.output_file is None:
        output_file = f"{os.path.basename(input_dir)}.ipynb"
    else:
        output_file = args.output_file

    combine_py_files_to_notebook(input_dir, output_file)

    print(f"Notebook '{output_file}' has been created successfully.")