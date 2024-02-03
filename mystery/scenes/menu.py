from importlib import import_module

from pyglet import app, clock
from pyglet.graphics import Batch, Group
from pyglet.sprite import Sprite
from pyglet.text import Label
from pyglet.window import Window

from mystery.gui.widgets import TextButton
from mystery.scenes import Scene


class MenuScene(Scene):
    def __init__(self, window: Window):
        super().__init__(window)
        self.batch = Batch()
        self.back_group = Group(order=0)
        self.fore_group = Group(order=1)

        self.background_image = self.window.resource.loader.image(
            "textures/background.png"
        )
        self.background_image.anchor_x = self.background_image.width // 2
        self.background_image.anchor_y = self.background_image.height // 2
        self.background = Sprite(
            self.background_image,
            x=self.window.width // 2,
            y=self.window.height // 2,
            batch=self.batch,
            group=self.back_group,
        )
        self.title_image = self.window.resource.loader.image("textures/title.png")
        self.title_image.anchor_x = self.title_image.width // 2
        self.title_image.anchor_y = self.title_image.height // 2
        self.title = Sprite(
            self.title_image,
            x=self.window.width // 2,
            y=0.8 * self.window.height,
            batch=self.batch,
            group=self.fore_group,
        )

        self.game_button = TextButton(
            self.window.resource.translate("menu.start_game"),
            self.window.width // 2 - 150,
            0.8 * self.window.height // 2 + 65,
            300,
            55,
            batch=self.batch,
            group=self.fore_group,
        )
        self.saves_button = TextButton(
            self.window.resource.translate("menu.saves"),
            self.window.width // 2 - 150,
            0.8 * self.window.height // 2 + 5,
            300,
            55,
            batch=self.batch,
            group=self.fore_group,
        )
        self.settings_button = TextButton(
            self.window.resource.translate("menu.settings"),
            self.window.width // 2 - 150,
            0.8 * self.window.height // 2 - 55,
            300,
            55,
            font_size=24,
            batch=self.batch,
            group=self.fore_group,
        )
        self.exit_button = TextButton(
            self.window.resource.translate("menu.exit"),
            self.window.width // 2 - 150,
            0.8 * self.window.height // 2 - 115,
            300,
            55,
            font_size=24,
            batch=self.batch,
            group=self.fore_group,
        )
        self.game_button.push_handlers(on_click=self.start)
        self.settings_button.push_handlers(on_click=self.settings)
        self.exit_button.push_handlers(on_click=self.window.close)
        self.frame.add_widget(
            self.game_button, self.saves_button, self.settings_button, self.exit_button
        )

    def _animate(self, dt):
        if self.background.opacity <= 10:
            self.background.opacity = 0
            if not self.window.has_scene("start"):
                next_scene = import_module("mystery.scenes.start").StartScene
                self.window.add_scene("start", next_scene)
            self.window.switch_scene("start")
        else:
            self.background.opacity -= dt * 120
            clock.schedule_once(self._animate, 1 / self.window.setting["fps"])

    def start(self):
        self.fore_group.visible = False
        clock.schedule_once(self._animate, 1 / self.window.setting["fps"])

    def settings(self):
        if not self.window.has_scene("settings.main"):
            next_scene = import_module("mystery.scenes.settings.main").SettingsScene
            self.window.add_scene("settings.main", next_scene)
        self.window.switch_scene("settings.main")

    def on_draw(self):
        self.window.clear()
        self.batch.draw()

    def on_resize(self, width, height):
        self.background.position = (width // 2, height // 2, 0)
        if 3 * width >= 4 * height:
            self.background.scale = width / self.background.image.width
        else:
            self.background.scale = height / self.background.image.height
        self.title.position = (width // 2, 0.8 * height, 0)
        self.game_button.position = (width // 2 - 150, 0.8 * height // 2 + 65)
        self.saves_button.position = (width // 2 - 150, 0.8 * height // 2 + 5)
        self.settings_button.position = (width // 2 - 150, 0.8 * height // 2 - 55)
        self.exit_button.position = (width // 2 - 150, 0.8 * height // 2 - 115)

    def on_language_change(self):
        self.game_button.text = self.window.resource.translate("menu.start_game")
        self.saves_button.text = self.window.resource.translate("menu.saves")
        self.settings_button.text = self.window.resource.translate("menu.settings")
        self.exit_button.text = self.window.resource.translate("menu.exit")

    def on_scene_leave(self):
        self.background.opacity = 255
        self.fore_group.visible = True


__all__ = "StartScene"
