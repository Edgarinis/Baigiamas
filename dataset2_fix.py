import os

# Base path to dataset2
base_dir = r'C:\Users\cedga\Desktop\Baigiamo_duomenys\520mb\Vest_hardhat'

# Folders to process
subfolders = ['train/labels', 'valid/labels', 'test/labels']

# Mapping: Reflective Vest (1) → 7, Helmet (0) stays 0
class_map = {1: 7}

for subfolder in subfolders:
    label_dir = os.path.join(base_dir, subfolder)
    print(f"Remapping labels in: {label_dir}")

    for filename in os.listdir(label_dir):
        if not filename.endswith('.txt'):
            continue

        filepath = os.path.join(label_dir, filename) 
        with open(filepath, 'r') as f: # Open each label file
            lines = f.readlines()

        new_lines = []
        for line in lines:
            parts = line.strip().split()
            if len(parts) < 5: #Checkas ar turim kiek reik parametru
                continue
            class_id = int(parts[0])
            new_id = class_map.get(class_id, class_id)  # remap or keep as-is
            parts[0] = str(new_id)
            new_lines.append(' '.join(parts))

        with open(filepath, 'w') as f:
            f.write('\n'.join(new_lines))
