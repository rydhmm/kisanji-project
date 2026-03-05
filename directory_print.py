from pathlib import Path

# 1. SET YOUR PATH HERE
# We use r"..." so Python treats backslashes correctly
directory_path = r"C:\app_fron"

def tree(directory, prefix=''):
    path_obj = Path(directory)
    
    # Check if the path actually exists
    if not path_obj.exists():
        print(f"Directory not found: {directory}")
        return

    # Sort items: directories first, then files
    try:
        items = sorted(path_obj.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
    except PermissionError:
        print(f"{prefix}└── [Access Denied]")
        return

    total_items = len(items)
    
    for index, item in enumerate(items):
        is_last = (index == total_items - 1)
        connector = '└── ' if is_last else '├── '
        
        print(f"{prefix}{connector}{item.name}")
        
        if item.is_dir():
            extension = '    ' if is_last else '│   '
            tree(item, prefix + extension)

# Run the function
print(f"Directory Tree for: {directory_path}")
tree(directory_path)