import ast
import os
from time import sleep

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
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if not ast.get_docstring(node):
                place = get_place(file_path, node)
                places.append(place)

        elif isinstance(node, ast.Module):
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and not ast.get_docstring(item):
                    place = get_place(file_path, item)
                    places.append(place)

    return set(places)


def get_place(file_path, node):
    file_name = os.path.basename(file_path)
    module_name = file_name.split(".")[0]
    module_path = os.path.dirname(file_path)
    place = os.path.join(module_path, file_name)[len(directory)+1:]

    if isinstance(node, ast.FunctionDef):
        place += f":{node.name}"
    elif isinstance(node, ast.ClassDef):
        place += f":{node.name}:{node.name}"

    return place

while True:
    sleep(10)
    with open('missing_documentation.txt', 'w', encoding='utf-8') as f:
        for result in extract_from_files(directory):
            print(result, file=f)
