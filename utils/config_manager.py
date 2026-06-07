
import os
import json
from config import CONFIG_FILE
from utils.logger import logger

def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                cfg = json.load(f)
                logger.debug(f"Configuración cargada con éxito: {cfg}")
                return cfg
        except Exception as e:
            logger.error(f"Error cargando archivo de configuración {CONFIG_FILE}: {str(e)}", exc_info=True)
    else:
        logger.info(f"El archivo de configuración {CONFIG_FILE} no existe. Se utilizarán valores por defecto.")
    return {}


def save_config(data: dict):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f, indent=2)
            logger.debug(f"Configuración guardada en {CONFIG_FILE}: {data}")
    except Exception as e:
        logger.error(f"Error guardando archivo de configuración {CONFIG_FILE}: {str(e)}", exc_info=True)

