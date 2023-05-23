import zipfile

def generate_treeview(zip_path):
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        tree = {}
        for file in zip_file.namelist():
            parts = file.split('/')
            current_level = tree
            for part in parts:
                if part not in current_level:
                    current_level[part] = {}
                current_level = current_level[part]

        _print_tree(tree)

def _print_tree(tree, indent=''):
    for key in tree:
        print(indent + '|-- ' + key)
        if tree[key]:
            _print_tree(tree[key], indent + '    ')

# Usage example
generate_treeview('example.zip')
