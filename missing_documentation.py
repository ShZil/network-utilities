import ast
import os
directory = "./Scanner"

def extract_from_files(directory):
    py_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))

    results = []
    for file_path in py_files:
        results.extend(extract_missing_docstrings(file_path))

    return results

def extract_missing_docstrings(file_path):
    places = []

    with open(file_path, 'r', encoding='utf-8') as file:
        tree = ast.parse(file.read())

    for node in ast.walk(tree):
        # Write the code that's supposed to go here
        pass

    return places


for result in extract_from_files(directory):
    print(result)
