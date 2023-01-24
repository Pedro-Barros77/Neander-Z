from domain.models.ui.pages.main_menu import MainMenu
from domain.services import menu_controller

menu = MainMenu()
menu_controller.start_page(menu)