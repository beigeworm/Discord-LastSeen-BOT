import os
import shutil
import subprocess
import schedule
import time
import psutil
from datetime import datetime, timedelta

# Run this script instead to run the bot and restart it once every week (Resets leaderboards etc..)

def move_json_files():
    # Create a directory with the current date as its name
    current_date = datetime.now().strftime('%Y-%m-%d')
    directory_name = f'json_files_{current_date}'
    os.makedirs(directory_name, exist_ok=True)

    # Move all .json files to the new directory
    for filename in os.listdir('.'):
        if filename.endswith('.json'):
            shutil.move(filename, os.path.join(directory_name, filename))

def restart_script():
    # Find and kill the process associated with the egiebot.py script
    for proc in psutil.process_iter():
        if proc.name() == 'python3' and 'activitybot.py' in ' '.join(proc.cmdline()):
            proc.terminate()

    # Restart the egiebot.py script
    subprocess.Popen(['python3', 'activitybot.py'])

def main():
    # Move JSON files and restart script
    move_json_files()
    restart_script()

main()
# Schedule the main function to run once every week
schedule.every().week.do(main)

while True:
    schedule.run_pending()
    time.sleep(1)
