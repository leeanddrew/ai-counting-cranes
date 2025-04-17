import argparse
import os
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="YOLOv5 training script wrapper")
    parser.add_argument('--imgsz', type=int, default=736, help='Image size')
    parser.add_argument('--epochs', type=int, default=300, help='Number of training epochs')
    parser.add_argument('--data', type=str, required=True, help='Path to data.yaml')
    parser.add_argument('--batch-size', type=int, default=16, help='Batch size')
    parser.add_argument('--weights', type=str, default='yolov5x.pt', help='Pretrained weights')
    parser.add_argument('--cache', type=str, default='ram', help='Caching method (e.g., "ram", "disk", or "")')
    parser.add_argument('--device', type=str, default='cpu', help='CUDA device (e.g., "0" or "cpu")')
    parser.add_argument('--name', type=str, default='exp', help='Run name inside the project folder')
    parser.add_argument('--project', type=str, default='yolo-mlops', help='W&B project name and training log folder')
    parser.add_argument('--entity', type=str, default=None, help='W&B entity/team name (optional)')
    return parser.parse_args()

def main():
    args = parse_args()

    root = Path(__file__).resolve().parents[1]
    yolo_train = root / "yolov5" / "train.py"

    assert yolo_train.exists(), "YOLOv5 train.py not found — did you clone YOLOv5 into your project root?"

    # Build the training command
    cmd = f"""
    python {yolo_train} --imgsz {args.imgsz} --epochs {args.epochs} --data {args.data} \\
    --batch-size {args.batch_size} --weights {args.weights} --cache {args.cache} \\
    --device {args.device} --project {args.project} --name {args.name}
    """

    # Only add --entity if provided
    if args.entity:
        cmd += f" --entity {args.entity}"

    print(f"Running command:\n{cmd}")
    os.system(cmd)


if __name__ == "__main__":
    main()
