import easyocr
reader = easyocr.Reader(['en'])

def apply_OCR(image_path, OCR_threshold = 0.5):
    """
    Applies Optical Character Recognition (OCR) on an image and returns the recognized text.

    Args:
        image_path (str): The path to the image file.
        OCR_threshold (float, optional): The confidence threshold for the OCR detection. Defaults to 0.5.

    Returns:
        str or None: The recognized text if any text is detected, otherwise None.
    """
    try:
        result = reader.readtext(image_path)
        text = " ".join(detection[1] for detection in result if detection[2] > OCR_threshold)
        text = text.replace(",", "")
        return text if text else None
    except Exception as e:
        return None