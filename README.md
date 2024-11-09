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

--------------

# Cara Menjalankan Script

Script ini dapat dijalankan di berbagai platform, termasuk Windows, Linux/VPS, dan Termux. Berikut adalah langkah-langkah untuk menjalankan script ini.

## Persyaratan

Pastikan Anda memiliki Python versi 3.7 atau lebih baru. Anda juga perlu menginstal `pip`, yang biasanya sudah termasuk dalam instalasi Python.

## Langkah Instalasi

### 1. Clone Repository
Clone repository ini terlebih dahulu:

```bash
git clone https://github.com/xBabylonia/MemesWarStartBot.git
cd repository
```

### 2. Install Dependensi
Jalankan perintah berikut untuk menginstal semua dependensi yang dibutuhkan.

```bash
pip install aiohttp colorama urllib.parse
```

## Cara Menjalankan di Windows

1. Buka Command Prompt atau Terminal di folder project.
2. Jalankan script dengan perintah berikut:

   ```bash
   python main.py
   ```

## Cara Menjalankan di Linux atau VPS

1. Buka terminal.
2. Arahkan ke folder tempat Anda meng-clone repository.
3. Jalankan perintah berikut:

   ```bash
   python3 main.py
   ```

## Cara Menjalankan di Termux

1. Pastikan Termux Anda sudah diperbarui:

   ```bash
   pkg update && pkg upgrade
   ```

2. Install Python di Termux jika belum terpasang:

   ```bash
   pkg install python
   ```

3. Clone repository dan masuk ke folder project:

   ```bash
   git clone https://github.com/xBabylonia/MemesWarStartBot.git
   cd repository
   ```

4. Install dependensi:

   ```bash
   pip install aiohttp colorama urllib.parse
   ```

5. Jalankan script:

   ```bash
   python main.py
   ```
   
--------------
## Note

This script is intended for educational and research purposes only. Use at your own risk.