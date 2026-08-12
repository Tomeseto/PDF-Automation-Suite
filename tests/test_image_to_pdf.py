import os
import pytest
from PIL import Image
from app.modules.image_to_pdf import images_to_pdf

@pytest.fixture
def test_images(tmp_path):
    img1 = tmp_path / "img1.png"
    img2 = tmp_path / "img2.jpg"
    img3 = tmp_path / "img3.png"
    
    Image.new("RGB", (100, 100), "white").save(img1)
    Image.new("RGB", (200, 200), "black").save(img2)
    Image.new("RGB", (50, 150), "red").save(img3)
    
    return [str(img1), str(img2), str(img3)]

def test_convert_one_image(tmp_path, test_images):
    out = str(tmp_path / "out.pdf")
    res = images_to_pdf([test_images[0]], out)
    assert os.path.exists(res)

def test_convert_multiple_images(tmp_path, test_images):
    out = str(tmp_path / "out.pdf")
    res = images_to_pdf(test_images, out)
    assert os.path.exists(res)

def test_convert_mixed_sizes(tmp_path, test_images):
    out = str(tmp_path / "out.pdf")
    res = images_to_pdf(test_images, out)
    assert os.path.exists(res)

def test_convert_invalid_image(tmp_path):
    invalid = tmp_path / "invalid.txt"
    invalid.write_text("not an image")
    out = str(tmp_path / "out.pdf")
    with pytest.raises(RuntimeError):
        images_to_pdf([str(invalid)], out)

def test_convert_missing_file(tmp_path):
    missing = str(tmp_path / "missing.png")
    out = str(tmp_path / "out.pdf")
    with pytest.raises(FileNotFoundError):
        images_to_pdf([missing], out)

def test_convert_empty_list(tmp_path):
    out = str(tmp_path / "out.pdf")
    with pytest.raises(ValueError):
        images_to_pdf([], out)
