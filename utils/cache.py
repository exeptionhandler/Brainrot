from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from config import Config

class CacheManager:
    def __init__(self):
        self.relation_cache: Dict[str, Any] = {}
        self.brainrot_cache: Dict[str, Any] = {
            'last_update': None,
            'data': None,
            'stats': None
        }
    
    def is_brainrot_cache_valid(self) -> bool:
        return (self.brainrot_cache['data'] is not None and 
                self.brainrot_cache['last_update'] is not None and
                (datetime.now() - self.brainrot_cache['last_update'] < 
                 timedelta(minutes=Config.CACHE_DURATION_MINUTES)))
    
    def update_brainrot_cache(self, data: Any):
        self.brainrot_cache['data'] = data
        self.brainrot_cache['last_update'] = datetime.now()
    
    def get_relation(self, key: str) -> Optional[Any]:
        return self.relation_cache.get(key)
    
    def set_relation(self, key: str, value: Any):
        self.relation_cache[key] = value
    
    def clear_relation_cache(self):
        self.relation_cache = {}
    
    def clear_all(self):
        self.clear_relation_cache()
        self.brainrot_cache = {'last_update': None, 'data': None, 'stats': None}

# Instancia global de caché
cache_manager = CacheManager()