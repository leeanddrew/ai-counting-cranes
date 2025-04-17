# main.py

import os
import sys

# Ensure yolov5 is added to sys.path BEFORE SAHI is imported
yolov5_path = os.path.abspath("yolov5")
if yolov5_path not in sys.path:
    sys.path.insert(0, yolov5_path)

# Now that yolov5 is importable, we can safely import inference code
from src import infer

if __name__ == "__main__":
    infer.run()
