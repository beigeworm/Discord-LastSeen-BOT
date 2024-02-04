import discord
import json
import asyncio
from discord.ext import commands
from datetime import datetime, timezone, timedelta
import getpass
import importlib

bot_token = input("Enter Your Bot Token: ")
server_id = input("Enter Your Server ID: ")
channel_id = input("Enter Your Channel ID: ")
show_idle = input("Post idle activity (Y/N): ")
show_updates = input("Post online/offline activity (Y/N): ")

serverid = server_id
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)
bot.activity = discord.Game(name="/seen")

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
    total_time_data[display_name] = total_time_data.get(display_name, 0) + time_delta.total_seconds()

    with open('totaltime.json', 'w') as total_time_file:
        json.dump(total_time_data, total_time_file, indent=4)
  
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
        await channel.send(f'> :red_circle: **{display_name}** Went Offline')

        if display_name in last_seen_data:
            start_time = last_seen_data.get(f"{display_name}_start_time")
            if start_time:
                last_seen_timestamp = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S UTC').replace(tzinfo=timezone.utc)
                time_delta = datetime.now(timezone.utc) - last_seen_timestamp
                await update_total_time(server_id, username, display_name, time_delta)
    else:
        last_seen_data[username] = 'Online Now'
        last_seen_data[display_name] = 'Online Now'
        last_seen_data[f"{display_name}_start_time"] = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
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
  
async def change_activity_loop():
    while True:
        bot.activity = discord.Game(name="/seen")
        await asyncio.sleep(60)
        
        bot.activity = discord.Game(name="/total")
        await asyncio.sleep(60)
  
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
                if status == 'offline' and previous_status != 'offline':
                    await log_last_seen(server.id, username, display_name, status)
                elif status != 'offline' and previous_status == 'offline':
                    await log_last_seen(server.id, username, display_name, status)
                elif status == 'idle' and previous_status != 'idle':
                    await channel.send(f'> :orange_circle: **{member.display_name}** Went AFK - Status:`{status}`')
                elif status == 'dnd' and previous_status != 'dnd':
                    await channel.send(f'> :no_entry: **{member.display_name}** Do Not Disturb - Status:`{status}`')
                elif status == 'online' and previous_status != 'online':
                    await channel.send(f'> :green_circle: **{member.display_name}** Woke Up - Status:`{status}`')
            if show_updates == 'y':
                if status == 'offline' and previous_status != 'offline':
                    await log_last_seen(server.id, username, display_name, status)
                elif status != 'offline' and previous_status == 'offline':
                    await log_last_seen(server.id, username, display_name, status)
                
        await asyncio.sleep(30)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    for server in bot.guilds:
        await log_status(server)
        await update_last_seen_online(server)
        await log_online_at_startup(server) 
        bot.loop.create_task(update_status_loop(server))
        bot.loop.create_task(change_activity_loop())

@bot.command(name='toggleidle')
async def toggle_idle(ctx):
    global show_idle
    if show_idle == 'n':
        show_idle = 'y'
        await ctx.send('**Now showing idle status updates.**')
    else:
        show_idle = 'n'
        await ctx.send('**Idle status updates hidden.**')
        
@bot.command(name='toggleonline')
async def toggle_updates(ctx):
    global show_updates
    if show_updates == 'n':
        show_updates = 'y'
        await ctx.send('**Now showing online/offline status updates.**')
    else:
        show_updates = 'n'
        await ctx.send('**online/offline status updates hidden.**')

@bot.command(name='seen')
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

@bot.command(name='total')
async def total_online_time(ctx, user_identifier: str):
    server_id = ctx.guild.id

    try:
        with open('totaltime.json', 'r') as total_time_file:
            total_time_data = json.load(total_time_file)
        
        display_name = user_identifier
        total_time_seconds = total_time_data.get(display_name, 0)

        total_time_str = format_timedelta(timedelta(seconds=total_time_seconds))
        await ctx.send(f'> Total online time for **{display_name}**: `{total_time_str}`')
    except FileNotFoundError:
        await ctx.send('No total online time data available.')

@bot.command(name='restart', hidden=True)
async def restart(ctx):
    await ctx.send('Restarting...')
    for extension in bot.extensions.copy():
        bot.unload_extension(extension)
        bot.load_extension(extension)
    await ctx.send('Restart complete.')

def format_timedelta(td):
    days, seconds = td.days, td.seconds
    hours = days * 24 + seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours} hrs, {minutes} mins, {seconds} secs"

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

@bot.event
async def on_message_delete(message):
    channel = bot.get_channel(channel_id)
    author = message.author
    content = message.content
    await channel.send(f'> :no_entry_sign: **{author.display_name}** Deleted the message: `{content}`')

bot.run(bot_token)
