import os
import sys
import cv2
from pathlib import Path
from PIL import Image as PImage, ImageDraw, ImageFont
from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction
from sahi.utils.cv import read_image
import argparse

def convert_to_yolo_format(bbox, iw=736, ih=736):
    x_min, y_min, width, height = bbox
    x_center = x_min + (width / 2)
    y_center = y_min + (height / 2)
    return [x_center / iw, y_center / ih, width / iw, height / ih]


def write_yolo_boxes_to_file(img_width, img_height, yolo_boxes, filename):
    with open(filename, 'w') as file:
        for box in yolo_boxes:
            yolo_box = convert_to_yolo_format(bbox=box[1:], iw=img_width, ih=img_height)
            file.write(f"{box[0]} {' '.join(map(str, yolo_box))}\n")


def sahi_inference(
    detection_model,
    slice_heights,
    slice_widths,
    image_dir,
    label_dir=None,
    predict_dir="predictions",
    predict_annot_dir="annotations",
    image_format=".jpg",
    img_height=736,
    img_width=736,
    overlap_height_ratio=0.2,
    overlap_width_ratio=0.2,
    font_path="Arial_Bold.ttf"
):
    os.makedirs(predict_dir, exist_ok=True)
    os.makedirs(predict_annot_dir, exist_ok=True)

    gt_b, gt_d, pr_b, pr_d, image_name = [], [], [], [], []

    image_files = sorted([f for f in os.listdir(image_dir) if f.endswith(image_format)])
    if len(slice_heights) == 1: slice_heights *= len(image_files)
    if len(slice_widths) == 1: slice_widths *= len(image_files)

    for idx, filename in enumerate(image_files):
        image_path = os.path.join(image_dir, filename)
        result = get_sliced_prediction(
            image_path,
            detection_model,
            slice_height=slice_heights[idx],
            slice_width=slice_widths[idx],
            overlap_height_ratio=overlap_height_ratio,
            overlap_width_ratio=overlap_width_ratio,
        )
        # Step 1: Save predicted image with bounding boxes using SAHI
        result.export_visuals(
            file_name=filename[:-4],
            export_dir=predict_dir,
            hide_labels=True,
            rect_th=1
        )

        # Step 2: Save YOLO-format annotations
        coco_annot = result.to_coco_annotations()
        yolo_boxes = [[i['category_id'], *i['bbox']] for i in coco_annot]
        write_yolo_boxes_to_file(
            img_width,
            img_height,
            yolo_boxes,
            os.path.join(predict_annot_dir, filename[:-4] + ".txt")
        )

        # Step 3: Count predictions
        pred_duck = sum(1 for obj in result.object_prediction_list if obj.category.id == 0)
        pred_crane = sum(1 for obj in result.object_prediction_list if obj.category.id == 1)

        # Step 4: Open predicted image and overlay counts
        pred_image_path = os.path.join(predict_dir, filename[:-4] + ".png")
        pred_image = PImage.open(pred_image_path).convert("RGB")
        draw_pred = ImageDraw.Draw(pred_image)
        font = ImageFont.truetype(font_path, 15)

        draw_pred.text((0, 0), f"Pred Crane:{pred_crane}", font=font, fill='yellow')
        draw_pred.text((0, 20), f"Pred Duck:{pred_duck}", font=font, fill='yellow')

        # Step 5: Overwrite original image with final one (boxes + counts)
        pred_image.save(pred_image_path)
        print(f"✓ Saved prediction image with boxes + counts: {pred_image_path}")

        # Step 6: Store prediction/GT counts (if GT is used elsewhere)
        gt_duck, gt_crane = 0, 0
        label_path = os.path.join(label_dir, filename[:-4]+".txt") if label_dir else None
        if label_path and os.path.isfile(label_path):
            with open(label_path, 'r') as file:
                for line in file:
                    if line.startswith("0"): gt_duck += 1
                    elif line.startswith("1"): gt_crane += 1

    gt_b.append(gt_crane)
    gt_d.append(gt_duck)
    pr_b.append(pred_crane)
    pr_d.append(pred_duck)
    image_name.append(filename)


    return gt_b, gt_d, pr_b, pr_d, image_name


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run SAHI inference with configurable parameters.")

    parser.add_argument("--image_dir", type=str,default="../sample_inference/images", help="Path to directory with input images")
    parser.add_argument("--predict_dir", type=str, default="../sample_inference/predictions", help="Directory to save prediction images")
    parser.add_argument("--predict_annot_dir", type=str, default="../sample_inference/raw_predictions", help="Directory to save YOLO-format prediction labels")
    parser.add_argument("--slice_heights", type=int, nargs='+', default=[736], help="Slice heights (can be multiple)")
    parser.add_argument("--slice_widths", type=int, nargs='+', default=[736], help="Slice widths (can be multiple)")
    parser.add_argument("--confidence", type=float, default=0.2, help="Confidence threshold for predictions")
    parser.add_argument("--model_path", type=str, default="../yolo-birds/exp/weights/best.pt", help="Path to trained YOLO model")
    parser.add_argument("--image_format", type=str, default=".jpg", help="Image file extension")
    parser.add_argument("--device",type=str,default="cpu",help="Device to make inference on")
    parser.add_argument("--font_path", type=str, default="../Arial_Bold.ttf", help="Path to .ttf font for overlay text")

    args = parser.parse_args()

    detection_model = AutoDetectionModel.from_pretrained(
    model_type='yolov5',
    model_path=args.model_path,
    confidence_threshold=args.confidence,
    device=args.device,
    )

    sahi_inference(
        detection_model=detection_model,
        slice_heights=args.slice_heights,
        slice_widths=args.slice_widths,
        image_dir=args.image_dir,
        predict_dir=args.predict_dir,
        predict_annot_dir=args.predict_annot_dir,
        image_format=args.image_format,
        font_path=args.font_path
    )
