from sahi.predict import get_sliced_prediction
from sahi.utils.cv import read_image
from PIL import ImageDraw, ImageFont
import os
from PIL import Image

def sahi_single_inference(
    image_path,
    detection_model,
    output_path="prediction.png",
    slice_height=512,
    slice_width=512,
    font_path="Arial_Bold.ttf"
):
    result = get_sliced_prediction(
        image=image_path,
        detection_model=detection_model,
        slice_height=slice_height,
        slice_width=slice_width,
        overlap_height_ratio=0.2,
        overlap_width_ratio=0.2,
    )

    result.export_visuals(
        file_name="./temp",
        export_dir=os.path.dirname(output_path),
        hide_labels=True,
        rect_th=1
    )

    pred_image = Image.open(os.path.join(os.path.dirname(output_path), "temp.png")).convert("RGB")
    draw_pred = ImageDraw.Draw(pred_image)
    font = ImageFont.truetype(font_path, 15)

    pred_duck = sum(1 for obj in result.object_prediction_list if obj.category.id == 0)
    pred_crane = sum(1 for obj in result.object_prediction_list if obj.category.id == 1)

    draw_pred.text((0, 0), f"Pred Crane:{pred_crane}", font=font, fill='yellow')
    draw_pred.text((0, 20), f"Pred Duck:{pred_duck}", font=font, fill='yellow')

    pred_image.save(output_path)
    return output_path
