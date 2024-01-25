# Discord-LastSeen-BOT
A simple python script for a discord bot that saves server member online/offline status changes.

With a command to check 'last-seen' info with `/seen`

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
