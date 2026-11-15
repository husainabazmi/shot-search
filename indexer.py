
import hashlib
import logging
from pathlib import Path

from PIL import Image
from tqdm import tqdm

from db import (
    get_connection,
    init_db,
    get_image,
    add_image,
    update_image,
    update_mtime,
    delete_image
)
from ocr import extract_text

# Image extensions we support
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}

# Show warnings without stopping the program
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")


def calculate_hash(file_path):
    """Calculate SHA-256 hash without reading the whole file at once."""
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(4096)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


def index_folder(folder="images", db_path="shots.db", force=False, lang="eng"):

    image_folder = Path(folder)

    if not image_folder.is_dir():
        raise FileNotFoundError(f"Folder not found: {image_folder}")

    con = get_connection(db_path)
    init_db(con)

    new_count = 0
    skipped_count = 0
    removed_count = 0
    failed_count = 0
    processed_count = 0

    # Find all supported images
    image_paths = [
        path for path in image_folder.rglob("*")
        if path.is_file()
        and path.suffix.lower() in IMAGE_EXTENSIONS
    ]

    print(f"Found {len(image_paths)} images.")

    # Process each image
    for image_path in tqdm(image_paths, desc="Indexing images"):
        try:
            path_string = str(image_path.resolve())
            mtime = image_path.stat().st_mtime

            # Check whether this image already exists
            existing = get_image(con, path_string)

            # Skip unchanged images unless force is enabled
            if not force and existing is not None and existing["mtime"] == mtime:
                skipped_count += 1
                continue

            # Calculate file hash
            file_hash = calculate_hash(image_path)

            # Check whether file content has actually changed
            if not force and existing is not None:
                if existing["file_hash"] == file_hash:
                    update_mtime(con, path_string, mtime)
                    skipped_count += 1
                    processed_count += 1
                    continue

            # Run OCR
            with Image.open(image_path) as img:
                img.verify()
            extracted_text = extract_text(str(image_path), lang=lang)

            if existing is None:
                add_image(
                    con, path_string, mtime, file_hash, extracted_text
                )
                new_count += 1
            else:
                update_image(
                    con, path_string, mtime, file_hash, extracted_text
                )

            processed_count += 1

            # Save progress every 20 processed images
            if processed_count % 20 == 0:
                con.commit()

        except (Image.DecompressionBombError, Image.DecompressionBombWarning) as error:
            failed_count += 1
            logging.warning(
                "Image too large, skipped %s: %s", image_path, error
            )

        except Exception:
            failed_count += 1
            logging.exception(
                "Could not process %s", image_path
            )

    # Remove database entries for deleted images
    database_images = con.execute(
        "SELECT path FROM images"
    ).fetchall()

    for row in database_images:
        if not Path(row["path"]).exists():
            delete_image(con, row["path"])
            removed_count += 1

    con.commit()
    con.close()

    print("\nIndexing complete!")
    print(f"Indexed {new_count} new images.")
    print(f"Skipped {skipped_count} unchanged images.")
    print(f"Removed {removed_count} deleted images.")
    print(f"Failed {failed_count} images.")

if __name__ == "__main__":
    index_folder()
