import os
import nbformat as nbf
from nbformat.v4 import new_notebook, new_code_cell

def combine_py_files_to_notebook(directory_path, output_file):
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
        nbf.write(nb, f)
    
    def process_files(input_files, output_file):
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
            nbf.write(nb, f)
    
    if __name__ == "__main__":
        import sys
        
        if len(sys.argv) < 2:
            print("Usage: python combine_py_files_to_new_notebook.py <input_file1> [input_file2 ...] <output_file>")
            sys.exit(1)
        
        output_file = sys.argv[-1]
        input_files = sys.argv[1:-1]
        
        if len(input_files) == 1 and os.path.isdir(input_files[0]):
            combine_py_files_to_notebook(input_files[0], output_file)
        else:
            process_files(input_files, output_file)
        
        print(f"Notebook '{output_file}' has been created successfully.")
    
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
        nbf.write(nb, f)

# Usage
directory_path = '.'  # Current directory, change this if needed
output_file = 'combined_scripts.ipynb'

combine_py_files_to_notebook(directory_path, output_file)
print(f"Notebook '{output_file}' has been created successfully.")