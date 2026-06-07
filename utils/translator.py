import json
import os
import sys
from utils.logger import logger

class Translator:
    def __init__(self):
        self.current_lang = "es"  # Default to Spanish
        self.translations = {}
        self._load_translations()

    def set_lang(self, lang: str):
        if lang in ["es", "en"]:
            self.current_lang = lang
            self._load_translations()
            logger.info(f"Idioma de interfaz cambiado a: {lang}")

    def _load_translations(self):
        # Base path detection (works for development and PyInstaller package)
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        path = os.path.join(base_path, "assets", "i18n", f"{self.current_lang}.json")
        
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    self.translations = json.load(f)
                logger.debug(f"Traducciones cargadas con éxito para idioma '{self.current_lang}' desde {path}")
            else:
                logger.error(f"Archivo de traducción no encontrado en la ruta: {path}")
                # Fallback empty translations
                self.translations = {}
        except Exception as e:
            logger.error(f"Error cargando traducciones en {path}: {str(e)}", exc_info=True)
            self.translations = {}

    def translate(self, key: str, **kwargs) -> str:
        val = self.translations.get(key, key)
        if kwargs:
            try:
                return val.format(**kwargs)
            except Exception as e:
                logger.warning(f"Error formateando traducción para key '{key}': {str(e)}")
        return val

# Global instance
translator = Translator()

def t(key: str, **kwargs) -> str:
    """Función de traducción rápida global."""
    return translator.translate(key, **kwargs)
