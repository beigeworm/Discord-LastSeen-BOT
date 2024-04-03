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

bot_token = 'YOUR_BOT_TOKEN_HERE'
server_id = 1189897915062296706
channel_id = 1192158425841414224
commands_channel_id = 1192158425841414224
any_channel = 'n'
show_idle = 'y'
show_updates = 'y'
music_player = 'y'
tracking_start_date = datetime.now().strftime("%d %b %Y")
serverid = server_id

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)
bot.activity = discord.Game(name="/seenhelp")

def setup(bot):
    bot.add_cog(MemberActivity(bot))
    bot.add_cog(MusicPlayer(bot))
    bot.add_cog(AdminCommands(bot))

def format_timedelta(td):
    days, seconds = td.days, td.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours} hrs, {minutes} mins, {seconds} secs"

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
    global tracking_start_date
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

    # Load cogs
    await bot.wait_until_ready()
    await load_cogs(bot)

    for server in bot.guilds:
        await log_status(server)
        await update_last_seen_online(server)
        await log_online_at_startup(server)
        if not tracking_start_date:
            tracking_start_date = datetime.now().strftime("%dth %b %Y")
            with open('tracking_start_date.txt', 'w') as start_date_file:
                start_date_file.write(tracking_start_date)
        bot.loop.create_task(update_status_loop(server))

async def load_cogs(bot):
    try:
        for filename in os.listdir('./cogs'):
            if (
                filename.endswith('.py')
                and filename != '__init__.py'
                and filename != 'utils.py'
            ):
                try:
                    await bot.load_extension(f'cogs.{filename[:-3]}')
                    print(f"Loaded {filename} cog successfully.")
                except Exception as e:
                    print(f'Failed to load cog: {e}')
    except Exception as e:
        print(f'Failed to load cog: {e}')

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