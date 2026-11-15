from PIL import Image, ImageDraw

from indexer import index_folder
from db import get_connection


def create_image(path, text):
    image = Image.new("RGB", (400, 200), "white")
    draw = ImageDraw.Draw(image)
    draw.text((20, 50), text, fill="black")
    image.save(path)
def test_indexing_twice_processes_new_files_once(tmp_path, monkeypatch):

    image_folder = tmp_path / "images"
    image_folder.mkdir()

    db_path = tmp_path / "test.db"

    image_path = image_folder / "hello.png"
    create_image(image_path, "HELLO WORLD")

    ocr_calls = []

    def fake_ocr(path, lang="eng"):
        ocr_calls.append(path)
        return "HELLO WORLD"

    monkeypatch.setattr("indexer.extract_text", fake_ocr)

    index_folder(image_folder, db_path)
    index_folder(image_folder, db_path)

    assert len(ocr_calls) == 1

    con = get_connection(db_path)

    try:
        total_images = con.execute(
            "SELECT COUNT(*) FROM images"
        ).fetchone()[0]

        assert total_images == 1

    finally:
        con.close()
def test_corrupt_image_does_not_crash(tmp_path, monkeypatch):

    image_folder = tmp_path / "images"
    image_folder.mkdir()

    db_path = tmp_path / "test.db"

    # Create one valid image
    valid_image = image_folder / "valid.png"
    create_image(valid_image, "HELLO WORLD")

    # Create one corrupted image
    corrupt_image = image_folder / "corrupt.png"
    corrupt_image.write_bytes(b"This is not a valid image")

    monkeypatch.setattr(
        "indexer.extract_text",
        lambda path, lang="eng": "HELLO WORLD"
    )

    # Indexing should continue despite the corrupted image
    index_folder(image_folder, db_path)

    con = get_connection(db_path)

    try:
        total_images = con.execute(
            "SELECT COUNT(*) FROM images"
        ).fetchone()[0]

        assert total_images == 1

    finally:
        con.close()