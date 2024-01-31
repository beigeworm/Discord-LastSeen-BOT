import discord
import json
import asyncio
from discord.ext import commands
from datetime import datetime, timezone, timedelta
import getpass

bot_token = input("Enter Your Bot Token: ")
server_id = int(input("Enter Your Server ID: "))
channel_id = int(input("Enter Your Channel ID: "))

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)
bot.activity = discord.Game(name="/seen")

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
        
async def log_last_seen(server_id, username, display_name, status):
    last_seen_data = {}

    try:
        with open(f'lastseen_{server_id}.json', 'r') as last_seen_file:
            last_seen_data = json.load(last_seen_file)
    except FileNotFoundError:
        pass

    if status == 'offline':
        timestamp_utc = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        last_seen_data[username] = timestamp_utc
        last_seen_data[display_name] = timestamp_utc
        print(f'{display_name} went offline')
    else:
        last_seen_data[username] = 'Online Now'
        last_seen_data[display_name] = 'Online Now'
        print(f'{display_name} is online')

    with open(f'lastseen_{server_id}.json', 'w') as last_seen_file:
        json.dump(last_seen_data, last_seen_file, indent=4)

async def log_member_statuses(server):
    log_data = []

    for member in server.members:
        member_data = {
            'username': member.name,
            'display_name': member.display_name,
            'status': str(member.status),
            'last_online_time': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
            'status_changed_time': None
        }
        log_data.append(member_data)

    with open(f'logs_{server.id}.json', 'w') as log_file:
        json.dump(log_data, log_file, indent=4)

async def get_previous_statuses(server):
    try:
        with open(f'logs_{server.id}.json', 'r') as log_file:
            return {entry['username']: entry for entry in json.load(log_file)}
    except FileNotFoundError:
        return {}
    
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
            print(f'{member.name} Online Now')

    with open(f'lastseen_{server.id}.json', 'w') as last_seen_file:
        json.dump(last_seen_data, last_seen_file, indent=4)
        
        
async def update_status_loop(server):
    while True:
        previous_statuses = {}

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

            if status == 'offline' and previous_status != 'offline':
                await log_last_seen(server.id, username, display_name, status)
            elif status != 'offline' and previous_status == 'offline':
                await log_last_seen(server.id, username, display_name, status)

        await asyncio.sleep(60)

async def update_statuses_loop(server):
    previous_statuses = await get_previous_statuses(server)

    for member in server.members:
        username = member.name
        display_name = member.display_name
        status = str(member.status)

        last_online_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        previous_statuses.setdefault(username, {'status': 'offline', 'last_online_time': last_online_time, 'status_changed_time': None})
        previous_statuses[username].update({'status': status, 'last_online_time': last_online_time, 'status_changed_time': datetime.now()})

    while True:
        await log_member_statuses(server)

        for member in server.members:
            username = member.name
            display_name = member.display_name
            status = str(member.status)

            previous_status_data = previous_statuses[username]
            previous_status = previous_status_data['status']
            if status == 'idle' and status != previous_status:
                channel = bot.get_channel(channel_id)
                previous_statuses[username].update({'status': status})
                continue

            if status == 'dnd' and status != previous_status:
                channel = bot.get_channel(channel_id)
                await channel.send(f'> :no_entry: **{member.display_name}** Changed status to: `do not disturb`')
                previous_statuses[username].update({'status': status})
                continue

            last_online_time = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
            previous_last_online_time = previous_status_data['last_online_time']
            status_changed_time = previous_status_data['status_changed_time']

            if status != previous_status:
                channel = bot.get_channel(channel_id)

                if status == 'offline' and status_changed_time is not None:
                    last_online_timestamp = datetime.strptime(previous_last_online_time, '%Y-%m-%d %H:%M:%S %Z').replace(tzinfo=timezone.utc)
                    offline_duration = datetime.now(timezone.utc) - last_online_timestamp
                    offline_message = f'> :red_circle: **{display_name}** Changed status to: `{status}` - Total online time:`{str(offline_duration).split(".")[0]}`'
                    await channel.send(offline_message)
                elif status_changed_time is not None:
                    await channel.send(f'> :green_circle: **{display_name}** Changed status to: `{status}`')

                previous_statuses[username].update({'status': status, 'last_online_time': last_online_time, 'status_changed_time': datetime.now()})
        await asyncio.sleep(60)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

    for server in bot.guilds:
        await log_member_statuses(server)
        await log_status(server)
        await update_last_seen_online(server)

        bot.loop.create_task(update_statuses_loop(server))
        bot.loop.create_task(update_status_loop(server))


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
            await ctx.send(f' :green_circle: **{user_identifier}** is currently online.')
        else:
            last_seen_timestamp = datetime.strptime(last_seen_time, '%Y-%m-%d %H:%M:%S UTC').replace(tzinfo=timezone.utc)
            now_utc = datetime.now(timezone.utc)
            
            time_difference = now_utc - last_seen_timestamp
            time_difference_str = format_timedelta(time_difference)
            
            await ctx.send(f'**{user_identifier}** was last seen online at: `{last_seen_time}` '
                           f'(Approximately {time_difference_str} ago)')
    except FileNotFoundError:
        await ctx.send('No last seen data available.')

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
