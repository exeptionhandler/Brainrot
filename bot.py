import discord
from discord.ext import commands, tasks
from discord.ui import Button, View, Select
import aiohttp
import asyncio
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json
from typing import Dict, List, Optional

# Cargar variables de entorno
load_dotenv()

# Configuración
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Diccionario de emojis personalizados
CUSTOM_EMOJIS = {
    # Emojis de estado
    'disponible': '<:yes:1409698306006843423>',
    'vendido': '<:no:1409698339590766677>',
    'cargando': '<:loading:1409696840235880549>',
    
    # Emojis de efectos
    'fire': '<:Fire:1409669192004931716>',
    'fireworks': '<:Fireworks:1409669176062382201>',
    'glitch': '<:Glitch:1409669158265684029>',
    'shark': '<:Shark_Fin:1409669098467496036>',
    'taco': '<:Taco:1409669063130484787>',
    'wet': '<:Wet:1409669046273708082>',
    'snowy': '<:Snowy:1409669074618941481>',
    'sleepy': '<:Sleepy:1409669084328624138>',
    'nyan': '<:Nyan:1409669115228192808>',
    'disco': '<:Disco:1409669214255579258>',
    'crab': '<:CrabClaw:1409669228604428308>',
    'comet': '<:Cometstruck:1409669235696996502>',
    'comet2': '<:Comet2:1409669244010102997>',
    'bubblegum': '<:Bubblegum:1409669250423193701>',
    'brazil': '<:Brazil:1409669262540279929>',
    'bomb': '<:Bombardiro:1409669272262672487>',
    'bloodmoon': '<:Bloodmoon:1409669312448565329>',
    'ufo': '<:UFO:1409669322682400788>',
    '10b': '<:10b:1409669329120792638>',
    'matteo': '<:MatteoHat:1409669147230736565>',
    'evil': '<:EvilTungTungSahur:1409669203257987263>',
    
    # Emojis genéricos
    'brainrot': '🧠',
    'dinero': '💰',
    'rareza': '🎯',
    'efectos': '✨',
    'cuenta': '👤',
    'buscar': '🔍',
    'estadisticas': '📊',
    'dashboard': '📈',
    'error': '❌',
    'exito': '✅',
    'advertencia': '⚠️',
    'info': 'ℹ️',
    'reloj': '⏰',
    'corazon': '❤️',
    'fuego': '🔥',
    'estrella': '⭐',
    'cohete': '🚀',
    'gem': '💎',
    'rainbow': '🌈'
}

# Mapeo de efectos a emojis personalizados
EFECTO_EMOJIS = {
    'fire': 'fire',
    'spark': 'fireworks',
    'glitch': 'glitch',
    'shark': 'shark',
    'taco': 'taco',
    'wet': 'wet',
    'snow': 'snowy',
    'sleepy': 'sleepy',
    'nyan': 'nyan',
    'disco': 'disco',
    'crab': 'crab',
    'comet': 'comet',
    'bubblegum': 'bubblegum',
    'brazil': 'brazil',
    'bomb': 'bomb',
    'bloodmoon': 'bloodmoon',
    'ufo': 'ufo',
    '10b': '10b',
    'matteo': 'matteo',
    'evil': 'evil',
    'diamond': 'gem',
    'rainbow': 'rainbow',
    'galaxy': 'ufo',
    'color': 'rainbow'
}

# Mapeo de rarezas a emojis
RAREZA_EMOJIS = {
    'brainrot god': '👑',
    'secret': '🔒',
    'mythic': '🌟',
    'common': '⚪',
    'rare': '🔵',
    'epic': '🟣',
    'legendary': '🟠'
}

# Caché para mejorar el rendimiento
relation_cache: Dict[str, str] = {}
brainrot_cache = {
    'last_update': None,
    'data': None,
    'stats': None
}

class NotionClient:
    def __init__(self, token):
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        self.session = None
        
    async def create_session(self):
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)
    
    async def close_session(self):
        if self.session:
            await self.session.close()
    
    async def query_database(self, database_id, force_refresh=False):
        if not force_refresh and brainrot_cache['data'] and brainrot_cache['last_update'] and (datetime.now() - brainrot_cache['last_update'] < timedelta(minutes=5)):
            return brainrot_cache['data']
        
        await self.create_session()
        url = f"https://api.notion.com/v1/databases/{database_id}/query"
        async with self.session.post(url) as response:
            data = await response.json()
            brainrot_cache['data'] = data
            brainrot_cache['last_update'] = datetime.now()
            return data
    
    async def get_page(self, page_id):
        if page_id in relation_cache:
            return relation_cache[page_id]
        
        await self.create_session()
        url = f"https://api.notion.com/v1/pages/{page_id}"
        async with self.session.get(url) as response:
            data = await response.json()
            relation_cache[page_id] = data
            return data

notion = NotionClient(NOTION_TOKEN)

# Función para obtener emoji de efecto
def get_efecto_emoji(efecto_name):
    efecto_lower = efecto_name.lower()
    for key, emoji_key in EFECTO_EMOJIS.items():
        if key in efecto_lower:
            return CUSTOM_EMOJIS.get(emoji_key, '✨')
    return '✨'

# Función para obtener emoji de rareza
def get_rareza_emoji(rareza_name):
    rareza_lower = rareza_name.lower()
    for key, emoji in RAREZA_EMOJIS.items():
        if key in rareza_lower:
            return emoji
    return '⚪'

async def extract_notion_property(properties, property_name, property_type):
    try:
        prop = properties.get(property_name, {})
        
        if property_type == 'title':
            if prop.get('title') and prop['title']:
                return prop['title'][0].get('text', {}).get('content', 'N/A')
        
        elif property_type == 'number':
            number_value = prop.get('number')
            if number_value is not None:
                return f"{number_value:,.0f} US$"
        
        elif property_type == 'multi_select':
            if prop.get('multi_select'):
                return [item['name'] for item in prop['multi_select']]
        
        elif property_type == 'checkbox':
            return prop.get('checkbox', False)
        
        elif property_type == 'relation':
            if prop.get('relation') and prop['relation']:
                relation_id = prop['relation'][0]['id']
                try:
                    related_page = await notion.get_page(relation_id)
                    for prop_value in related_page.get('properties', {}).values():
                        if prop_value.get('type') == 'title' and prop_value.get('title'):
                            if prop_value['title'] and len(prop_value['title']) > 0:
                                name = prop_value['title'][0].get('text', {}).get('content')
                                if name:
                                    return name
                    return f"Cuenta #{relation_id[:8]}"
                except:
                    return f"Cuenta #{relation_id[:8]}"
    
    except Exception as e:
        print(f"Error extrayendo {property_name}: {e}")
    
    return 'N/A'

class AdvancedPaginationView(View):
    def __init__(self, pages, timeout=180):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.current_page = 0
        self.total_pages = len(pages)
        self.message = None
        
    async def update_embed(self, interaction):
        embed = self.pages[self.current_page]
        embed.set_footer(text=f"{CUSTOM_EMOJIS['reloj']} Página {self.current_page + 1}/{self.total_pages} • ⏹️ para cerrar")
        
        self.previous_button.disabled = (self.current_page == 0)
        self.next_button.disabled = (self.current_page == self.total_pages - 1)
        self.first_button.disabled = (self.current_page == 0)
        self.last_button.disabled = (self.current_page == self.total_pages - 1)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.secondary)
    async def first_button(self, interaction: discord.Interaction, button: Button):
        if self.current_page > 0:
            self.current_page = 0
            await self.update_embed(interaction)
    
    @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction: discord.Interaction, button: Button):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_embed(interaction)
    
    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction: discord.Interaction, button: Button):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            await self.update_embed(interaction)
    
    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary)
    async def last_button(self, interaction: discord.Interaction, button: Button):
        if self.current_page < self.total_pages - 1:
            self.current_page = self.total_pages - 1
            await self.update_embed(interaction)
    
    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.danger)
    async def stop_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.defer()
        await interaction.delete_original_response()
        self.stop()

@tasks.loop(minutes=30)
async def clean_cache():
    global relation_cache
    relation_cache = {}
    print(f"{CUSTOM_EMOJIS['cargando']} Caché limpiada")

@bot.event
async def on_ready():
    print(f'{bot.user} se ha conectado a Discord! {CUSTOM_EMOJIS["cohete"]}')
    clean_cache.start()
    try:
        synced = await bot.tree.sync()
        print(f"Comandos slash sincronizados: {len(synced)}")
    except Exception as e:
        print(f"Error sincronizando comandos slash: {e}")

@bot.command()
async def brainrots(ctx, items_per_page: int = 5):
    """Muestra Brainrots con emojis personalizados"""
    try:
        loading_msg = await ctx.send(f"{CUSTOM_EMOJIS['cargando']} Cargando Brainrots...")
        
        data = await notion.query_database(NOTION_DATABASE_ID)
        
        if not data or 'results' not in data:
            await loading_msg.edit(content=f"{CUSTOM_EMOJIS['error']} No se pudieron obtener los datos.")
            return
        
        all_brainrots = data['results']
        
        if not all_brainrots:
            await loading_msg.edit(content=f"{CUSTOM_EMOJIS['advertencia']} No hay Brainrots en la base de datos.")
            return
        
        pages = []
        items_per_page = max(1, min(items_per_page, 5))
        
        for i in range(0, len(all_brainrots), items_per_page):
            page_brainrots = all_brainrots[i:i + items_per_page]
            
            embed = discord.Embed(
                title=f"{CUSTOM_EMOJIS['brainrot']} **COLECCIÓN DE BRAINROTS**", 
                color=0x00ffaa,
                timestamp=datetime.now()
            )
            
            for item in page_brainrots:
                properties = item.get('properties', {})
                
                brainrot = await extract_notion_property(properties, 'Brainrot', 'title')
                dinero = await extract_notion_property(properties, 'Dinero / Segundo', 'number')
                rareza_list = await extract_notion_property(properties, 'Rareza', 'multi_select')
                efectos_list = await extract_notion_property(properties, 'Efectos', 'multi_select')
                vendido = await extract_notion_property(properties, 'Vendido?', 'checkbox')
                cuenta = await extract_notion_property(properties, 'Cuenta', 'relation')
                
                # Formatear con emojis personalizados
                rareza_text = ""
                if rareza_list and rareza_list != 'N/A':
                    for rareza in rareza_list:
                        rareza_emoji = get_rareza_emoji(rareza)
                        rareza_text += f"{rareza_emoji} {rareza} "
                else:
                    rareza_text = "⚪ Sin rareza"
                
                efectos_text = ""
                if efectos_list and efectos_list != 'N/A':
                    for efecto in efectos_list:
                        efecto_emoji = get_efecto_emoji(efecto)
                        efectos_text += f"{efecto_emoji} {efecto} "
                else:
                    efectos_text = f"{CUSTOM_EMOJIS['efectos']} Sin efectos"
                
                status_emoji = CUSTOM_EMOJIS['vendido'] if vendido else CUSTOM_EMOJIS['disponible']
                status_text = "Vendido" if vendido else "Disponible"
                
                field_value = f"{CUSTOM_EMOJIS['dinero']} **{dinero}**\n"
                field_value += f"{CUSTOM_EMOJIS['rareza']} **{rareza_text}**\n"
                field_value += f"{CUSTOM_EMOJIS['efectos']} **{efectos_text}**\n"
                field_value += f"{status_emoji} **{status_text}**\n"
                field_value += f"{CUSTOM_EMOJIS['cuenta']} **{cuenta}**"
                
                embed.add_field(name=f"**{brainrot}**", value=field_value, inline=False)
                embed.add_field(name="\u200b", value="▬" * 35, inline=False)
            
            pages.append(embed)
        
        await loading_msg.delete()
        view = AdvancedPaginationView(pages)
        first_embed = pages[0]
        first_embed.set_footer(text=f"{CUSTOM_EMOJIS['reloj']} Página 1/{len(pages)} • {CUSTOM_EMOJIS['brainrot']} Total: {len(all_brainrots)} Brainrots")
        
        await ctx.send(embed=first_embed, view=view)
        
    except Exception as e:
        await ctx.send(f"{CUSTOM_EMOJIS['error']} Error: {str(e)}")

@bot.command()
async def dashboard(ctx):
    """Dashboard con emojis personalizados"""
    try:
        data = await notion.query_database(NOTION_DATABASE_ID)
        
        if not data or 'results' not in data:
            await ctx.send(f"{CUSTOM_EMOJIS['error']} No se pudieron obtener los datos.")
            return
        
        all_brainrots = data['results']
        
        # Calcular estadísticas
        total = len(all_brainrots)
        total_value = 0
        rareza_count = {}
        efectos_count = {}
        vendidos = 0
        
        for item in all_brainrots:
            properties = item.get('properties', {})
            
            dinero = properties.get('Dinero / Segundo', {}).get('number', 0)
            if dinero:
                total_value += dinero
            
            rareza_list = properties.get('Rareza', {}).get('multi_select', [])
            for rareza in rareza_list:
                rareza_name = rareza.get('name', 'Sin rareza')
                rareza_count[rareza_name] = rareza_count.get(rareza_name, 0) + 1
            
            efectos_list = properties.get('Efectos', {}).get('multi_select', [])
            for efecto in efectos_list:
                efecto_name = efecto.get('name', 'Sin efecto')
                efectos_count[efecto_name] = efectos_count.get(efecto_name, 0) + 1
            
            if properties.get('Vendido?', {}).get('checkbox', False):
                vendidos += 1
        
        # Crear embed del dashboard
        embed = discord.Embed(
            title=f"{CUSTOM_EMOJIS['dashboard']} **DASHBOARD BRAINROTS**",
            description=f"{CUSTOM_EMOJIS['cohete']} Estadísticas completas de tu colección",
            color=0x9370DB,
            timestamp=datetime.now()
        )
        
        embed.add_field(name=f"{CUSTOM_EMOJIS['brainrot']} Total Brainrots", value=f"**{total}**", inline=True)
        embed.add_field(name=f"{CUSTOM_EMOJIS['dinero']} Valor Total", value=f"**{total_value:,.0f} US$**", inline=True)
        embed.add_field(name=f"{CUSTOM_EMOJIS['vendido']} Vendidos", value=f"**{vendidos}**", inline=True)
        
        # Top rarezas
        rareza_text = "\n".join([f"{get_rareza_emoji(k)} {k}: **{v}**" for k, v in sorted(rareza_count.items(), key=lambda x: x[1], reverse=True)[:3]])
        embed.add_field(name=f"{CUSTOM_EMOJIS['rareza']} Top Rarezas", value=rareza_text or "No data", inline=False)
        
        # Top efectos
        if efectos_count:
            top_efecto = max(efectos_count.items(), key=lambda x: x[1])
            efecto_emoji = get_efecto_emoji(top_efecto[0])
            embed.add_field(name=f"{CUSTOM_EMOJIS['efectos']} Efecto Más Común", value=f"{efecto_emoji} {top_efecto[0]}: **{top_efecto[1]}**", inline=True)
        
        # Disponibilidad
        disp_emoji = CUSTOM_EMOJIS['disponible']
        vend_emoji = CUSTOM_EMOJIS['vendido']
        disponibilidad = f"{disp_emoji} Disponibles: **{total - vendidos}**\n{vend_emoji} Vendidos: **{vendidos}**"
        embed.add_field(name=f"{CUSTOM_EMOJIS['info']} Disponibilidad", value=disponibilidad, inline=True)
        
        embed.set_footer(text=f"{CUSTOM_EMOJIS['fuego']} Usa !brainrots para ver la lista completa")
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"{CUSTOM_EMOJIS['error']} Error: {str(e)}")

@bot.command()
async def emojis(ctx):
    """Muestra todos los emojis personalizados disponibles"""
    embed = discord.Embed(
        title=f"{CUSTOM_EMOJIS['rainbow']} **EMOJIS PERSONALIZADOS**",
        description="Lista de todos los emojis disponibles para el bot",
        color=0xFFD700
    )
    
    # Agrupar emojis por categoría
    categorias = {
        "Estados": ['disponible', 'vendido', 'cargando'],
        "Efectos": ['fire', 'fireworks', 'glitch', 'shark', 'taco', 'wet', 'snowy', 'sleepy', 
                   'nyan', 'disco', 'crab', 'comet', 'bubblegum', 'brazil', 'bomb', 'bloodmoon', 'ufo', '10b', 'matteo', 'evil'],
        "Genéricos": ['brainrot', 'dinero', 'rareza', 'efectos', 'cuenta', 'buscar', 'estadisticas', 
                     'dashboard', 'error', 'exito', 'advertencia', 'info', 'reloj', 'corazon', 'fuego', 'estrella', 'cohete', 'gem', 'rainbow']
    }
    
    for categoria, emoji_keys in categorias.items():
        value = ""
        for key in emoji_keys:
            if key in CUSTOM_EMOJIS:
                value += f"{CUSTOM_EMOJIS[key]} `:{key}:`\n"
        if value:
            embed.add_field(name=f"**{categoria}**", value=value, inline=True)
    
    await ctx.send(embed=embed)

@bot.command()
async def ping(ctx):
    """Comando de prueba con emojis"""
    latency = round(bot.latency * 1000)
    status_emoji = CUSTOM_EMOJIS['exito'] if latency < 100 else CUSTOM_EMOJIS['advertencia']
    await ctx.send(f"{status_emoji} **Pong!** {CUSTOM_EMOJIS['reloj']} Latencia: {latency}ms • {CUSTOM_EMOJIS['fuego']} {datetime.now().strftime('%H:%M:%S')}")

@bot.command()
async def ayuda(ctx):
    """Muestra ayuda con emojis"""
    embed = discord.Embed(
        title=f"{CUSTOM_EMOJIS['info']} **AYUDA - COMANDOS DISPONIBLES**",
        description=f"{CUSTOM_EMOJIS['cohete']} Sistema de gestión de Brainrots con Notion",
        color=0x00FFFF
    )
    
    commands = [
        (f"!brainrots [n]", f"{CUSTOM_EMOJIS['brainrot']} Muestra Brainrots con paginación"),
        (f"!dashboard", f"{CUSTOM_EMOJIS['dashboard']} Dashboard con estadísticas"),
        (f"!emojis", f"{CUSTOM_EMOJIS['rainbow']} Lista de emojis disponibles"),
        (f"!ping", f"{CUSTOM_EMOJIS['reloj']} Prueba de conectividad"),
        (f"!ayuda", f"{CUSTOM_EMOJIS['info']} Muestra esta ayuda")
    ]
    
    for cmd, desc in commands:
        embed.add_field(name=cmd, value=desc, inline=False)
    
    embed.set_footer(text=f"{CUSTOM_EMOJIS['estrella']} ¡Usa los emojis personalizados!")
    await ctx.send(embed=embed)

# Evento de cierre
@bot.event
async def close():
    await notion.close_session()
    clean_cache.stop()

if __name__ == "__main__":
    print(f"{CUSTOM_EMOJIS['cohete']} Iniciando bot con emojis personalizados...")
    bot.run(DISCORD_TOKEN)