import subprocess
import os
from pathlib import Path

def run_training(epochs=50, img_size=640, batch_size=16, model_weights="yolov5s.pt"):
    """
    Run YOLO training after the dataset is split.
    
    :param output_dir: Path to the directory containing the data.yaml.
    :param epochs: Number of epochs for training.
    :param img_size: Image size for training.
    :param batch_size: Batch size for training.
    :param model_weights: Pre-trained model weights to use (YOLOv5 or YOLOv8).
    """
    # Path to the data.yaml
    data_yaml_path = Path(__file__).parent.parent.joinpath("dataset", "data.yaml").as_posix()

    # Check if YOLOv5 or YOLOv8 should be used
    if os.path.exists('yolov5'):
        # Run YOLOv5 training
        print("Running YOLOv5 training...")
        subprocess.run([
            'python', 'yolov5/train.py',
            '--img', str(img_size),
            '--batch', str(batch_size),
            '--epochs', str(epochs),
            '--data', data_yaml_path,
            '--weights', model_weights
        ])
    else:
        # Run YOLOv8 training
        print("Running YOLOv8 training...")
        subprocess.run([
            'yolo', 'task=detect', 'mode=train',
            f'model={model_weights}', f'data={data_yaml_path}',
            f'epochs={epochs}', f'imgsz={img_size}'
        ])

if __name__ == '__main__':
    run_training()