# ==================== Discord Message Backupper =========================
# SYNOPSIS
# Uses powershell along with Discord's API to retrieve all messages from all channels visible to the BOT

# USAGE
# 1. Run script and enter your bot token
# 2. Messages will be saved to text files in the same directory as the script

import discord
import asyncio
import re

# Define a function to format timestamps
def format_timestamp(timestamp):
    # Replace 'T' with a space and remove fractions of a second and timezone offset
    formatted_timestamp = re.sub(r'T', ' ', timestamp)
    formatted_timestamp = re.sub(r'\.\d+(\+|-)\d{2}:\d{2}$', '', formatted_timestamp)
    return formatted_timestamp

# Define a function to save data to a file
def save_to_file(filename, content):
    with open(filename, 'a', encoding='utf-8') as file:
        file.write(content + '\n')

# Asynchronous function to process messages in a channel
async def process_messages(channel, guild_name, channel_name):
    filename = f"{guild_name} - {channel_name}.txt"
    async for message in channel.history(limit=None):
        formatted_timestamp = format_timestamp(str(message.created_at))
        content = f"{formatted_timestamp} - {message.author.name}: {message.content}"
        save_to_file(filename, content)

# Asynchronous function to process voice channel history (join/leave)
async def process_voice_history(channel, guild_name, channel_name):
    filename = f"{guild_name} - {channel_name} - voice-history.txt"
    # Add code here to retrieve and process voice channel join/leave history
    # For example, using a bot event to track voice state updates
    # and save join/leave events to the file.

# Main function to retrieve data from Discord
async def main(token):
    # Initialize the Discord client
    client = discord.Client(intents=discord.Intents.all())

    @client.event
    async def on_ready():
        print(f"Logged in as {client.user.name}")

        # Iterate through each guild (server) the bot is part of
        for guild in client.guilds:
            guild_name = guild.name

            # Iterate through each channel in the guild
            for channel in guild.channels:
                # Process text channels
                if isinstance(channel, discord.TextChannel):
                    channel_name = channel.name
                    await process_messages(channel, guild_name, channel_name)

                # Process voice channels (e.g., tracking join/leave history)
                elif isinstance(channel, discord.VoiceChannel):
                    channel_name = channel.name
                    await process_voice_history(channel, guild_name, channel_name)

        # Close the client when done
        await client.close()

    # Run the client
    await client.start(token)

# Run the script with your bot token
if __name__ == "__main__":
    token = "YOUR_BOT_TOKEN_HERE"
    asyncio.run(main(token))
