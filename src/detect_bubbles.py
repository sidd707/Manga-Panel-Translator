from ultralytics import YOLO


def detect_bubbles(model_path, image):
    """
    Detects bubbles in an image using a YOLOv8 model.

    Args:
        model_path (str): The file path to the YOLO model.
        image (str or np.ndarray): Path to image or image array.

    Returns:
        list: [x1, y1, x2, y2, score, class_id] for each detection.
    """
    model = YOLO(model_path)
    results = model(image)[0]
    return results.boxes.data.tolist()
