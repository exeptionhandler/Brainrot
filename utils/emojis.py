CUSTOM_EMOJIS = {
    'disponible': '<:yes:1409698306006843423>',
    'vendido': '<:no:1409698339590766677>',
    'cargando': '<a:loading:1409696840235880549>',
    'fire': '<:Fire:1409669192004931716>',
    'fireworks': '<:Fireworks:1409669176062382201>',
    # ... todos los emojis
}

EFECTO_EMOJIS = {
    'fire': 'fire',
    'spark': 'fireworks',
    # ... mapeo de efectos
}

RAREZA_EMOJIS = {
    'brainrot god': '👑',
    'secret': '🔒',
    # ... mapeo de rarezas
}

def get_efecto_emoji(efecto_name: str) -> str:
    efecto_lower = efecto_name.lower()
    for key, emoji_key in EFECTO_EMOJIS.items():
        if key in efecto_lower:
            return CUSTOM_EMOJIS.get(emoji_key, '✨')
    return '✨'

def get_rareza_emoji(rareza_name: str) -> str:
    rareza_lower = rareza_name.lower()
    for key, emoji in RAREZA_EMOJIS.items():
        if key in rareza_lower:
            return emoji
    return '⚪'

def get_emoji(key: str) -> str:
    return CUSTOM_EMOJIS.get(key, '')