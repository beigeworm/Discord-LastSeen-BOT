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
music_player = 'y'
tracking_start_date = datetime.now().strftime("%d %b %Y")
serverid = server_id

class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='play', description='Start Music Player')
    async def play(self, ctx, url):
        if any_channel == 'n' and ctx.channel.id != commands_channel_id:
            await ctx.send("You can only use this command in the designated channel.")
            return
        else:
            voice_channel = ctx.author.voice.channel
            if voice_channel:
                if music_player == 'y':
                    try:
                        await voice_channel.connect()
                        voice_client = ctx.guild.voice_client
                        os.system(f'youtube-dl --force-ipv4 -x --audio-format mp3 {url} -o temp.mp3')
                        await asyncio.sleep(3)
                        voice_client.play(discord.FFmpegPCMAudio('temp.mp3'), after=lambda e: print('done', e))
                        await ctx.send(f'> :musical_note:  Now playing...  :musical_note: ')
                        while voice_client.is_playing():
                            await asyncio.sleep(1)
                        os.remove('temp.mp3')
                        await voice_client.disconnect()
                    except Exception as e:
                        await ctx.send(f'An error occurred: {e}')
                        await voice_client.disconnect()
                else:
                    await ctx.send("Music player is disabled.")
            else:
                await ctx.send("You need to be in a voice channel to use this command.")
    
    @commands.command(name='stop', description='Stop Music Player')
    async def stop(self, ctx):
        voice_client = ctx.guild.voice_client
        if voice_client:
            if voice_client.is_playing():
                voice_client.stop()
                await ctx.send("Playback stopped.")
            else:
                await ctx.send("Nothing is playing.")
        else:
            await ctx.send("I'm not in a voice channel.")

    @commands.Cog.listener()
    async def on_ready(self):
        print('Music cog is ready.')

async def setup(bot):
    await bot.add_cog(MusicPlayer(bot))