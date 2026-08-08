import ast
import sys
import os

def findVersion(repo_name):
    # Python package directories use underscores instead of hyphens
    package_dir = repo_name.replace('-', '_')
    file_path = os.path.join(package_dir, "__init__.py")

    if not os.path.exists(file_path):
        print(f"Error: Expected file at {file_path} does not exist.", file=sys.stderr)
        return None

    with open(file_path, "r") as f:
        tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__version__":
                        # Extract and return the string value
                        return node.value.s if hasattr(node.value, "s") else node.value.value

    return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Repository name argument is missing.", file=sys.stderr)
        sys.exit(1)

    repo_name = sys.argv[1]
    version = findVersion(repo_name)

    if version:
        print(version)
        sys.exit(0)
    else:
        print(f"Could not find __version__ string inside {repo_name}/__init__.py", file=sys.stderr)
        sys.exit(1)
