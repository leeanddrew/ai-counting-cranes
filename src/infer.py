import os
import cv2
from pathlib import Path
from PIL import Image as PImage, ImageDraw, ImageFont
from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction
from sahi.utils.cv import read_image
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error, mean_absolute_error


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
    image_format=".tif",
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

        # Save predicted boxes image
        result.export_visuals(file_name=filename[:-4], export_dir=predict_dir, hide_labels=True, rect_th=1)

        # Save YOLO-format annotations
        coco_annot = result.to_coco_annotations()
        yolo_boxes = [[i['category_id'], *i['bbox']] for i in coco_annot]
        write_yolo_boxes_to_file(img_width, img_height, yolo_boxes, os.path.join(predict_annot_dir, filename[:-4]+".txt"))

        # Count predictions
        pred_duck = sum(1 for obj in result.object_prediction_list if obj.category.id == 0)
        pred_crane = sum(1 for obj in result.object_prediction_list if obj.category.id == 1)

        # Count ground truth
        gt_duck, gt_crane = 0, 0
        label_path = os.path.join(label_dir, filename[:-4]+".txt") if label_dir else None
        if label_path and os.path.isfile(label_path):
            with open(label_path, 'r') as file:
                for line in file:
                    if line.startswith("0"): gt_duck += 1
                    elif line.startswith("1"): gt_crane += 1

        gt_b.append(gt_crane); gt_d.append(gt_duck)
        pr_b.append(pred_crane); pr_d.append(pred_duck)
        image_name.append(filename)

        # Visualize and merge GT vs Prediction
        gt_image = PImage.open(image_path).convert("RGB")
        pred_image = PImage.open(os.path.join(predict_dir, filename[:-4]+".png")).convert("RGB")

        draw_gt = ImageDraw.Draw(gt_image)
        draw_pred = ImageDraw.Draw(pred_image)
        font = ImageFont.truetype(font_path, 15)

        draw_gt.text((0, 0), f"GT Crane:{gt_crane}", font=font, fill='yellow')
        draw_gt.text((0, 20), f"GT Duck:{gt_duck}", font=font, fill='yellow')

        if label_path and os.path.isfile(label_path):
            with open(label_path, 'r') as file:
                for line in file:
                    class_id, x_center, y_center, width, height = map(float, line.split())
                    x_center *= img_width; y_center *= img_height
                    width *= img_width; height *= img_height
                    left = x_center - width / 2
                    top = y_center - height / 2
                    draw_gt.rectangle([left, top, left + width, top + height], outline={0: "red", 1: "blue"}[int(class_id)], width=1)

        draw_pred.text((0, 0), f"Pred Crane:{pred_crane}", font=font, fill='yellow')
        draw_pred.text((0, 20), f"Pred Duck:{pred_duck}", font=font, fill='yellow')

        # Combine and save
        merged = PImage.new('RGB', (img_width * 2, img_height))
        merged.paste(gt_image, (0, 0))
        merged.paste(pred_image, (img_width, 0))
        merged.save(os.path.join(predict_dir, filename))

    return gt_b, gt_d, pr_b, pr_d, image_name


if __name__ == "__main__":
    model_path = "/content/drive/MyDrive/conservation_research/YOLO/yolov5/runs/train/MCyolov5x_6_6/weights.best.pt"
    detection_model = AutoDetectionModel.from_pretrained(
        model_type='yolov5',
        model_path=model_path,
        confidence_threshold=0.2,
        device="cuda:0",
    )

    sahi_inference(
        detection_model=detection_model,
        slice_heights=[736],
        slice_widths=[736],
        image_dir="/content/drive/MyDrive/conservation_research/YOLO/datasets/sacr_dataset_Jan30/val/images",
        label_dir="/content/drive/MyDrive/conservation_research/YOLO/datasets/sacr_dataset_Jan30/val/labels",
        predict_dir="/content/drive/MyDrive/conservation_research/YOLO/datasets/yolov5_dataset/val_predictions",
        predict_annot_dir="/content/drive/MyDrive/conservation_research/YOLO/datasets/yolov5_dataset/val_annotations",
        font_path="/content/drive/MyDrive/conservation_research/YOLO/Arial_Bold.ttf"
    )