"""
synthetic_generator.py
Generates synthetic raster images (shapes) for R2V testing / benchmarking.
"""
from PIL import Image, ImageDraw
import random


def generate_synthetic_raster(output_path="test_raster.png", width=800, height=600,
                              filled=False):
    """Draw a few random shapes. `output_path` may be a path or a file object."""
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    for _ in range(5):
        shape = random.choice(["rectangle", "ellipse", "polygon"])
        color = tuple(random.randint(0, 200) for _ in range(3))
        x1, y1 = random.randint(30, width // 2), random.randint(30, height // 2)
        x2, y2 = x1 + random.randint(60, 220), y1 + random.randint(60, 220)
        kw = {"fill": color} if filled else {"outline": color, "width": 3}
        if shape == "rectangle":
            draw.rectangle([x1, y1, x2, y2], **kw)
        elif shape == "ellipse":
            draw.ellipse([x1, y1, x2, y2], **kw)
        else:
            draw.polygon([(x1, y1), (x2, y1 + 50), (x1 + 50, y2)],
                         **({"fill": color} if filled else {"outline": color}))
    image.save(output_path, format="PNG")
    return output_path


if __name__ == "__main__":
    print("Generated:", generate_synthetic_raster())
