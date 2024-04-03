import discord
from discord.ext import commands, tasks
import json
import asyncio
from datetime import datetime, timezone, timedelta
import getpass
import importlib
from collections import Counter
import ffmpeg
import os

server_id = 1189897915062296706
channel_id = 1192158425841414224
commands_channel_id = 1192158425841414224
any_channel = 'n'
tracking_start_date = datetime.now().strftime("%d %b %Y")
serverid = server_id

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='restart', description='Restart the Bot')
    @commands.has_permissions(administrator=True)
    async def restart(self, ctx):
        await ctx.send('Restarting...')
        for extension in bot.extensions.copy():
            bot.unload_extension(extension)
            bot.load_extension(extension)
        await ctx.send('Restart complete.')

    @commands.command(name='adminhelp', description='Admin command list')
    @commands.has_permissions(administrator=True)
    async def seenbothelp(self, ctx):
        if any_channel == 'n' and ctx.channel.id != commands_channel_id:
            await ctx.send("You can only use this command in the designated channel.")
            return
        else:
            help_embed = discord.Embed(title='ADMIN COMMAND LIST', description='List of all available admin commands and their descriptions', color=discord.Color.green())
            help_embed.add_field(name="Command", value="------\n/adminhelp\n/toggleonline\n/toggleidle\n/restart\n/toggleplayer\n/commandchannel", inline=True)
            help_embed.add_field(name="Alias", value="------\n\n/to\n/ti\n\n/tp\n/tcc", inline=True)
            help_embed.add_field(name="Description", value="------\nList all admin commands and descriptions.\nToggle online/offline updates. (admin only)\nToggle idle updates. (admin only)\nSoft Restart the bot. (admin only)\nToggle enable music player.\nToggle only command channel.", inline=True)
            await ctx.send(embed=help_embed)

    @commands.command(name='commandchannel', description='Commands in one channel only')
    @commands.has_permissions(administrator=True)
    async def command_channel(self, ctx):
        global any_channel
        if any_channel == 'n':
            any_channel = 'y'
            await ctx.send('**Command Channel Disabled.**')
        else:
            any_channel = 'n'
            await ctx.send('**Command Channel Enabled.**')

    @commands.command(name='toggleplayer', description='Toggle Music Player')
    @commands.has_permissions(administrator=True)
    async def toggle_player(self, ctx):
        global music_player
        if music_player == 'n':
            music_player = 'y'
            await ctx.send('**Music Player Enabled.**')
        else:
            music_player = 'n'
            await ctx.send('**Music Player Disabled.**')

    @commands.command(name='toggleonline', description='Toggle online notifications')
    @commands.has_permissions(administrator=True)
    async def toggle_updates(self, ctx):
        global show_updates
        if show_updates == 'n':
            show_updates = 'y'
            await ctx.send('**Now showing online/offline status updates.**')
        else:
            show_updates = 'n'
            await ctx.send('**online/offline status updates hidden.**')

    @commands.command(name='toggleidle', description='Toggle idle notifications')
    @commands.has_permissions(administrator=True)
    async def toggle_idle(self, ctx):
        global show_idle
        if show_idle == 'n':
            show_idle = 'y'
            await ctx.send('**Now showing idle status updates.**')
        else:
            show_idle = 'n'
            await ctx.send('**Idle status updates hidden.**')

    @commands.Cog.listener()
    async def on_ready(self):
        print('Admin cog is ready.')

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))