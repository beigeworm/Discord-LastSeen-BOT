# Discord Server Activity Monitor Bot

This Discord bot is designed to monitor server activity, provide activity leaderboards, and play music. It logs member statuses, tracks their last seen times, and provides various commands for retrieving activity statistics. Additionally, it can play music from YouTube.

## Installation Instructions
### Dependencies
- Python 3.8 or higher
- discord.py library
- youtube-dl library
- ffmpeg library

### Steps
1. Clone or download the repository to your local machine.
2. Install Python if you haven't already (Python 3.8 or higher is required).
3. Install dependencies using pip:

`pip install discord.py`

`pip install ffmpeg`

`pip install git+https://github.com/ytdl-org/youtube-dl` (this is the most up to date version)

4. Install ffmpeg.
- Windows : get ffmpeg and place ffmpeg.exe in the same directory as the script - https://ffmpeg.org/download.html
- Linux : in a termial type - `sudo apt install ffmpeg -y`

5. Create a Discord bot and obtain the bot token.
6. Obtain your Discord server ID and channel ID.
7. Update the following variables in the code with your bot token, server ID, and channel ID:
- `bot_token`
- `server_id`
- `channel_id`
8. Run the bot script:

`python ./bot.py`

## Commands
- **/seenhelp**: List all commands and their descriptions.
- **/lastseen [user]** (Alias: /ls): Display last seen time for a member.
- **/totalonline [user]** (Alias: /online): Display total online time for a member.
- **/totalactive [user]** (Alias: /active): Display total active time for a member.
- **/activeleaderboard**: Display top 10 most active members.
- **/onlineleaderboard**: Display top 10 online members.
- **/play [url]** (Alias: /p): Play a song from YouTube.
- **/stop** (Alias: /s): Stop the current song.
- **/toggleidle** (Admin only): Toggle idle status updates.
- **/toggleonline** (Admin only): Toggle online/offline status updates.
- **/restart** (Admin only): Soft restart the bot.
- **/adminhelp**: List all admin commands and their descriptions.
