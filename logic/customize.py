# logic/customize.py
from PyQt6.QtGui import QFont
from logic.theme_manager import load_theme_qss, set_theme, get_theme

class Customize:
    #  Tema
    @staticmethod
    def apply_theme(theme_name: str):
        set_theme(theme_name)
        load_theme_qss()

    @staticmethod
    def current_theme() -> str:
        return get_theme()

    #  Fonte
    @staticmethod
    def app_font(size: int = 10, family: str = "Arial"):
        return QFont(family, size)

    #  Paleta de cores customizada (futuro)
    @staticmethod   
    def set_accent_color(color: str):
        # Exemplo: "#7C3AED"
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        app.setStyleSheet(f":root {{ --accent-color: {color}; }}")
