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
show_idle = 'y'
show_updates = 'y'
tracking_start_date = datetime.now().strftime("%d %b %Y")
serverid = server_id

class MemberActivity(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='lastseen', description='User last seen info')
    async def last_seen(self, ctx, user_identifier: str):
        if any_channel == 'n' and ctx.channel.id != commands_channel_id:
            await ctx.send("You can only use this command in the designated channel.")
            return
        else:
            if user_mention := discord.utils.get(ctx.message.mentions, name=user_identifier):
                username = user_mention.name
                display_name = user_mention.display_name
            else:
                username = user_identifier
                display_name = user_identifier
        
                server_id = ctx.guild.id
                try:
                    with open(f'lastseen_{server_id}.json', 'r') as last_seen_file:
                        last_seen_data = json.load(last_seen_file)
                    last_seen_time = last_seen_data.get(username, last_seen_data.get(display_name, '`Not available` '))
                    if last_seen_time == 'Online Now':
                        await ctx.send(f'> :green_circle: **{user_identifier}** is currently online.')
                    else:
                        last_seen_timestamp = datetime.strptime(last_seen_time, '%Y-%m-%d %H:%M:%S UTC').replace(tzinfo=timezone.utc)
                        now_utc = datetime.now(timezone.utc)
                        time_difference = now_utc - last_seen_timestamp
                        time_difference_str = format_timedelta(time_difference)
                        await ctx.send(f'> **{user_identifier}** was last seen online at: `{last_seen_time}` '
                                       f'[`{time_difference_str}` ago]')
                except FileNotFoundError:
                    await ctx.send('No last seen data available.')

    @commands.command(name='totalonline', description='User total online time')
    async def total_online_time(self, ctx, user_identifier: str):
    
        if any_channel == 'n' and ctx.channel.id != commands_channel_id:
            await ctx.send("You can only use this command in the designated channel.")
            return
        else:
            server_id = ctx.guild.id
            try:
                with open('totaltime.json', 'r') as total_time_file:
                    total_time_data = json.load(total_time_file)
                
                display_name = user_identifier
                total_time_seconds = total_time_data.get(display_name, 0)
                total_time_str = format_timedelta(timedelta(seconds=total_time_seconds))
                await ctx.send(f'> Total online time for **{display_name}** : `{total_time_str}`')
            except FileNotFoundError:
                await ctx.send('No total online time data available.')
            
    @commands.command(name='totalactive', description='User total active time')
    async def total_active_time(self, ctx, user_identifier: str):
    
        if any_channel == 'n' and ctx.channel.id != commands_channel_id:
            await ctx.send("You can only use this command in the designated channel.")
            return
        else:
            server_id = ctx.guild.id
            try:
                with open('totalonlinetime.json', 'r') as total_time_file:
                    total_time_data = json.load(total_time_file)
                
                display_name = user_identifier
                total_time_seconds = total_time_data.get(display_name, 0)
                total_time_str = format_timedelta(timedelta(seconds=total_time_seconds))
                await ctx.send(f'> Total active time for **{display_name}** : `{total_time_str}`')
            except FileNotFoundError:
                await ctx.send('No total active time data available.')
    
    @commands.command(name='activeleaderboard', description='Total active time leaderboard')
    async def active_leaders(self, ctx):
        if any_channel == 'n' and ctx.channel.id != commands_channel_id:
            await ctx.send("You can only use this command in the designated channel.")
            return
        else:    
            try:
                with open('activeleaderboard.json', 'r') as total_time_file:
                    total_time_data = json.load(total_time_file)
                
                total_time_counter = Counter(total_time_data)
                top_10 = total_time_counter.most_common(10)
                leaderboard_message = "**Top 10 Most Active Members:**\n"
                for index, (display_name, total_time) in enumerate(top_10, start=1):
                    total_time_str = format_timedelta(timedelta(seconds=total_time))
                    leaderboard_message += f"{index}. {display_name} : `{total_time_str}`\n"
        
                leaderboard_message += f"\n"
                await ctx.send(leaderboard_message)
            except FileNotFoundError:
                await ctx.send('No total active time data available.')
    
    @commands.command(name='onlineleaderboard', description='Total online time leaderboard')
    async def active_leaders(self, ctx):
        if any_channel == 'n' and ctx.channel.id != commands_channel_id:
            await ctx.send("You can only use this command in the designated channel.")
            return
        else:
            try:
                with open('onlineleaderboard.json', 'r') as total_time_file:
                    total_time_data = json.load(total_time_file)
                
                total_time_counter = Counter(total_time_data)
                top_10 = total_time_counter.most_common(10)
                leaderboard_message = "**Top 10 Online Members:**\n"
                for index, (display_name, total_time) in enumerate(top_10, start=1):
                    total_time_str = format_timedelta(timedelta(seconds=total_time))
                    leaderboard_message += f"{index}. {display_name} : `{total_time_str}`\n"
        
                leaderboard_message += f"\n"
                await ctx.send(leaderboard_message)
            except FileNotFoundError:
                await ctx.send('No total online time data available.')

    @commands.command(name='seenhelp', description='List all commands and their descriptions')
    async def seenbothelp(self, ctx):
    
        if any_channel == 'n' and ctx.channel.id != commands_channel_id:
            await ctx.send("You can only use this command in the designated channel.")
            return
        else:
            help_embed = discord.Embed(title='SeenBOT  |  Information', description=f'SeenBOT tracks member activity and provides information/statistics on a given member, SeenBOT also has actvity leaderboards. Use the commands below.\n\n **Tracking started : {tracking_start_date}** \n\n[user] can be a username OR display name. (no @ symbol required)', color=discord.Color.green())
            help_embed.add_field(name="Command", value="------\n/seenhelp\n/lastseen [user]\n/totalonline [user]\n/totalactive [user]\n/activeleaderboard\n/onlineleaderboard\n/play [url]\n/stop", inline=True)
            help_embed.add_field(name="Alias", value="------\n\n/ls [user]\n/online [user]\n/active [user]\n/leaderboard\n\n/p [url]\n/s", inline=True)
            help_embed.add_field(name="Description", value="------\nList all commands and their descriptions.\nDisplay last seen time for a member.\nDisplay total online time for a member.\nDisplay total active time for a member.\nDisplay top 10 most active members.\nDisplay top 10 online members.\nPlay a song from YouTube.\nStop the current song.", inline=True)
            await ctx.send(embed=help_embed)

    @commands.Cog.listener()
    async def on_ready(self):
        print('Member cog is ready.')

async def setup(bot):
    await bot.add_cog(MemberActivity(bot))
