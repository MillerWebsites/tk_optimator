import os
import nbformat as nbf
from nbformat.v4 import new_notebook, new_code_cell
from typing import List

def combine_py_files_to_notebook(directory_path: str, output_file: str) -> None:
    """Combine multiple .py files into one Jupyter notebook."""
    # Create a new notebook
    nb = new_notebook()
    
    # Iterate through all .py files in the directory
    for filename in sorted(os.listdir(directory_path)):
        if filename.endswith('.py'):
            file_path = os.path.join(directory_path, filename)
            
            # Read the content of the .py file
            with open(file_path, 'r') as file:
                content = file.read()
            
            # Create a new code cell with the file content
            cell_content = f"# {filename}\n\n{content}"
            cell = new_code_cell(cell_content)
            
            # Add the cell to the notebook
            nb.cells.append(cell)
    
    # Write the notebook to a file
    with open(output_file, 'w') as f:
        nbf.write(nb, f, version=4)

def process_files(input_files: List[str], output_file: str) -> None:
    """Combine multiple .py files into one Jupyter notebook."""
    nb = new_notebook()
    
    for file_path in input_files:
        if os.path.isfile(file_path) and file_path.endswith('.py'):
            with open(file_path, 'r') as file:
                content = file.read()
            
            filename = os.path.basename(file_path)
            cell_content = f"# {filename}\n\n{content}"
            cell = new_code_cell(cell_content)
            nb.cells.append(cell)
    
    with open(output_file, 'w') as f:
        nbf.write(nb, f, version=4)

if __name__ == "__main__":
    import sys
    import argparse
    import os

    parser = argparse.ArgumentParser(description='Combine Python files into a Jupyter notebook')
    parser.add_argument('-o', '--output_file', help='Output notebook file', default=None)
    parser.add_argument('-i', '--input_files', nargs='*', help='Input Python files or directory', default=['.'])
    args = parser.parse_args()

    if len(args.input_files) == 1 and os.path.isdir(args.input_files[0]):
        input_dir = args.input_files[0]
    else:
        input_dir = os.getcwd()

    if args.output_file is None:
        output_file = f"{os.path.basename(input_dir)}.ipynb"
    else:
        output_file = args.output_file

    if len(args.input_files) == 1 and os.path.isdir(args.input_files[0]):
        combine_py_files_to_notebook(input_dir, output_file)
    else:
        process_files(args.input_files, output_file)

    print(f"Notebook '{output_file}' has been created successfully.")