import discord
import json
import asyncio
from discord.ext import commands
from datetime import datetime, timezone, timedelta
import getpass

bot_token = input("Enter Your Bot Token: ")
server_id = int(input("Enter Your Server ID: "))
channel_id = int(input("Enter Your Channel ID: "))

# Alternative way (remove above)
# bot_token = 'your-bot-token'
# server_id = 1234567890123456
# channel_id = 1234567890123456

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

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
                await channel.send(f'> **{member.display_name}** Changed status to: `{status}`')
                previous_statuses[username].update({'status': status})
                continue

            if status == 'dnd' and status != previous_status:
                channel = bot.get_channel(channel_id)
                await channel.send(f'> **{member.display_name}** Changed status to: `do not disturb`')
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
                    offline_message = f'> **{display_name}** Changed status to: `{status}` - Total online time:`{str(offline_duration).split(".")[0]}`'
                    await channel.send(offline_message)
                elif status_changed_time is not None:
                    await channel.send(f'> **{display_name}** Changed status to: `{status}`')

                previous_statuses[username].update({'status': status, 'last_online_time': last_online_time, 'status_changed_time': datetime.now()})
        await asyncio.sleep(10)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')

    for server in bot.guilds:
        await log_member_statuses(server)

        bot.loop.create_task(update_statuses_loop(server))

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel != after.channel:
        if after.channel is not None:
            channel = bot.get_channel(channel_id)
            await channel.send(f'> **{member.display_name}** Joined voice channel: `{after.channel.name}`')
        elif before.channel is not None:
            channel = bot.get_channel(channel_id)
            await channel.send(f'> **{member.display_name}** Left voice channel: `{before.channel.name}`')

@bot.event
async def on_member_update(before, after):
    if before.status != after.status:
        server = after.guild
        await log_member_statuses(server)

@bot.event
async def on_message_delete(message):
    channel = bot.get_channel(channel_id)
    author = message.author
    content = message.content
    await channel.send(f'> **{author.display_name}** Deleted the message: `{content}`')

bot.run(bot_token)
