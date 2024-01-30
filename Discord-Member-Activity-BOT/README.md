# Discord-Member-Activity-BOT
A simple python script for a discord bot that saves server member activity to a channel of your choice.

This script will message a channel in a server members activity (status, VC activity, deleted messages).
Can be used in multiple servers with one server for update massages.

**SETUP**
- Create a BOT here: https://discord.com/developers/applications
- Go to your new Bot, then `Oauth2` > `URL Generator`
- In scopes select `Bot`
- In Bot Permissions select `send messages`, `view audit log`, `read messages/view channels`
- Copy link into your browser and add bot to server
- In `Bot` go to `reset token` and replace YOUR_BOT_TOKEN_HERE in the `bot.py` file
- Install python 3. (on Windows use Microsoft Store version)
- Open powershell
- run `pip install discord.py`
- then run `python ./C:/path/to/yourbot.py`
- Alternatively use the exe file and enter your bot token to run.
