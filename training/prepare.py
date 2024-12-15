import os
import shutil
import random
import yaml
import xml.etree.ElementTree as ET
from pathlib import Path

def create_data_splits(image_dir, annotation_dir, output_dir, val_ratio=0.1, test_ratio=0.1):
    """
    Split the images and annotations into training, validation, and test sets.
    
    :param image_dir: Path to the directory containing images.
    :param annotation_dir: Path to the directory containing annotations.
    :param output_dir: Path to the output directory where the new sets will be created.
    :param val_ratio: Proportion of the data to be used for validation.
    :param test_ratio: Proportion of the data to be used for testing.
    """
    # Create the output directories for train, val, and test sets
    sets = ['train', 'val', 'test']
    for set_name in sets:
        os.makedirs(os.path.join(output_dir, 'images', set_name), exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'labels', set_name), exist_ok=True)

    # Get the list of image and annotation files
    image_files = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    # Shuffle the image files to randomize the selection
    random.shuffle(image_files)

    # Calculate split sizes
    total_files = len(image_files)
    test_size = int(total_files * test_ratio)
    val_size = int(total_files * val_ratio)
    train_size = total_files - val_size - test_size

    # Split the files
    train_files = image_files[:train_size]
    val_files = image_files[train_size:train_size + val_size]
    test_files = image_files[train_size + val_size:]

    # Helper function to copy files
    def copy_files(file_list, set_name):
        for file in file_list:
            # Copy image
            image_path = os.path.join(image_dir, file)
            shutil.copy(image_path, os.path.join(output_dir, 'images', set_name, file))

            # Copy corresponding annotation
            annotation_file = file.replace('.jpg', '.txt').replace('.jpeg', '.txt').replace('.png', '.txt')
            annotation_path = os.path.join(annotation_dir, annotation_file)
            if os.path.exists(annotation_path):
                shutil.copy(annotation_path, os.path.join(output_dir, 'labels', set_name, annotation_file))
            else:
                print(f"Warning: No annotation found for {file}")

    # Copy the files to respective directories
    copy_files(train_files, 'train')
    copy_files(val_files, 'val')
    copy_files(test_files, 'test')

    print(f"Data split completed: {len(train_files)} training, {len(val_files)} validation, {len(test_files)} testing.")

def load_classes_from_xml(xml_file):
    """Load classes and their colors from an XML file."""
    if not os.path.exists(xml_file):
        raise FileNotFoundError(xml_file)

    class_names = []
    tree = ET.parse(xml_file)
    root = tree.getroot()
    for cls in root.findall("class"):
        class_name = cls.get("name")
        if class_name:
            class_names.append(class_name)
    return class_names

def create_data_yaml(output_dir, class_names):
    image_dir = Path(output_dir).joinpath("images")

    data = {
        'train': image_dir.joinpath("train").as_posix(),
        'val': image_dir.joinpath("val").as_posix(),
        'test': image_dir.joinpath("test").as_posix(),
        'nc': len(class_names),
        'names': class_names
    }

    # Save the data.yaml to the specified output directory
    with open(os.path.join(output_dir, 'data.yaml'), 'w') as file:
        yaml.dump(data, file, default_flow_style=False, indent=2)

if __name__ == '__main__':
    image_directory = Path(__file__).parent.joinpath("images").as_posix()
    annotation_directory = Path(__file__).parent.joinpath("labels").as_posix()
    output_directory = Path(__file__).parent.parent.joinpath("dataset").as_posix()

    create_data_splits(image_directory, annotation_directory, output_directory)
    create_data_yaml(Path(__file__).parent.parent.joinpath("dataset").as_posix(),
                     load_classes_from_xml(
                         Path(__file__).parent.joinpath("labels", "classes.xml").as_posix()))