import unittest
import xml.etree.ElementTree as ET

from PIL import Image

from tracer import vectorize


SVG_NS = "{http://www.w3.org/2000/svg}"


class VectorizeTests(unittest.TestCase):
    def test_transparent_png_keeps_transparent_background_and_small_details(self):
        image = Image.new("RGBA", (5, 5), (0, 0, 0, 0))
        image.putpixel((2, 2), (255, 0, 0, 255))

        svg, _ = vectorize(image)
        root = ET.fromstring(svg)
        paths = root.findall(f"{SVG_NS}path")

        self.assertIsNone(root.find(f"{SVG_NS}rect"))
        self.assertEqual(len(paths), 1)
        self.assertEqual(paths[0].get("fill"), "#ff0000")
        self.assertIsNone(paths[0].get("stroke"))

    def test_partial_alpha_is_encoded_as_svg_fill_opacity(self):
        image = Image.new("RGBA", (2, 2), (0, 0, 0, 0))
        image.putpixel((0, 0), (0, 0, 255, 128))

        svg, _ = vectorize(image)
        paths = ET.fromstring(svg).findall(f"{SVG_NS}path")

        self.assertEqual(len(paths), 1)
        self.assertEqual(paths[0].get("fill"), "#0000ff")
        self.assertEqual(paths[0].get("fill-opacity"), "0.501961")

    def test_downscaling_keeps_transparent_background(self):
        image = Image.new("RGBA", (2001, 2), (0, 0, 0, 0))
        for x in range(500, 1500):
            image.putpixel((x, 0), (255, 0, 0, 255))

        svg, stats = vectorize(image)
        root = ET.fromstring(svg)

        self.assertEqual(stats["width"], 2001)
        self.assertIsNone(root.find(f"{SVG_NS}rect"))

    def test_black_and_white_mode_keeps_transparency(self):
        image = Image.new("RGBA", (3, 3), (0, 0, 0, 0))
        image.putpixel((1, 1), (0, 0, 0, 255))

        svg, _ = vectorize(image, mode="bw")
        root = ET.fromstring(svg)

        self.assertIsNone(root.find(f"{SVG_NS}rect"))
        self.assertEqual(root.find(f"{SVG_NS}path").get("fill"), "#000000")

    def test_black_and_white_mode_traces_opaque_white_background(self):
        image = Image.new("RGB", (3, 3), (255, 255, 255))
        image.putpixel((1, 1), (0, 0, 0))

        svg, _ = vectorize(image, mode="bw")
        root = ET.fromstring(svg)
        fills = {path.get("fill") for path in root.findall(f"{SVG_NS}path")}

        self.assertEqual(fills, {"#000000", "#ffffff"})

    def test_color_mode_keeps_the_most_common_color_as_a_path(self):
        image = Image.new("RGB", (4, 4), (0, 0, 0))
        for y in range(1, 3):
            for x in range(1, 3):
                image.putpixel((x, y), (255, 255, 255))

        svg, _ = vectorize(image, colors=2)
        root = ET.fromstring(svg)
        fills = {path.get("fill") for path in root.findall(f"{SVG_NS}path")}

        self.assertIsNone(root.find(f"{SVG_NS}rect"))
        self.assertEqual(fills, {"#000000", "#ffffff"})


if __name__ == "__main__":
    unittest.main()
