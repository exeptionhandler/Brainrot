import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    NOTION_TOKEN = os.getenv('NOTION_TOKEN')
    NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
    
    # Configuración de caché
    CACHE_DURATION_MINUTES = 30
    ITEMS_PER_PAGE = 5
    
    # Validación de configuraciones
    @classmethod
    def validate(cls):
        missing = []
        if not cls.DISCORD_TOKEN:
            missing.append("DISCORD_TOKEN")
        if not cls.NOTION_TOKEN:
            missing.append("NOTION_TOKEN")
        if not cls.NOTION_DATABASE_ID:
            missing.append("NOTION_DATABASE_ID")
        
        if missing:
            raise ValueError(f"Faltan variables de entorno: {', '.join(missing)}")