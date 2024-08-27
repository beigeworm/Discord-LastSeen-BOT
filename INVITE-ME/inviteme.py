import discord
from discord.ext import commands
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)
@bot.event
async def on_ready():
print(f'{bot.user} connected')
server = bot.get_guild(int(''))
invite_link = await server.text_channels[0].create_invite(max_age=0)
print(f'{invite_link}')
bot.run('')