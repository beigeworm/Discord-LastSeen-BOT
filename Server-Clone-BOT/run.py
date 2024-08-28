import discord
import asyncio
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Server to copy FROM
source_guild_id = 7003854220195389759 # Replace with the source guild ID 

# Server to copy TO
target_guild_id = 1277595292237168761  # Replace with the target guild ID


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')
    await bot.tree.sync()  # Sync the command tree with Discord
    print('Command tree synced.')
    
    source_guild = bot.get_guild(source_guild_id)
    target_guild = bot.get_guild(target_guild_id)

    if not source_guild or not target_guild:
        print("Invalid guild IDs. Please check the provided guild IDs.")
        return

    print(f'Source Guild: {source_guild.name} ({source_guild.id})')
    print(f'Target Guild: {target_guild.name} ({target_guild.id})')

# Utility function to clone roles and map them
async def clone_roles(source_guild, target_guild):
    role_mapping = {}  # Mapping of old roles to new roles

    for role in source_guild.roles:
        if role.is_default():
            role_mapping[role.id] = target_guild.default_role
            continue
        new_role = await target_guild.create_role(
            name=role.name,
            permissions=role.permissions,
            colour=role.colour,
            hoist=role.hoist,
            mentionable=role.mentionable,
        )
        role_mapping[role.id] = new_role
        await asyncio.sleep(0.9)
    
    return role_mapping

# Utility function to clone categories and channels
async def clone_channels(source_guild, target_guild, role_mapping):
    for category in source_guild.categories:
        new_category = await target_guild.create_category(
            name=category.name,
            overwrites={
                role_mapping.get(role.id): perms 
                for role, perms in category.overwrites.items() 
                if role_mapping.get(role.id) is not None
            },
        )
        await asyncio.sleep(0.9)

        for channel in category.channels:
            if isinstance(channel, discord.TextChannel):
                new_channel = await target_guild.create_text_channel(
                    name=channel.name,
                    category=new_category,
                    topic=channel.topic,
                    overwrites={
                        role_mapping.get(role.id): perms 
                        for role, perms in channel.overwrites.items() 
                        if role_mapping.get(role.id) is not None
                    },
                )
                await clone_messages(channel, new_channel)
            elif isinstance(channel, discord.VoiceChannel):
                await target_guild.create_voice_channel(
                    name=channel.name,
                    category=new_category,
                    overwrites={
                        role_mapping.get(role.id): perms 
                        for role, perms in channel.overwrites.items() 
                        if role_mapping.get(role.id) is not None
                    },
                )
            await asyncio.sleep(0.9)

# Utility function to split long messages into chunks
def split_message(content, max_length=2000):
    return [content[i:i+max_length] for i in range(0, len(content), max_length)]

# Utility function to clone messages
async def clone_messages(source_channel, target_channel):
    messages = []
    async for message in source_channel.history(limit=50, oldest_first=False):  # Get the latest messages first
        messages.append(message)

    for message in reversed(messages):  # Reverse the list to send messages in the correct order
        if message.embeds:  # Check if the message has embeds
            for embed in message.embeds:
                await target_channel.send(embed=embed)
        else:
            # Handle messages that are too long
            content = f"-# Username: `{message.author.name}` \n{message.content}"
            if len(content) > 2000:
                chunks = split_message(content)
                for chunk in chunks:
                    await target_channel.send(chunk)
            else:
                await target_channel.send(content)
        await asyncio.sleep(0.5)

@bot.tree.command(name="clone_guild")
@app_commands.checks.has_permissions(administrator=True)
async def clone_guild(interaction: discord.Interaction):
    source_guild = bot.get_guild(source_guild_id)
    target_guild = bot.get_guild(target_guild_id)

    if not source_guild or not target_guild:
        await interaction.response.send_message("Invalid guild IDs. Please check the provided guild IDs.", ephemeral=True)
        return

    await interaction.response.send_message(f"Starting the cloning process from `{source_guild.name}` to `{target_guild.name}`...", ephemeral=True)

    # Clone roles and create a role mapping
    role_mapping = await clone_roles(source_guild, target_guild)
    await interaction.followup.send("Roles cloned successfully!")

    # Clone channels and messages with the correct role mapping
    await clone_channels(source_guild, target_guild, role_mapping)
    await interaction.followup.send("Channels and messages cloned successfully!")

@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!", ephemeral=True)

bot.run('YOUR_BOT_TOKEN_HERE')
