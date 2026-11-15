
from PIL import Image, ImageStat, ImageOps
import pytesseract
import sys


def preprocess(img):
    # 1. Convert to grayscale
    gray = img.convert("L")
    # Downscale unusually large images
    width, height = gray.size

    if max(width, height) > 4000:
        scale = 4000 / max(width, height)

        gray = gray.resize(
            (int(width * scale), int(height * scale)),
            Image.Resampling.LANCZOS
        )

    # 2. Upscale small images
    width, height = gray.size

    if width < 1500:
        gray = gray.resize(
            (width * 2, height * 2),
            Image.Resampling.LANCZOS
        )

    # 3. Detect dark mode and invert if necessary
    brightness = ImageStat.Stat(gray).mean[0]

    if brightness < 100:
        gray = ImageOps.invert(gray)

    # 4. Improve contrast
    gray = ImageOps.autocontrast(gray)

    return gray


def extract_text(image_path, use_preprocessing=True, lang="eng"):
    with Image.open(image_path) as img:

        if use_preprocessing:
            img = preprocess(img)

        return pytesseract.image_to_string(
            img,
            lang=lang,
            config="--psm 6"
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ocr.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    print(extract_text(image_path))
