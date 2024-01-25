import discord
import json
import asyncio
from datetime import datetime, timezone
from discord.ext import commands

bot_token = 'YOUR_BOT_TOKEN_HERE'
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)
bot.activity = discord.Game(name="/seen")

async def log_member_statuses(server):
    log_data = []

    for member in server.members:
        member_data = {
            'username': member.name,
            'display_name': member.display_name,
            'status': str(member.status)
        }
        log_data.append(member_data)

    with open(f'logs_{server.id}.json', 'w') as log_file:
        json.dump(log_data, log_file, indent=4)

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

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

    for server in bot.guilds:
        await log_member_statuses(server)
        await update_last_seen_online(server)

        bot.loop.create_task(update_statuses_loop(server))

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
        await ctx.send(f'**{user_identifier}** was last seen online at: `{last_seen_time}` ')
    except FileNotFoundError:
        await ctx.send('No last seen data available.')

async def update_statuses_loop(server):
    while True:
        previous_statuses = {}

        try:
            with open(f'logs_{server.id}.json', 'r') as log_file:
                previous_statuses = {entry['username']: entry['status'] for entry in json.load(log_file)}
        except FileNotFoundError:
            pass

        await log_member_statuses(server)

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

@bot.event
async def on_member_update(before, after):
    if before.status != after.status:
        server = after.guild
        await log_member_statuses(server)

bot.run(bot_token)
