import discord
from discord.ext import commands, tasks
from config import Config
from utils.cache import cache_manager
from services.notion_client import notion_client

# Validar configuración
Config.validate()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Tarea automática para limpiar caché
@tasks.loop(minutes=30)
async def clean_cache():
    cache_manager.clear_relation_cache()
    print("🧹 Caché limpiada")

@bot.event
async def on_ready():
    print(f'{bot.user} se ha conectado a Discord! 🚀')
    clean_cache.start()
    
    # Cargar comandos modularizados
    try:
        await bot.load_extension('commands.brainrots')
        await bot.load_extension('commands.dashboard')
        await bot.load_extension('commands.utility')
        print("✅ Comandos cargados correctamente")
    except Exception as e:
        print(f"❌ Error cargando comandos: {e}")
    try:
        synced = await bot.tree.sync()
        print(f"🔗 Comandos slash sincronizados: {len(synced)}")
    except Exception as e:
        print(f"⚠️ Error sincronizando comandos slash: {e}")

@bot.event
async def on_close():
    await notion_client.close_session()
    clean_cache.stop()
    print("👋 Bot desconectado")

if __name__ == "__main__":
    bot.run(Config.DISCORD_TOKEN)