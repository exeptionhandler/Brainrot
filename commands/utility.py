import discord
from discord.ext import commands
from utils import emojis

class UtilityCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx: commands.Context):
        """Comando de prueba"""
        latency = round(self.bot.latency * 1000)
        await ctx.send(f"{emojis.get_emoji('exito')} **Pong!** {emojis.get_emoji('reloj')} Latencia: {latency}ms")

    @commands.command()
    async def ayuda(self, ctx: commands.Context):
        """Muestra ayuda"""
        embed = discord.Embed(
            title=f"{emojis.get_emoji('info')} **AYUDA**",
            description="Comandos disponibles:",
            color=0x00FFFF
        )
        embed.add_field(name="!brainrots", value="Muestra la colección", inline=False)
        embed.add_field(name="!dashboard", value="Estadísticas", inline=False)
        embed.add_field(name="!ping", value="Prueba de conexión", inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UtilityCommands(bot))