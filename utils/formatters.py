from typing import List, Any, Dict
from . import emojis

def format_price(price: float) -> str:
    return f"{price:,.0f} US$"

def format_rareza_list(rareza_list: List[str]) -> str:
    if not rareza_list or rareza_list == 'N/A':
        return "⚪ Sin rareza"
    
    formatted = []
    for rareza in rareza_list:
        emoji = emojis.get_rareza_emoji(rareza)
        formatted.append(f"{emoji} {rareza}")
    return " ".join(formatted)

def format_efectos_list(efectos_list: List[str]) -> str:
    if not efectos_list or efectos_list == 'N/A':
        return f"{emojis.get_emoji('efectos')} Sin efectos"
    
    formatted = []
    for efecto in efectos_list:
        emoji = emojis.get_efecto_emoji(efecto)
        formatted.append(f"{emoji} {efecto}")
    return " ".join(formatted)

def format_status(vendido: bool) -> tuple:
    emoji = emojis.get_emoji('vendido') if vendido else emojis.get_emoji('disponible')
    text = "Vendido" if vendido else "Disponible"
    return emoji, text