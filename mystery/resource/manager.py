import sys
from atexit import register as atexit_register
from json import load, loads
from os import makedirs
from pathlib import Path
from tempfile import TemporaryDirectory

from pyglet import gl
from pyglet.font import have_font
from pyglet.font import load as load_font
from pyglet.image import load as load_image
from pyglet.resource import Loader
from pytmx import TiledMap, TileFlags

FONT_NAME = "Unifont"
SUPPORTED_LANG = {
    "en_us": "English (United States)",
    "zh_cn": "简体中文 (中国大陆)",
    "zh_hk": "繁體中文 (中國香港)",
    "zh_tw": "繁體中文 (中國臺灣)",
}


class ResourceManager:
    """Manage resources."""

    def __init__(self):
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            path = "assets"
            self._frozen = True
        else:
            path = "mystery/assets"
            self._frozen = False
        self.loader = Loader(path)
        self._lang = "en_us"
        self._translation_en_us = load(self.loader.file("i18n/en_us.json", mode="r"))
        self._translation_now = {}

        # Create temporary directory for *.tmx files.
        if not self._frozen:
            self._tmpdir = TemporaryDirectory(prefix="mystery-")
            atexit_register(self._tmpdir.cleanup)
            self.copy_to_tempdir()

        # Load uninstalled font.
        if not have_font("Unifont"):
            self.loader.add_font("unifont.otf")
        self.font = load_font("Unifont")

    @property
    def language(self) -> str:
        return self._lang

    @language.setter
    def language(self, name: str):
        if name not in SUPPORTED_LANG:
            name = "en_us"
        self._lang = name
        if self._lang == "en_us":
            self._translation_now = self._translation_en_us
            return
        contents = self.loader.file(f"i18n/{self._lang}.json", mode="rb").read()
        s = contents.decode("utf-8")
        self._translation_now = loads(s)

    def _image_loader(self, filename: str, flags, **kwargs):
        image = load_image(filename)

        def custom_load_image(rect: tuple[int, ...] = None, flags: TileFlags = None):
            if rect:
                x, y, w, h = rect
                y = image.height - y - h
                tile = image.get_region(x, y, w, h)
            else:
                tile = image
            return tile

        return custom_load_image

    def copy_to_tempdir(self):
        files = [
            Path("start.tmx"),
            Path("start_tent.tmx"),
            Path("tilesets/mask.png"),
            Path("tilesets/mask.tsx"),
            Path("tilesets/outside_objects.png"),
            Path("tilesets/outside_objects.tsx"),
            Path("tilesets/terrain.png"),
            Path("tilesets/terrain.tsx"),
        ]
        makedirs(Path(self._tmpdir.name) / "tilesets", exist_ok=True)
        for f in files:
            contents = self.loader.file(str(Path("maps") / f)).read()
            name = Path(self._tmpdir.name) / f
            with open(name, "wb") as target:
                target.write(contents)

    def tiled_map(self, name: str) -> TiledMap:
        if self._frozen:
            filename = Path(sys._MEIPASS) / "assets" / "maps" / f"{name}.tmx"
        else:
            filename = Path(self._tmpdir.name) / f"{name}.tmx"
        kwargs = {
            "image_loader": self._image_loader,
            "invert_y": True,
        }
        return TiledMap(filename, **kwargs)

    def translate(self, name: str, **kwargs) -> str:
        """Get the translation of `name`.

        Localized strings are generated by the following order:
          1. the language chosen by the player
          2. English
          3. `name` parameter
        """
        s = self._translation_now.get(name, self._translation_en_us.get(name, name))
        if s != name:
            try:
                return s.format(**kwargs)
            except:
                return name
        else:
            return name


__all__ = "FONT_NAME", "SUPPORTED_LANG", "ResourceManager"
