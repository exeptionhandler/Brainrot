import discord
from discord.ext import commands
from models.brainrot import BrainrotCollection
from views.pagination import AdvancedPaginationView
from utils import emojis, formatters

class BrainrotCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.collection = BrainrotCollection()
    
    @commands.command()
    async def brainrots(self, ctx: commands.Context, items_per_page: int = 5):
        """Muestra Brainrots con paginación"""
        try:
            loading_msg = await ctx.send(f"{emojis.get_emoji('cargando')} Cargando Brainrots...")
            
            # Cargar datos
            data = await self.collection.load_from_notion()
            all_brainrots = self.collection.get_all()
            
            if not all_brainrots:
                await loading_msg.edit(content=f"{emojis.get_emoji('advertencia')} No hay Brainrots.")
                return
            
            # Crear páginas
            pages = []
            items_per_page = max(1, min(items_per_page, 5))
            
            for i in range(0, len(all_brainrots), items_per_page):
                page_brainrots = all_brainrots[i:i + items_per_page]
                embed = await self.create_brainrot_embed(page_brainrots)
                pages.append(embed)
            
            await loading_msg.delete()
            
            if pages:
                view = AdvancedPaginationView(pages)
                first_embed = pages[0]
                first_embed.set_footer(
                    text=f"{emojis.get_emoji('reloj')} Página 1/{len(pages)} • "
                         f"{emojis.get_emoji('brainrot')} Total: {len(all_brainrots)}"
                )
                await ctx.send(embed=first_embed, view=view)
            else:
                await ctx.send(f"{emojis.get_emoji('advertencia')} No hay datos para mostrar.")
            
        except Exception as e:
            print(f"Error en brainrots: {e}")
            try:
                await ctx.send(f"{emojis.get_emoji('error')} Error al cargar los datos.")
            except:
                pass  # Evitar errores en cascada
    
    async def create_brainrot_embed(self, brainrots: list) -> discord.Embed:
        embed = discord.Embed(
            title=f"{emojis.get_emoji('brainrot')} **BRAINROTS**", 
            color=0x00ffaa
        )
        
        for brainrot in brainrots:
            try:
                nombre = await brainrot.get_name()
                precio = await brainrot.get_price()
                rarezas = await brainrot.get_rarezas()
                efectos = await brainrot.get_efectos()
                vendido = await brainrot.is_vendido()
                cuenta = await brainrot.get_cuenta()
                
                field_value = f"{emojis.get_emoji('dinero')} **{precio}**\n"
                field_value += f"{emojis.get_emoji('rareza')} **{formatters.format_rareza_list(rarezas)}**\n"
                field_value += f"{emojis.get_emoji('efectos')} **{formatters.format_efectos_list(efectos)}**\n"
                
                status_emoji, status_text = formatters.format_status(vendido)
                field_value += f"{status_emoji} **{status_text}**\n"
                field_value += f"{emojis.get_emoji('cuenta')} **{cuenta}**"
                
                embed.add_field(name=f"**{nombre}**", value=field_value, inline=False)
                embed.add_field(name="\u200b", value="▬" * 30, inline=False)
                
            except Exception as e:
                print(f"Error procesando brainrot: {e}")
                continue
        
        return embed

async def setup(bot):
    await bot.add_cog(BrainrotCommands(bot))