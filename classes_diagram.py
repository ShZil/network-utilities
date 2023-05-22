import os
import ast

def extract_classes(file_path):
    classes = []

    with open(file_path, 'r', encoding='utf-8') as file:
        tree = ast.parse(file.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            superclass = ''
            if node.bases:
                superclass = node.bases[0].id
            docstring = ast.get_docstring(node) or ''
            methods = []
            fields = []

            for subnode in node.body:
                if isinstance(subnode, ast.FunctionDef):
                    methods.append(subnode.name)
                elif isinstance(subnode, ast.Assign):
                    field_name = subnode.targets[0].id
                    fields.append(field_name)

            class_data = {
                'name': class_name,
                'superclass': superclass,
                'docstring': docstring,
                'methods': methods,
                'fields': fields
            }

            classes.append(class_data)

    return classes

def extract_classes_from_files(directory):
    py_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                py_files.append(os.path.join(root, file))

    classes = []
    for file_path in py_files:
        classes.extend(extract_classes(file_path))

    return classes


directory = "./Scanner"
classes = extract_classes_from_files(directory)

open('classes_diagram.py', 'w', encoding='utf-8').close()

for class_data in classes:
    name, superclass, docstring, methods, fields = class_data['name'], class_data['superclass'], class_data['docstring'], '\n'.join(class_data['methods']), '\n'.join(class_data['fields'])
    superclass = f"({superclass})" if len(superclass) > 0 else ''
    methods = "# Methods:\n" + methods if len(methods) > 0 else ''
    fields = "# Fields:\n" + fields if len(fields) > 0 else ''
    print(f"""
    class {name}{superclass}:
        \"\"\"
        {docstring}
        \"\"\"

        {methods}
        {fields}
    \n\n
    """, file=open('classes_diagram_result.py', 'a', encoding='utf-8'))
