import os
import shutil

# Dataset 1 and Dataset 2 paths
dataset1 = r'C:\Users\cedga\Desktop\Baigiamo_duomenys\150mb' 
dataset2 = r'C:\Users\cedga\Desktop\Baigiamo_duomenys\520mb\Vest_hardhat'
merged = r'C:\Users\cedga\Desktop\Baigiamo_duomenys\merged_dataset'

# Subfolders to merge
splits = ['train', 'valid', 'test']

for split in splits:
    for t in ['images', 'labels']:
        src1 = os.path.join(dataset1, split, t)
        src2 = os.path.join(dataset2, split, t)
        dst = os.path.join(merged, t, split)
        os.makedirs(dst, exist_ok=True)

        for folder in [src1, src2]:
            if os.path.exists(folder):
                for file in os.listdir(folder):
                    src_file = os.path.join(folder, file)
                    dst_file = os.path.join(dst, file)
                    if not os.path.exists(dst_file):  # avoid overwriting
                        shutil.copy2(src_file, dst_file)
