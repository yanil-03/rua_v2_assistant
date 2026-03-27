import os

# Project structure definition
structure = {
    "rua_project": {
        "main.py": "",
        "utils.py": "",
        "modules": {
            "__init__.py": "",
            "wake_word.py": "",
            "ear.py": "",
            "brain.py": "",
            "memory.py": "",
            "voice.py": ""
        }
    }
}


def create_structure(base_path, tree):
    for name, content in tree.items():
        path = os.path.join(base_path, name)

        if isinstance(content, dict):
            # Create directory
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            # Create file
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)


if __name__ == "__main__":
    create_structure(".", structure)
    print("✅ RUA project structure created successfully!")