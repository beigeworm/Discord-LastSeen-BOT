import discord
import json
import asyncio
from discord.ext import commands
from datetime import datetime, timezone, timedelta
import getpass
import importlib
from collections import Counter
import os
import ffmpeg

bot_token = input("Enter Your Bot Token: ")
server_id = input("Enter Your Server ID: ")
channel_id = input("Enter Your Channel ID: ")
show_idle = input("Post idle activity (Y/N): ")
show_updates = input("Post online/offline activity (Y/N): ")
music_player = 'y'

serverid = server_id
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)
bot.activity = discord.Game(name="/seenhelp")

async def log_online_at_startup(server):
    last_seen_data = {}
    for member in server.members:
        username = member.name
        display_name = member.display_name
        status = str(member.status)

        if status != 'offline':
            last_seen_data[username] = 'Online Now'
            last_seen_data[display_name] = 'Online Now'
            last_seen_data[f"{display_name}_start_time"] = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
            if status != 'idle':
                last_seen_data[f"{display_name}_active_start_time"] = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

    with open(f'lastseen_{server.id}.json', 'w') as last_seen_file:
        json.dump(last_seen_data, last_seen_file, indent=4)

async def log_status(server):
    logs_data = []
    for member in server.members:
        member_data = {
            'username': member.name,
            'display_name': member.display_name,
            'status': str(member.status)
        }
        logs_data.append(member_data)

    with open(f'seen_{server.id}.json', 'w') as log_file:
        json.dump(logs_data, log_file, indent=4)
  
async def update_total_time(server_id, username, display_name, time_delta):
    total_time_data = {}
    try:
        with open('totaltime.json', 'r') as total_time_file:
            total_time_data = json.load(total_time_file)
    except FileNotFoundError:
        pass

    total_time_data[username] = total_time_data.get(username, 0) + time_delta.total_seconds()
    if username != display_name:
        total_time_data[display_name] = total_time_data.get(display_name, 0) + time_delta.total_seconds()
    with open('totaltime.json', 'w') as total_time_file:
        json.dump(total_time_data, total_time_file, indent=4)

    total_time_data = {}
    try:
        with open('onlineleaderboard.json', 'r') as total_time_file:
            total_time_data = json.load(total_time_file)
    except FileNotFoundError:
        pass

    total_time_data[display_name] = total_time_data.get(display_name, 0) + time_delta.total_seconds()
    with open('onlineleaderboard.json', 'w') as total_time_file:
        json.dump(total_time_data, total_time_file, indent=4)
        
async def update_total_online_time(server_id, username, display_name, time_delta):
    total_online_time_data = {}
    try:
        with open('totalonlinetime.json', 'r') as total_online_time_file:
            total_online_time_data = json.load(total_online_time_file)
    except FileNotFoundError:
        pass

    total_online_time_data[username] = total_online_time_data.get(username, 0) + time_delta.total_seconds()
    if username != display_name:
        total_online_time_data[display_name] = total_online_time_data.get(display_name, 0) + time_delta.total_seconds()
    with open('totalonlinetime.json', 'w') as total_online_time_file:
        json.dump(total_online_time_data, total_online_time_file, indent=4)
    
    total_online_time_data = {}
    try:
        with open('activeleaderboard.json', 'r') as total_online_time_file:
            total_online_time_data = json.load(total_online_time_file)
    except FileNotFoundError:
        pass

    total_online_time_data[display_name] = total_online_time_data.get(display_name, 0) + time_delta.total_seconds()
    with open('activeleaderboard.json', 'w') as total_online_time_file:
        json.dump(total_online_time_data, total_online_time_file, indent=4)


async def log_last_active(server_id, username, display_name, status):
    last_seen_data = {}
    channel = bot.get_channel(channel_id)
    try:
        with open(f'lastseen_{server_id}.json', 'r') as last_seen_file:
            last_seen_data = json.load(last_seen_file)
    except FileNotFoundError:
        pass

    if status == 'idle' or status == 'online':
        timestamp_utc = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        last_seen_data[username] = timestamp_utc
        last_seen_data[display_name] = timestamp_utc  
        start_time = last_seen_data.get(f"{display_name}_active_start_time")
        if start_time:
            last_seen_timestamp = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S UTC').replace(tzinfo=timezone.utc)
            time_delta = datetime.now(timezone.utc) - last_seen_timestamp
            if status == 'idle':
                await update_total_online_time(server_id, username, display_name, time_delta)
              
    last_seen_data[f"{display_name}_active_start_time"] = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    with open(f'lastseen_{server_id}.json', 'w') as last_seen_file:
        json.dump(last_seen_data, last_seen_file, indent=4) 
    with open(f'lastseen_{serverid}.json', 'w') as last_seen_file:
        json.dump(last_seen_data, last_seen_file, indent=4)

  
async def log_last_seen(server_id, username, display_name, status):
    last_seen_data = {}
    channel = bot.get_channel(channel_id)
    try:
        with open(f'lastseen_{server_id}.json', 'r') as last_seen_file:
            last_seen_data = json.load(last_seen_file)
    except FileNotFoundError:
        pass

    if status == 'offline':
        timestamp_utc = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        last_seen_data[username] = timestamp_utc
        last_seen_data[display_name] = timestamp_utc
        if show_updates == 'y':
            await channel.send(f'> :red_circle: **{display_name}** Went Offline')

        if display_name in last_seen_data:
            start_time = last_seen_data.get(f"{display_name}_start_time")
            if start_time:
                last_seen_timestamp = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S UTC').replace(tzinfo=timezone.utc)
                time_delta = datetime.now(timezone.utc) - last_seen_timestamp
                await update_total_time(server_id, username, display_name, time_delta)
                
                if display_name in last_seen_data:
                    start_time = last_seen_data.get(f"{display_name}_active_start_time")
                    if start_time:
                        last_seen_timestamp = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S UTC').replace(tzinfo=timezone.utc)
                        time_delta = datetime.now(timezone.utc) - last_seen_timestamp
                        await update_total_online_time(server_id, username, display_name, time_delta)
                
    else:
        last_seen_data[username] = 'Online Now'
        last_seen_data[display_name] = 'Online Now'
        last_seen_data[f"{display_name}_start_time"] = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        last_seen_data[f"{display_name}_active_start_time"] = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        if show_updates == 'y':
            await channel.send(f'> :green_circle: **{display_name}** Is Now Online - Status:`{status}`')

    with open(f'lastseen_{server_id}.json', 'w') as last_seen_file:
        json.dump(last_seen_data, last_seen_file, indent=4)   
    with open(f'lastseen_{serverid}.json', 'w') as last_seen_file:
        json.dump(last_seen_data, last_seen_file, indent=4)

async def update_last_seen_online(server):
    last_seen_data = {}
    try:
        with open(f'lastseen_{server.id}.json', 'r') as last_seen_file:
            last_seen_data = json.load(last_seen_file)
    except FileNotFoundError:
        pass

    for member in server.members:
        username = member.name
        display_name = member.display_name
        status = str(member.status)

        if status != 'offline':
            last_seen_data[username] = 'Online Now'
            last_seen_data[display_name] = 'Online Now'

    with open(f'lastseen_{server.id}.json', 'w') as last_seen_file:
        json.dump(last_seen_data, last_seen_file, indent=4)
    with open(f'lastseen_{server_id}.json', 'w') as last_seen_file:
        json.dump(last_seen_data, last_seen_file, indent=4)
  
async def update_status_loop(server):
    while True:
        previous_statuses = {}
        channel = bot.get_channel(channel_id)
        try:
            with open(f'seen_{server.id}.json', 'r') as log_file:
                previous_statuses = {entry['username']: entry['status'] for entry in json.load(log_file)}
        except FileNotFoundError:
            pass

        await log_status(server)
        for member in server.members:
            username = member.name
            display_name = member.display_name
            status = str(member.status)
            previous_status = previous_statuses.get(username, 'offline')
            if show_idle == 'y':
                if status == 'offline' and previous_status == 'idle':
                    await log_last_active(server.id, username, display_name, status)
                    await log_last_seen(server.id, username, display_name, status)
                elif status == 'offline' and previous_status != 'offline':
                    await log_last_seen(server.id, username, display_name, status)                      
                elif status != 'offline' and previous_status == 'offline':
                    await log_last_seen(server.id, username, display_name, status)
                elif status == 'idle' and previous_status != 'idle':
                    await log_last_active(server.id, username, display_name, status)
                    await channel.send(f'> :orange_circle: **{member.display_name}** Went AFK - Status:`{status}`')
                elif status == 'dnd' and previous_status != 'dnd':
                    await channel.send(f'> :no_entry: **{member.display_name}** Do Not Disturb - Status:`{status}`')
                elif status == 'online' and previous_status != 'online':
                    await log_last_active(server.id, username, display_name, status)
                    await channel.send(f'> :green_circle: **{member.display_name}** Woke Up - Status:`{status}`')
            else:
                if status == 'offline' and previous_status == 'idle':
                    await log_last_active(server.id, username, display_name, status)
                    await log_last_seen(server.id, username, display_name, status)
                elif status == 'offline' and previous_status != 'offline':
                    await log_last_seen(server.id, username, display_name, status)
                elif status != 'offline' and previous_status == 'offline':
                    await log_last_seen(server.id, username, display_name, status)
                elif status == 'idle' and previous_status != 'idle':
                    await log_last_active(server.id, username, display_name, status)
                elif status == 'online' and previous_status != 'online':
                    await log_last_active(server.id, username, display_name, status)
        await asyncio.sleep(30)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    for server in bot.guilds:
        await log_status(server)
        await update_last_seen_online(server)
        await log_online_at_startup(server) 
        bot.loop.create_task(update_status_loop(server))

@bot.command(name='toggleidle', aliases=['ti'])
@commands.has_permissions(administrator=True)
async def toggle_idle(ctx):
    global show_idle
    if show_idle == 'n':
        show_idle = 'y'
        await ctx.send('**Now showing idle status updates.**')
    else:
        show_idle = 'n'
        await ctx.send('**Idle status updates hidden.**')
        
@bot.command(name='toggleonline', aliases=['to'])
@commands.has_permissions(administrator=True)
async def toggle_updates(ctx):
    global show_updates
    if show_updates == 'n':
        show_updates = 'y'
        await ctx.send('**Now showing online/offline status updates.**')
    else:
        show_updates = 'n'
        await ctx.send('**online/offline status updates hidden.**')

@bot.command(name='lastseen', aliases=['ls'])
async def last_seen(ctx, user_identifier: str):
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

@bot.command(name='totalonline', aliases=['online'])
async def total_online_time(ctx, user_identifier: str):
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
        
@bot.command(name='totalactive', aliases=['active'])
async def total_online_time(ctx, user_identifier: str):
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

@bot.command(name='activeleaderboard', aliases=['leaderboard'])
async def active_leaders(ctx):
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

@bot.command(name='onlineleaderboard')
async def active_leaders(ctx):
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

@bot.command(name='restart')
@commands.has_permissions(administrator=True)
async def restart(ctx):
    await ctx.send('Restarting...')
    for extension in bot.extensions.copy():
        bot.unload_extension(extension)
        bot.load_extension(extension)
    await ctx.send('Restart complete.')

@bot.command(name='seenhelp', help='List all commands and their descriptions')
async def seenbothelp(ctx):
    help_embed = discord.Embed(title='SeenBOT  |  Information', description='SeenBOT tracks member activity and provides information/statistics on a given member, SeenBOT also has actvity leaderboards. Use the commands below.\n\n **Tracking started : 13th Feb 2024** \n\n[user] can be a username OR display name. (no @ symbol required)', color=discord.Color.green())

    help_embed.add_field(name="Command", value="------\n/seenhelp\n/lastseen [user]\n/totalonline [user]\n/totalactive [user]\n/activeleaderboard\n/onlineleaderboard\n/play [url]\n/stop", inline=True)
    help_embed.add_field(name="Alias", value="------\n\n/ls [user]\n/online [user]\n/active [user]\n/leaderboard\n\n/p [url]\n/s", inline=True)
    help_embed.add_field(name="Description", value="------\nList all commands and their descriptions.\nDisplay last seen time for a member.\nDisplay total online time for a member.\nDisplay total active time for a member.\nDisplay top 10 most active members.\nDisplay top 10 online members.\nPlay a song from YouTube.\nStop the current song.", inline=True)
    await ctx.send(embed=help_embed)

@bot.command(name='adminhelp')
@commands.has_permissions(administrator=True)
async def seenbothelp(ctx):
    help_embed = discord.Embed(title='ADMIN COMMAND LIST', description='List of all available admin commands and their descriptions', color=discord.Color.green())

    help_embed.add_field(name="Command", value="------\n/adminhelp\n/toggleonline\n/toggleidle\n/restart\n/toggleplayer", inline=True)
    help_embed.add_field(name="Alias", value="------\n\n/to\n/ti\n\n/tp", inline=True)
    help_embed.add_field(name="Description", value="------\nList all admin commands and descriptions.\nToggle online/offline updates. (admin only)\nToggle idle updates. (admin only)\nSoft Restart the bot. (admin only)\nToggle enable music player.", inline=True)
    await ctx.send(embed=help_embed)

def format_timedelta(td):
    days, seconds = td.days, td.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours} hrs, {minutes} mins, {seconds} secs"

@bot.command(name='toggleplayer', aliases=['tp'])
@commands.has_permissions(administrator=True)
async def toggle_player(ctx):
    global music_player
    if music_player == 'n':
        music_player = 'y'
        await ctx.send('**Music player enabled.**')
    else:
        music_player = 'n'
        await ctx.send('**Music player disabled.**')

@bot.command(name='play', aliases=['p'])
async def play(ctx, url):
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

@bot.command(name='stop', aliases=['s'])
async def stop(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client:
        if voice_client.is_playing():
            voice_client.stop()
            await ctx.send("Playback stopped.")
        else:
            await ctx.send("Nothing is playing.")
    else:
        await ctx.send("I'm not in a voice channel.")

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel != after.channel:
        if after.channel is not None:
            channel = bot.get_channel(channel_id)
            await channel.send(f'> :mega: **{member.display_name}** Joined voice channel: `{after.channel.name}`')
        elif before.channel is not None:
            channel = bot.get_channel(channel_id)
            await channel.send(f'> :mega: **{member.display_name}** Left voice channel: `{before.channel.name}`')

@bot.event
async def on_member_update(before, after):
    if before.status != after.status:
        server = after.guild
        await log_member_statuses(server)
        await log_status(server)
        if after.status != 'idle':
            await update_total_online_time(server.id, after.name, after.display_name, timedelta(seconds=30))  

@bot.event
async def on_message_delete(message):
    channel = bot.get_channel(channel_id)
    author = message.author
    content = message.content
    await channel.send(f'> :no_entry_sign: DELETED MESSAGE :no_entry_sign: Member: **{author.display_name}** Content: `{content}`')

bot.run(bot_token)
