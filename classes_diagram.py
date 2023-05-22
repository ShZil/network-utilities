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
                    method_name = subnode.name
                    method_docstring = ast.get_docstring(subnode) or ''
                    method_args = []
                    method_type_hints = dict()

                    for arg in subnode.args.args:
                        arg_name = arg.arg
                        method_args.append(arg_name)

                        if arg.annotation:
                            arg_type_hint = ast.unparse(arg.annotation).strip()
                            method_type_hints[arg_name] = arg_type_hint

                    method_data = {
                        'name': method_name,
                        'docstring': method_docstring,
                        'args': method_args,
                        'type_hints': method_type_hints
                    }

                    methods.append(method_data)
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

with open('classes_diagram_result.py', 'w', encoding='utf-8') as file:
    for class_data in classes:
        name = class_data['name']
        superclass = class_data['superclass']
        docstring = class_data['docstring']
        methods = class_data['methods']
        fields = class_data['fields']

        superclass = f"({superclass})" if superclass else ''
        class_declaration = f"class {name}{superclass}:"
        docstring = f'    """\n    {docstring}\n    """'

        methods_code = []
        for method_data in methods:
            method_name = method_data['name']
            method_docstring = method_data['docstring']
            method_args = [f"{arg}: {method_data['type_hints'][arg]}" if arg in method_data['type_hints'] else arg for arg in method_data['args']]
            method_args = ', '.join(method_args)


            method_declaration = f"    def {method_name}({method_args})"
            if method_docstring != '':
                method_docstring = f'        """\n        {method_docstring}\n        """'

            methods_code.append(f"{method_declaration}:")
            if method_docstring:
                methods_code.append(method_docstring)
            methods_code.append('        pass\n')

        fields_code = []
        for field in fields:
            fields_code.append(f"    {field} = ...")

        class_code = '\n'.join([class_declaration, docstring] + methods_code + fields_code)
        file.write(class_code + '\n\n')
