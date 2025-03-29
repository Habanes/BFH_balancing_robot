import os

def generate_directory_structure(root_dir, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for root, dirs, files in os.walk(root_dir):
            # Skip hidden folders
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            level = root.replace(root_dir, '').count(os.sep)
            indent = ' ' * 4 * level
            f.write(f"{indent}{os.path.basename(root)}/\n")
            sub_indent = ' ' * 4 * (level + 1)
            for file in files:
                if not file.startswith('.'):
                    f.write(f"{sub_indent}{file}\n")

def get_parent_directory(path, levels_up):
    for _ in range(levels_up):
        path = os.path.dirname(path)
    return path

def main(levels_up=2):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = get_parent_directory(current_dir, levels_up)
    output_file = os.path.join(current_dir, "directory_structure.txt")
    generate_directory_structure(root_dir, output_file)
    print(f"Directory structure saved to {output_file}")

if __name__ == "__main__":
    main(levels_up=0)  # You can change this value
