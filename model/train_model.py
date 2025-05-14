from ultralytics import YOLO
import torch
import os


# print(torch.cuda.is_available())  # Check if CUDA is available
# print(torch.cuda.get_device_name(0))  # Print the current CUDA device

# model = YOLO('yolov8n.yaml')  # Load a pretrained YOLOv8 model

# results = model.train(data='model\config.yaml', epochs=10, device = 0)  # Train the model on the dataset

def main():
    # Load the model (can be from .yaml or .pt file)
    model = YOLO('yolov8n.yaml')  # or use 'yolov8n.pt' for pretrained

    # Absolute path to your config (optional but safer)
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')

    # Train using GPU (device=0)
    results = model.train(
        data=config_path,
        epochs=10,
        device=0
    )

if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()  # helps on Windows
    main()