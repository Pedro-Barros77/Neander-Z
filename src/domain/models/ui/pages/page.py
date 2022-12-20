import pygame

from domain.models.ui.button import Button

class Page:
    def __init__(self, **kwargs) -> None:
        self.buttons: list[Button] = kwargs.pop("buttons", [])
        self.screen: pygame.Surface = kwargs.pop("screen", None)
        self.background_image: pygame.Surface = kwargs.pop("background_image", None)

    def update(self, **kwargs):
        for b in self.buttons:
            b.update()
            
    def set_background(self, image_path: str):
        self.background_image = pygame.transform.scale(pygame.image.load(image_path), self.screen.get_size())
        
    def draw(self):
        for b in self.buttons:
            b.draw(self.screen)
            