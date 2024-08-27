import discord
from discord.ext import commands
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)
@bot.event
async def on_ready():
print(f'{bot.user} connected')
server = bot.get_guild(123456789)
member = discord.utils.get(server.members, id=1234)
await member.unban()
print(f'finished')
bot.run('')