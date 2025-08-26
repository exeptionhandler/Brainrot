import aiohttp
from typing import Dict, Any, Optional
from config import Config
from utils.cache import cache_manager

class NotionClient:
    def __init__(self):
        self.token = Config.NOTION_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def create_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)
    
    async def close_session(self):
        if self.session:
            await self.session.close()
            self.session = None
    
    async def query_database(self, force_refresh: bool = False) -> Dict[str, Any]:
        if not force_refresh and cache_manager.is_brainrot_cache_valid():
            return cache_manager.brainrot_cache['data']
        
        await self.create_session()
        url = f"https://api.notion.com/v1/databases/{Config.NOTION_DATABASE_ID}/query"
        
        try:
            async with self.session.post(url) as response:
                data = await response.json()
                cache_manager.update_brainrot_cache(data)
                return data
        except Exception as e:
            raise Exception(f"Error querying Notion database: {e}")
    
    async def get_page(self, page_id: str) -> Dict[str, Any]:
        cached_data = cache_manager.get_relation(page_id)
        if cached_data:
            return cached_data
        
        await self.create_session()
        url = f"https://api.notion.com/v1/pages/{page_id}"
        
        try:
            async with self.session.get(url) as response:
                data = await response.json()
                cache_manager.set_relation(page_id, data)
                return data
        except Exception as e:
            raise Exception(f"Error getting Notion page {page_id}: {e}")
    
    async def extract_property(self, properties: Dict[str, Any], 
                             property_name: str, 
                             property_type: str) -> Any:
        from utils.formatters import format_price
        
        try:
            prop = properties.get(property_name, {})
            
            if property_type == 'title':
                if prop.get('title') and prop['title']:
                    return prop['title'][0].get('text', {}).get('content', 'N/A')
            
            elif property_type == 'number':
                number_value = prop.get('number')
                if number_value is not None:
                    return format_price(number_value)
            
            elif property_type == 'multi_select':
                if prop.get('multi_select'):
                    return [item['name'] for item in prop['multi_select']]
            
            elif property_type == 'checkbox':
                return prop.get('checkbox', False)
            
            elif property_type == 'relation':
                if prop.get('relation') and prop['relation']:
                    relation_id = prop['relation'][0]['id']
                    try:
                        related_page = await self.get_page(relation_id)
                        for prop_value in related_page.get('properties', {}).values():
                            if (prop_value.get('type') == 'title' and 
                                prop_value.get('title') and 
                                prop_value['title']):
                                name = prop_value['title'][0].get('text', {}).get('content')
                                if name:
                                    return name
                        return f"Cuenta #{relation_id[:8]}"
                    except:
                        return f"Cuenta #{relation_id[:8]}"
        
        except Exception as e:
            print(f"Error extrayendo propiedad {property_name}: {e}")
        
        return 'N/A'

# Instancia global del cliente
notion_client = NotionClient()