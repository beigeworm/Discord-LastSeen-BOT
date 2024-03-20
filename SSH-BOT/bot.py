import discord
import paramiko
from discord.ext import commands

# Discord Bot Token
TOKEN = 'YOUR_DISCORD_BOT_TOKEN'

# SSH Credentials
SSH_HOST = 'YOUR_SSH_URL'
SSH_PORT = 22
SSH_USERNAME = 'kali'
SSH_PASSWORD = 'kali'

# ID of the allowed channel
ALLOWED_CHANNEL_ID = 1219248017421504553

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='', intents=intents)

# Create an SSH client object
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Global variable to track current directory
current_directory = '/home/kali'

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

# Define a check to restrict commands to a specific channel
def in_allowed_channel(ctx):
    return ctx.channel.id == ALLOWED_CHANNEL_ID

@bot.event
async def on_message(message):
    if message.author.bot:  # Ignore messages from bots
        return

    if message.content.startswith('cd '):  # Check if it's a 'cd' command
        await change_directory(message.content[len('cd '):].strip(), message)  # Extract directory and call function
        return

    if message.channel.id == ALLOWED_CHANNEL_ID:  # Check if it's in the allowed channel
        command = message.content  # Get the content of the message
        await execute_ssh_command(message, command)

async def execute_ssh_command(message, command):
    global current_directory
    try:
        await message.add_reaction("\u231B")
        # Connect to SSH host if not connected
        if not ssh_client.get_transport() or not ssh_client.get_transport().is_active():
            ssh_client.connect(hostname=SSH_HOST, port=SSH_PORT, username=SSH_USERNAME, password=SSH_PASSWORD)

        # Execute the command
        stdin, stdout, stderr = ssh_client.exec_command(f'cd {current_directory} && {command}')
        output = stdout.readlines()
        error = stderr.read().decode('utf-8')

        if output:
            # Send output in chunks
            chunk_size = 10
            for i in range(0, len(output), chunk_size):
                chunk = ''.join(output[i:i+chunk_size])
                await message.channel.send(f'```{chunk}```')
            # Add a reaction to indicate success
            await message.add_reaction("\u2705")
        elif error:
            await message.channel.send(f'```Error: {error}```')
            # Add a reaction to indicate failure
            await message.add_reaction("\u274C")
        else:
            # Add a reaction to indicate success (no output)
            await message.add_reaction("\u2705")
    except Exception as e:
        await message.channel.send(f'Error: {str(e)}')
        # Add a reaction to indicate failure
        await message.add_reaction("\u274C")

async def change_directory(directory, message):
    global current_directory
    try:
        # Connect to SSH host if not connected
        if not ssh_client.get_transport() or not ssh_client.get_transport().is_active():
            ssh_client.connect(hostname=SSH_HOST, port=SSH_PORT, username=SSH_USERNAME, password=SSH_PASSWORD)

        # Change current directory
        current_directory = directory
        # Add a reaction to indicate success
        await message.add_reaction("\u2705")
    except Exception as e:
        await message.channel.send(f'Error: {str(e)}')
        # Add a reaction to indicate failure
        await message.add_reaction("\u274C")

bot.run(TOKEN)
