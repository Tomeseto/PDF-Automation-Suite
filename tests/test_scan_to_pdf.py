import os
import pytest
from PIL import Image
from app.modules.scan_to_pdf import scan_images_to_pdf

@pytest.fixture
def test_images(tmp_path):
    img1 = tmp_path / "img1.png"
    img2 = tmp_path / "img2.jpg"
    
    Image.new("RGB", (100, 100), "white").save(img1)
    Image.new("RGB", (200, 200), "black").save(img2)
    
    return [str(img1), str(img2)]

def test_scan_single_image(tmp_path, test_images):
    out = str(tmp_path / "out.pdf")
    res = scan_images_to_pdf([test_images[0]], out)
    assert os.path.exists(res)

def test_scan_multiple_images(tmp_path, test_images):
    out = str(tmp_path / "out.pdf")
    res = scan_images_to_pdf(test_images, out)
    assert os.path.exists(res)

def test_scan_enhance_on(tmp_path, test_images):
    out = str(tmp_path / "out.pdf")
    res = scan_images_to_pdf(test_images, out, enhance=True)
    assert os.path.exists(res)

def test_scan_enhance_off(tmp_path, test_images):
    out = str(tmp_path / "out.pdf")
    res = scan_images_to_pdf(test_images, out, enhance=False)
    assert os.path.exists(res)

def test_scan_invalid_image(tmp_path):
    invalid = tmp_path / "invalid.txt"
    invalid.write_text("not an image")
    out = str(tmp_path / "out.pdf")
    with pytest.raises(RuntimeError):
        scan_images_to_pdf([str(invalid)], out)

def test_scan_missing_file(tmp_path):
    missing = str(tmp_path / "missing.png")
    out = str(tmp_path / "out.pdf")
    with pytest.raises(FileNotFoundError):
        scan_images_to_pdf([missing], out)

def test_scan_empty_list(tmp_path):
    out = str(tmp_path / "out.pdf")
    with pytest.raises(ValueError):
        scan_images_to_pdf([], out)
