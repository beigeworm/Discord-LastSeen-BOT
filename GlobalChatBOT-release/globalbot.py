import discord
from discord.ext import commands, tasks
from discord import app_commands
from dotenv import load_dotenv
import os
import json
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True 

bot = commands.Bot(command_prefix='!', intents=intents)

global_chat_channels = {}
user_message_times = defaultdict(list)
GLOBAL_CHAT_IDENTIFIER = ''
ANTI_SPAM_TOPIC_IDENTIFIER = '' 
MUTE_DIR = 'mutes'

if not os.path.exists(MUTE_DIR):
    os.makedirs(MUTE_DIR)

def load_muted_users(guild_id):
    file_path = os.path.join(MUTE_DIR, f'{guild_id}.json')
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return []

def save_muted_users(guild_id, data):
    file_path = os.path.join(MUTE_DIR, f'{guild_id}.json')
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await update_global_chat_channels()
    await update_activity_status()
    update_activity_status_task.start() 
    check_channels.start()
    prune_message_history.start()
    await bot.tree.sync()

@bot.event
async def on_guild_join(guild):
    print(f"Bot joined guild: {guild.name}")
    await update_global_chat_channels()
    await update_activity_status()

@bot.event
async def on_guild_remove(guild):
    print(f"Bot removed from guild: {guild.name}")
    global global_chat_channels
    global_chat_channels = {k: v for k, v in global_chat_channels.items() if v.guild.id != guild.id}
    mute_file_path = os.path.join(MUTE_DIR, f'{guild.id}.json')
    if os.path.exists(mute_file_path):
        os.remove(mute_file_path)
    await update_activity_status()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if isinstance(message.channel, discord.DMChannel):
        if message.content.strip().lower() == '/start':
            if message.channel.id not in global_chat_channels:
                global_chat_channels[message.channel.id] = message.channel
                await message.channel.send("Global chat started. Your messages will be shared with global channels.")
        elif message.content.strip().lower() == '/stop':
            if message.channel.id in global_chat_channels:
                del global_chat_channels[message.channel.id]
                await message.channel.send("Global chat stopped. Your messages will no longer be shared with global channels.")
        else:
            if message.channel.id in global_chat_channels:

                for channel_id, channel in global_chat_channels.items():
                    if channel_id != message.channel.id:
                        if isinstance(channel, discord.TextChannel):
                            muted_usernames = load_muted_users(channel.guild.id)
                            
                            if message.author.name in muted_usernames:
                                continue

                            try:
                                await channel.send(f"-# Username: `{message.author.name}` \n{message.content}")
                            except Exception as e:
                                print(f"Failed to send message to channel {channel.id} in guild {channel.guild.id}: {e}")
                        elif isinstance(channel, discord.DMChannel):
                            try:
                                await channel.send(f"From DM channel - Username: `{message.author.name}` \n{message.content}")
                            except Exception as e:
                                print(f"Failed to send message to DM channel {channel.id}: {e}")
        return

    if message.channel.topic and ANTI_SPAM_TOPIC_IDENTIFIER in message.channel.topic:
        now = datetime.now(timezone.utc)
        user_message_times[(message.guild.id, message.author.id)].append(now)

        user_message_times[(message.guild.id, message.author.id)] = [
            timestamp for timestamp in user_message_times[(message.guild.id, message.author.id)]
            if now - timestamp < timedelta(minutes=20)
        ]

        if len(user_message_times[(message.guild.id, message.author.id)]) > 50:
            muted_usernames = load_muted_users(message.guild.id)
            muted_usernames.append(message.author.name)
            save_muted_users(message.guild.id, muted_usernames)
            await message.channel.send(f"{message.author.mention} has been automatically muted for excessive messaging.")
            return

        if len(user_message_times[(message.guild.id, message.author.id)]) > 1 and \
                now - user_message_times[(message.guild.id, message.author.id)][-2] < timedelta(seconds=10):
            await message.channel.send(f":no_entry: {message.author.mention} **Message Not Sent** 10 second slow-mode enabled!")
            return
        if '@everyone' in message.content:
            await message.channel.send(f":no_entry: {message.author.mention} **Message Not Sent** Messages containing `@everyone` are not allowed!")
            return
        else:
            await message.add_reaction('\u2705')

    if message.guild:
        muted_usernames = load_muted_users(message.guild.id)
        
        if message.author.name in muted_usernames:
            await message.channel.send(f"{message.author.mention}, you are currently muted in this server.")
            return

    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return

    if message.channel.id in global_chat_channels:
        username_match = re.match(r"Username:\s*`(\w+)`", message.content)
        if username_match:
            username = username_match.group(1)
        else:
            username = message.author.name

        for channel_id, channel in global_chat_channels.items():
            if channel_id != message.channel.id:
                if isinstance(channel, discord.TextChannel):
                    muted_usernames = load_muted_users(channel.guild.id)
                    
                    if username in muted_usernames:
                        continue

                    try:
                        await channel.send(f"-# Username: `{message.author.name}` \n{message.content}")
                    except Exception as e:
                        print(f"Failed to send message to channel {channel.id} in guild {channel.guild.id}: {e}")
                elif isinstance(channel, discord.DMChannel):
                    try:
                        await channel.send(f"-# Username: `{message.author.name}` \n{message.content}")
                    except Exception as e:
                        print(f"Failed to send message to DM channel {channel.id}: {e}")



@bot.tree.command(name="mute")
@app_commands.checks.has_permissions(manage_messages=True)
async def mute(interaction: discord.Interaction, username: str):
    guild = interaction.guild
    muted_usernames = load_muted_users(guild.id)
    if username not in muted_usernames:
        muted_usernames.append(username)
        save_muted_users(guild.id, muted_usernames)
        await interaction.response.send_message(f"User `{username}` has been muted in this server.", ephemeral=True)
    else:
        await interaction.response.send_message(f"User `{username}` is already muted in this server.", ephemeral=True)


@bot.tree.command(name="unmute")
@app_commands.checks.has_permissions(manage_messages=True)
async def unmute(interaction: discord.Interaction, username: str):
    guild = interaction.guild
    muted_usernames = load_muted_users(guild.id)
    if username in muted_usernames:
        muted_usernames.remove(username)
        save_muted_users(guild.id, muted_usernames)
        await interaction.response.send_message(f"User `{username}` has been unmuted in this server.", ephemeral=True)
    else:
        await interaction.response.send_message(f"User `{username}` is not muted in this server.", ephemeral=True)


@bot.tree.command(name="mutelist")
@app_commands.checks.has_permissions(manage_messages=True)
async def mutelist(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    muted_usernames = load_muted_users(guild_id)
    
    if muted_usernames:
        muted_users_string = "\n".join(muted_usernames)
        await interaction.response.send_message(f"Muted users in this server:\n{muted_users_string}", ephemeral=True)
    else:
        await interaction.response.send_message("No users are currently muted in this server.", ephemeral=True)


async def update_global_chat_channels():
    global global_chat_channels
    global_chat_channels = {}

    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.topic and GLOBAL_CHAT_IDENTIFIER in channel.topic:
                global_chat_channels[channel.id] = channel
                print(f"Found global-chat channel: {channel.name} in guild: {guild.name}")

    for dm_channel_id in global_chat_channels:
        dm_channel = bot.get_channel(dm_channel_id)
        if isinstance(dm_channel, discord.DMChannel):
            global_chat_channels[dm_channel_id] = dm_channel
            print(f"Added DM global-chat channel: {dm_channel.id}")

async def update_activity_status():
    global_chat_channel_count = 0
    dm_channel_count = 0
    for channel_id, channel in global_chat_channels.items():
        if isinstance(channel, discord.TextChannel) or isinstance(channel, discord.DMChannel):
            global_chat_channel_count += 1
            if isinstance(channel, discord.DMChannel):
                dm_channel_count += 1
    activity = discord.Activity(type=discord.ActivityType.watching, 
                                name=f'{global_chat_channel_count} channels ({dm_channel_count} DM\'s)')
    await bot.change_presence(activity=activity)
    print(f"Activity updated to: Watching {global_chat_channel_count} channels ({dm_channel_count} DM\'s)")

@tasks.loop(minutes=1)
async def update_activity_status_task():
    await update_activity_status()

@tasks.loop(minutes=1)
async def check_channels():
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.topic and GLOBAL_CHAT_IDENTIFIER in channel.topic:
                if channel.id not in global_chat_channels:
                    global_chat_channels[channel.id] = channel
                    print(f"Added new global-chat channel: {channel.name} in guild: {guild.name}")

    for dm_channel_id in list(global_chat_channels.keys()):
        dm_channel = bot.get_channel(dm_channel_id)
        if isinstance(dm_channel, discord.DMChannel):
            if dm_channel.id not in global_chat_channels:
                global_chat_channels[dm_channel.id] = dm_channel
                print(f"Added new DM global-chat channel: {dm_channel.id}")

@tasks.loop(minutes=10)
async def prune_message_history():
    now = datetime.now(timezone.utc)
    prune_before = now - timedelta(minutes=20)
    for key in list(user_message_times.keys()):
        user_message_times[key] = [timestamp for timestamp in user_message_times[key] if timestamp > prune_before]

bot.run(TOKEN)
