import discord
import asyncio
import random
import os

TOKEN = 'YOUR_TOKEN_HERE'

GOODBYE_CHANNEL_ID = 1139206799128543342  # Replace with your channel ID
WELCOME_CHANNEL_ID = 1139206799128543342  # Replace with your channel ID

GOODBYE_MESSAGES = [
    "Goodbye {displayname}, you've been firewalled! \U0001F525",
    "Farewell {displayname}, your session has ended. \U0001F44B",
    "{displayname} has left the network. Disconnecting... \U0001F6E1",
    "So long {displayname}, you've been logged out. \U0001F510",
    "We're sad to see you go, {displayname}. It's a hard breach to fill! \U0001F6E0",
    "Goodbye {displayname}, hope you don't run into any bugs! \U0001F41B",
    "You've been encrypted out, {displayname}. Safe travels! \U0001F512",
    "{displayname}, your IP has been logged. Goodbye! \U0001F310",
    "Logging off, {displayname}. Thanks for the security updates! \U0001F4BE",
    "Goodbye {displayname}, you've been securely removed from the server! \U0001F5D1",
    "Looks like {displayname} triggered the exit script. Farewell! \U0001F4BB",
    "Goodbye {displayname}, hope your firewall is always strong! \U0001F6E1",
    "Logging out {displayname}. You've been a great defender! \U0001F9D1\U0000200D\U0001F4BB",
    "So long {displayname}, may your passwords always be secure! \U0001F511",
    "Farewell {displayname}, you've reached the end of the packet. \U0001F4E6",
    "{displayname} has been disconnected from the mainframe. Goodbye! \U0001F5A5",
    "Goodbye {displayname}, your session has timed out. \U0000231B",
    "{displayname}, you've been securely logged out. Safe travels! \U00002708\U0000FE0F",
    "So long {displayname}, don't forget to update your firmware! \U00002699",
    "Goodbye {displayname}, you've been safely uninstalled. \U0001F5D1"
]

WELCOME_MESSAGES = [
    "Welcome {displayname} to the secure zone! \U0001F510",
    "Glad to have you join our network, {displayname}! \U0001F310",
    "{displayname} just joined the firewall! \U0001F6E1",
    "Hello {displayname}, ready to patch some vulnerabilities? \U0001F6E0",
    "A warm (and secure) welcome to you, {displayname}! \U0001F512",
    "Welcome {displayname}! Let's debug some code together. \U0001F41E",
    "Hey {displayname}, welcome to the safest server on the net! \U0001F6E1",
    "Welcome {displayname}! You're now part of the cybersecurity crew! \U0001F468\U0000200D\U0001F4BB",
    "{displayname} just accessed the mainframe! \U0001F5A5",
    "Welcome {displayname}, let's encrypt some data! \U0001F512",
    "Hello {displayname}! Hope you're ready for some cybersecurity fun! \U0001F389",
    "Welcome {displayname}, your session is now secure! \U0001F513",
    "Glad you could join us, {displayname}. Lets keep the bugs out! \U0001F41B",
    "{displayname}, welcome to the most secure server around! \U0001F512",
    "Welcome {displayname}, your connection is now secure! \U0001F510",
    "{displayname} just passed the firewall and joined the server! \U0001F6E1",
    "Hello {displayname}, welcome to our encrypted chat! \U0001F511",
    "Welcome {displayname}! Ready to defend the network? \U0001F6E1",
    "{displayname} just logged in! Lets secure the server! \U0001F4BB",
    "Welcome {displayname}, lets protect the digital world together! \U0001F310"
]


intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')
    await check_member_status()

async def check_member_status():
    await client.wait_until_ready()
    while not client.is_closed():
        for guild in client.guilds:
            member_file = f"{guild.id}_members.txt"
            
            if not os.path.isfile(member_file):
                with open(member_file, "w") as file:
                    for member in guild.members:
                        file.write(f"{member.id}\n")
                continue

            with open(member_file, "r") as file:
                previous_members = file.read().splitlines()

            current_members = [member.id for member in guild.members]

            for member_id in previous_members:
                if int(member_id) not in current_members:
                    member = await client.fetch_user(member_id)
                    channel = client.get_channel(GOODBYE_CHANNEL_ID)
                    goodbye_message = random.choice(GOODBYE_MESSAGES).format(displayname=member.display_name)

            with open(member_file, "w") as file:
                for member in current_members:
                    file.write(f"{member}\n")

        await asyncio.sleep(180) 

@client.event
async def on_member_remove(member):
    channel = client.get_channel(GOODBYE_CHANNEL_ID)
    goodbye_message = random.choice(GOODBYE_MESSAGES).format(displayname=member.display_name)

    embed = discord.Embed(
        title="Goodbye \U0001F44B",
        description=goodbye_message,
        color=discord.Color.red()
    )
    embed.add_field(name="Display Name", value=member.display_name, inline=False)
    embed.add_field(name="Username", value=member.name, inline=False)
    embed.add_field(name="User ID", value=member.id, inline=False)

    await channel.send(embed=embed)

@client.event
async def on_member_join(member):
    channel = client.get_channel(WELCOME_CHANNEL_ID)
    welcome_message = random.choice(WELCOME_MESSAGES).format(displayname=member.display_name)

    embed = discord.Embed(
        title="Welcome \U0001F973",
        description=welcome_message,
        color=discord.Color.green()
    )
    embed.add_field(name="Display Name", value=member.display_name, inline=False)
    embed.add_field(name="Username", value=member.name, inline=False)
    embed.add_field(name="User ID", value=member.id, inline=False)

    await channel.send(embed=embed)

client.run(TOKEN)