import tkinter as tk
from tkinter import filedialog, ttk
import cv2
import os
import random
import xml.etree.ElementTree as ET
from pathlib import Path

class YoloLabelingTool:
    def __init__(self, root):
        self.root = root
        self.root.title("YOLO Labeling Tool")

        # Initialize variables
        self.image_dir = None
        self.output_dir = Path(__file__).parent.joinpath("labels")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
        
        self.image_list = []
        self.current_image_idx = 0
        self.current_image = None
        self.annotations = {}
        self.class_mapping = {}
        self.drawing = False
        self.start_x, self.start_y = -1, -1
        self.end_x, self.end_y = -1, -1
        self.classes = []
        self.selected_class = tk.StringVar()
        self.class_colors = {}

        # GUI Elements
        self.canvas = tk.Canvas(root, width=800, height=600, bg="black")
        self.canvas.pack()

        self.status_label = tk.Label(root, text="Welcome! Load images to start.", anchor="w", relief=tk.SUNKEN)
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM)

        self.btn_prev_image = tk.Button(root, text="Previous Image", command=self.previous_image)
        self.btn_prev_image.pack(side=tk.LEFT, padx=5)

        self.btn_next_image = tk.Button(root, text="Next Image", command=self.next_image)
        self.btn_next_image.pack(side=tk.LEFT, padx=5)

        self.btn_save_annotations = tk.Button(root, text="Save Annotations", command=self.save_annotations)
        self.btn_save_annotations.pack(side=tk.RIGHT, padx=5)

        # Load classes and colors from XML
        self.load_classes_from_xml(os.path.join(self.output_dir, "classes.xml"))
        print(self.classes)
        self.selected_class.set(self.classes[0] if self.classes else "")

        self.class_selector = ttk.Combobox(root, values=self.classes, textvariable=self.selected_class, state="readonly")
        self.class_selector.pack(side=tk.BOTTOM, pady=5)
        self.class_selector.current(0)

        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)

        # Request image directory on launch
        self.load_images()

    def random_color(self):
        """Generate a random color."""
        return "#{:02x}{:02x}{:02x}".format(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    def set_status(self, message):
        """Display a message in the status label."""
        self.status_label.config(text=message)
    
    def load_classes_from_xml(self, xml_file):
        """Load classes and their colors from an XML file."""
        if not os.path.exists(xml_file):
            raise FileNotFoundError(xml_file)

        tree = ET.parse(xml_file)
        root = tree.getroot()
        for cls in root.findall("class"):
            class_name = cls.get("name")
            color = cls.get("color", self.random_color())  # Use provided color or generate one
            if class_name:
                self.classes.append(class_name)
                self.class_colors[class_name] = color
        self.set_status(f"Loaded {len(self.classes)} classes from XML.")

    def load_images(self):
        self.image_dir = filedialog.askdirectory(title="Select Image Directory", initialdir=os.getcwd())
        if self.image_dir:
            self.image_list = [os.path.join(self.image_dir, f) for f in os.listdir(self.image_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
            self.image_list.sort()  # Ensure consistent order
            if self.image_list:
                self.current_image_idx = 0
                self.load_current_image()
                self.set_status(f"Loaded {len(self.image_list)} images.")
            else:
                self.set_status("No valid images found in the selected directory.")
        else:
            self.set_status("No directory selected. Exiting.")
            self.root.destroy()

    def load_current_image(self):
        if self.image_list:
            self.current_image = cv2.imread(self.image_list[self.current_image_idx])
            image_path = self.image_list[self.current_image_idx]
            # Load existing annotations or initialize an empty list
            self.bboxes = self.annotations.get(image_path, [])
            self.display_image()
        else:
            self.set_status("No images loaded!")

    def display_image(self):
        if self.current_image is not None:
            # Resize image for display
            image = cv2.cvtColor(self.current_image, cv2.COLOR_BGR2RGB)
            height, width, _ = image.shape
            ratio = min(800 / width, 600 / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            resized_image = cv2.resize(image, (new_width, new_height))

            # Convert to Tkinter-compatible format
            self.tk_image = tk.PhotoImage(data=cv2.imencode('.png', resized_image)[1].tobytes())
            self.canvas.delete("all")  # Clear previous drawings
            self.canvas.create_image(400, 300, anchor=tk.CENTER, image=self.tk_image)

            # Draw existing bounding boxes
            for bbox in self.bboxes:
                x, y, w, h, class_name = bbox
                color = self.class_colors.get(class_name, "red")
                self.canvas.create_rectangle(x, y, x + w, y + h, outline=color, width=2)
                self.canvas.create_text(x + 5, y + 5, anchor="nw", text=class_name, fill=color, font=("Arial", 10, "bold"))

    def on_mouse_down(self, event):
        self.drawing = True
        self.start_x, self.start_y = event.x, event.y

    def on_mouse_up(self, event):
        if self.drawing:
            self.end_x, self.end_y = event.x, event.y
            # Normalize bounding box
            x_min = min(self.start_x, self.end_x)
            y_min = min(self.start_y, self.end_y)
            x_max = max(self.start_x, self.end_x)
            y_max = max(self.start_y, self.end_y)
            w = x_max - x_min
            h = y_max - y_min
            class_name = self.selected_class.get()
            bbox = (x_min, y_min, w, h, class_name)
            self.bboxes.append(bbox)
            self.set_status(f"Added bounding box for class '{class_name}'.")
            self.drawing = False
            self.display_image()

    def on_mouse_drag(self, event):
        if self.drawing:
            self.end_x, self.end_y = event.x, event.y
            self.display_image()
            self.canvas.create_rectangle(self.start_x, self.start_y, self.end_x, self.end_y, outline="red")

    def next_image(self):
        if self.current_image_idx < len(self.image_list) - 1:
            self.save_annotations()  # Save annotations before moving to the next image
            self.current_image_idx += 1
            self.load_current_image()
        else:
            self.set_status("No more images!")

    def previous_image(self):
        if self.current_image_idx > 0:
            self.save_annotations()  # Save annotations before moving to the previous image
            self.current_image_idx -= 1
            self.load_current_image()
        else:
            self.set_status("This is the first image!")

    def save_annotations(self):
        image_path = self.image_list[self.current_image_idx]
        self.annotations[image_path] = self.bboxes  # Persist in-memory annotations

        # Save to disk
        image_name = os.path.basename(image_path)
        
        annotation_file = os.path.join(self.output_dir, os.path.splitext(image_name)[0] + ".txt")

        height, width, _ = self.current_image.shape
        with open(annotation_file, "w") as f:
            for bbox in self.bboxes:
                x, y, w, h, class_name = bbox
                class_id = self.class_mapping.get(class_name, len(self.class_mapping))
                self.class_mapping[class_name] = class_id

                # Normalize coordinates for YOLO format
                x_center = (x + w / 2) / width
                y_center = (y + h / 2) / height
                w /= width
                h /= height

                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}\n")
        self.set_status(f"Annotations saved: {annotation_file}")


if __name__ == "__main__":
    root = tk.Tk()
    app = YoloLabelingTool(root)
    root.mainloop()