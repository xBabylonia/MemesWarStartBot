Channel: [Yog's Channel](https://t.me/yogschannel)

Bot: [@memes_war_start_bot](https://t.me/Memes_War_Start_Bot/MemesWar?startapp=MK3PV3)


# Memes War Automation

This is a Python script that automates various tasks in the "Memes War" game, including:

1. Daily check-in.
2. Claiming treasury rewards.
3. Sending warbonds to a guild.
4. Using a referral code.
5. Clear Daily & General Task.

## Features

- Supports multiple accounts by reading account data from a `data.txt` file
- Automatically claims daily rewards and treasury
- Sends warbonds to a specified guild
- Uses a referral code if provided

## Requirements

- Python 3.7 or later
- `aiohttp`, `colorama`, and `urllib.parse` libraries

## Usage

1. Create a `data.txt` file in the same directory as the script, and add one `telegramInitData` value per line.
2. Set the `GUILD_ID` and `REFERRAL_CODE` constants in the `CONFIG.py` file.
3. Run the script using `python war.py`.

## Note

This script is intended for educational and research purposes only. Use at your own risk.
