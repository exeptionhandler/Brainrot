import discord
from discord.ext import commands
from models.brainrot import BrainrotCollection
from utils import emojis

class DashboardCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.collection = BrainrotCollection()

    @commands.command()
    async def dashboard(self, ctx: commands.Context):
        """Muestra el dashboard de estadísticas"""
        try:
            await ctx.send(f"{emojis.get_emoji('cargando')} Generando dashboard...")
        except Exception as e:
            await ctx.send(f"{emojis.get_emoji('error')} Error: {str(e)}")

async def setup(bot):
    await bot.add_cog(DashboardCommands(bot))