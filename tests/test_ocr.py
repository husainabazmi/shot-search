from PIL import Image, ImageDraw, ImageFont
from ocr import extract_text


def test_extract_text_from_image(tmp_path):
    # Create a blank image
    image = Image.new("RGB", (800, 250), "white")
    draw = ImageDraw.Draw(image)

    # Add large text to the image
    font = ImageFont.truetype("arial.ttf", 48)
    draw.text((50, 80), "HELLO WORLD", fill="black", font=font)

    # Save the image
    image_path = tmp_path / "hello.png"
    image.save(image_path)

    # Extract text using actual OCR
    extracted_text = extract_text(str(image_path))

    assert "HELLO" in extracted_text.upper()