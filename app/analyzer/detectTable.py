import numpy as np
from PIL import Image
from ultralyticsplus import YOLO

def CropTable(image, filename_crop):
    model = YOLO('foduucom/table-detection-and-extraction')

    # Set model parameters
    model.overrides['conf'] = 0.25  # NMS confidence threshold
    model.overrides['iou'] = 0.8  # NMS IoU threshold
    model.overrides['agnostic_nms'] = False  # NMS class-agnostic
    model.overrides['max_det'] = 1000  # Maximum number of detections per image

    try:
        img = Image.open(image)
    except Exception as e:
        print("Error opening image file:", e)
        return False

    try:
        results = model.predict(img)
    except Exception as e:
        print("Error predicting with the model:", e)
        return False

    # Check if any boxes were detected
    if len(results[0].boxes.data.numpy()) > 0:
        try:
            x1, y1, x2, y2, _, _ = tuple(int(item) for item in results[0].boxes.data.numpy()[0])
        except Exception as e:
            print("Error processing detection results:", e)
            return False

        try:
            img = np.array(Image.open(image))
            # Cropping
            cropped_image = img[y1:y2, x1:x2]
            cropped_image = Image.fromarray(cropped_image)
            file_path = "./app/analyzer/" + filename_crop
            
            cropped_image.save(file_path)
            return True
        except Exception as e:
            print("Error processing and saving cropped image:", e)
            return False
    else:
        print("No table detected in the image.")
        return False
