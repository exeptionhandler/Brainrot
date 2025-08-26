from typing import List, Dict, Any
from services.notion_client import notion_client

class Brainrot:
    def __init__(self, notion_data: Dict[str, Any]):
        self.properties = notion_data.get('properties', {})
        self.id = notion_data.get('id')
    
    async def get_name(self) -> str:
        return await notion_client.extract_property(self.properties, 'Brainrot', 'title')
    
    async def get_price(self) -> str:
        return await notion_client.extract_property(self.properties, 'Dinero / Segundo', 'number')
    
    async def get_rarezas(self) -> List[str]:
        return await notion_client.extract_property(self.properties, 'Rareza', 'multi_select')
    
    async def get_efectos(self) -> List[str]:
        return await notion_client.extract_property(self.properties, 'Efectos', 'multi_select')
    
    async def is_vendido(self) -> bool:
        return await notion_client.extract_property(self.properties, 'Vendido?', 'checkbox')
    
    async def get_cuenta(self) -> str:
        return await notion_client.extract_property(self.properties, 'Cuenta', 'relation')
    
    async def to_dict(self) -> Dict[str, Any]:
        return {
            'nombre': await self.get_name(),
            'precio': await self.get_price(),
            'rarezas': await self.get_rarezas(),
            'efectos': await self.get_efectos(),
            'vendido': await self.is_vendido(),
            'cuenta': await self.get_cuenta()
        }

class BrainrotCollection:
    def __init__(self):
        self.brainrots: List[Brainrot] = []
    
    async def load_from_notion(self, force_refresh: bool = False):
        data = await notion_client.query_database(force_refresh)
        if data and 'results' in data:
            self.brainrots = [Brainrot(item) for item in data['results']]
    
    def get_all(self) -> List[Brainrot]:
        return self.brainrots
    
    def filter_by_name(self, query: str) -> List[Brainrot]:
        return [br for br in self.brainrots if query.lower() in (br.get_name() or '').lower()]
    
    def filter_by_rareza(self, rareza: str) -> List[Brainrot]:
        return [br for br in self.brainrots if rareza.lower() in [r.lower() for r in (br.get_rarezas() or [])]]
    
    def get_stats(self) -> Dict[str, Any]:
        # Implementar estadísticas
        return {}