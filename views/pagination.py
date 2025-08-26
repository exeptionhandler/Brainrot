import discord
from discord.ui import Button, View
from typing import List

class AdvancedPaginationView(View):
    def __init__(self, pages: List[discord.Embed], timeout: int = 180):
        super().__init__(timeout=timeout)
        self.pages = pages
        self.current_page = 0
        self.total_pages = len(pages)
        self.message = None
        
    async def update_embed(self, interaction: discord.Interaction):
        embed = self.pages[self.current_page]
        from utils.emojis import get_emoji
        embed.set_footer(text=f"{get_emoji('reloj')} Página {self.current_page + 1}/{self.total_pages} • ⏹️ para cerrar")
        
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