import aiohttp
import asyncio
import json
from typing import Dict, Optional, List
import logging
from datetime import datetime
from colorama import init, Fore, Back, Style
import urllib.parse
import time
from CONFIG import GUILD_ID, REFERRAL_CODE

# Initialize colorama
init()

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def encode_init_data(raw_init_data: str) -> str:
    """Convert raw init data to properly encoded format for cookies."""
    decoded = urllib.parse.unquote(raw_init_data)
    pairs = decoded.split('&')
    encoded_pairs = []
    
    for pair in pairs:
        if '=' not in pair:
            continue
        key, value = pair.split('=', 1)
        
        if key == 'user':
            value = urllib.parse.quote(urllib.parse.quote(value))
        else:
            value = urllib.parse.quote(value)
            
        encoded_pairs.append(f"{key}%3D{value}")
    
    return '%26'.join(encoded_pairs)

def read_accounts() -> List[str]:
    """Read and process account data from data.txt."""
    try:
        with open('data.txt', 'r', encoding='utf-8') as file:
            raw_accounts = file.readlines()
        
        accounts = [encode_init_data(line.strip()) for line in raw_accounts if line.strip()]
        logger.info(f"{Fore.GREEN}[+] Loaded {len(accounts)} accounts{Style.RESET_ALL}")
        return accounts
    except FileNotFoundError:
        logger.error(f"{Fore.RED}[!] data.txt not found{Style.RESET_ALL}")
        return []
    except Exception as e:
        logger.error(f"{Fore.RED}[!] Error reading data.txt: {e}{Style.RESET_ALL}")
        return []

class MemesWarAPI:
    def __init__(self, telegram_init_data: str):
        self.base_url = "https://memes-war.memecore.com/api"
        self.headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "origin": "https://memes-war.memecore.com",
            "pragma": "no-cache",
            "referer": "https://memes-war.memecore.com/",
            "sec-ch-ua": '"Chromium";v="130", "Microsoft Edge";v="130", "Not?A_Brand";v="99", "Microsoft Edge WebView2";v="130"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0"
        }
        self.cookies = {
            "telegramInitData": telegram_init_data
        }

    def print_banner(self):
        banner = f"""{Fore.CYAN}
    ┏━━━━┳┓╋╋╋╋╋┏━━━┓╋╋╋┏┓╋╋╋╋╋┏━━━┓╋╋┏┓╋╋╋╋╋┏━┓    awkowakwoakowa
    ┃┏┓┏┓┃┃╋╋╋╋╋┃┏━┓┃╋╋╋┃┃╋╋╋╋╋┃┏━┓┃╋╋┃┃╋╋╋╋╋┃┏┛    created by @yogschannel
    ┗┛┃┃┗┫┗━┳━━┓┃┃╋┃┣━┳━┛┣━━┳━┓┃┃╋┃┣━━┫┗━┳━━┳┛┗┓
    ╋╋┃┃╋┃┏┓┃┃━┫┃┃╋┃┃┏┫┏┓┃┃━┫┏┛┃┗━┛┃━━┫┏┓┃┏┓┣┓┏┛
    ╋╋┃┃╋┃┃┃┃┃━┫┃┗━┛┃┃┃┗┛┃┃━┫┃╋┃┏━┓┣━━┃┃┃┃┏┓┃┃┃
    ╋╋┗┛╋┗┛┗┻━━┛┗━━━┻┛┗━━┻━━┻┛╋┗┛╋┗┻━━┻┛┗┻┛┗┛┗┛
    {Style.RESET_ALL}
    """
        print(banner)

    async def use_referral_code(self, code: str) -> bool:
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
            async with session.put(f"{self.base_url}/user/referral/{code}") as response:
                if response.status == 200:
                    logger.info(f"{Fore.GREEN}[+] Used referral: {code}{Style.RESET_ALL}")
                    return True
                return False

    async def get_user_info(self, print_info=True) -> Dict:
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
            async with session.get(f"{self.base_url}/user") as response:
                if response.status == 200:
                    data = await response.json()
                    user = data["data"]["user"]
                    if print_info:
                        self.print_user_info(user)
                    return user
                return {}

    def print_user_info(self, user):
        now = datetime.now().strftime("%H:%M:%S")
        print(f"\n{Fore.CYAN}╭── User Info [{now}] ───")
        print(f"│ {Fore.WHITE}Nick: {user['nickname']}")
        print(f"│ {Fore.WHITE}Honor: {user['honorPoints']} │ Rank: {user['honorPointRank']}")
        print(f"│ {Fore.WHITE}Warbonds: {user['warbondTokens']}")
        print(f"{Fore.CYAN}╰{'─' * 30}{Style.RESET_ALL}")

    async def daily_checkin(self) -> bool:
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
            async with session.post(f"{self.base_url}/quest/check-in") as response:
                success = response.status == 200
                if success:
                    logger.info(f"{Fore.GREEN}[+] Daily check-in done{Style.RESET_ALL}")
                return success

    async def claim_treasury(self) -> Dict:
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
            async with session.post(f"{self.base_url}/quest/treasury") as response:
                if response.status == 200:
                    data = await response.json()
                    rewards = data["data"]
                    reward_amount = rewards['rewards'][0]['rewardAmount']
                    logger.info(f"{Fore.GREEN}[+] Treasury claimed: {reward_amount} WARBOND{Style.RESET_ALL}")
                    return rewards
                return {}

    async def send_warbonds(self, guild_id: str, warbond_count: int) -> bool:
        payload = {
            "guildId": guild_id,
            "warbondCount": warbond_count
        }
        async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
            async with session.post(
                f"{self.base_url}/guild/warbond",
                json=payload
            ) as response:
                success = response.status == 200
                if success:
                    logger.info(f"{Fore.GREEN}[+] Sent {warbond_count} warbonds{Style.RESET_ALL}")
                return success

    async def claim_single_treasury(self):
        try:
            await self.claim_treasury()
        except Exception as e:
            logger.error(f"{Fore.RED}[!] Treasury error: {e}{Style.RESET_ALL}")
        return await self.get_user_info(print_info=True)

async def process_account(init_data: str, account_number: int, total_accounts: int):
    """Process a single account."""
    logger.info(f"\n{Fore.YELLOW}[*] Account {account_number}/{total_accounts}{Style.RESET_ALL}")
    
    api = MemesWarAPI(init_data)
    
    user_info = await api.get_user_info(print_info=False)
    if not user_info:
        logger.error(f"{Fore.RED}[!] Failed to get user info{Style.RESET_ALL}")
        return
    
    await api.daily_checkin()
    await api.use_referral_code(REFERRAL_CODE)
    
    warbond_count = user_info['warbondTokens']
    await api.send_warbonds(GUILD_ID, warbond_count)
    
    await api.claim_single_treasury()

async def main():
    api = MemesWarAPI("")  # Empty instance just for banner
    api.print_banner()
    
    accounts = read_accounts()
    if not accounts:
        logger.error(f"{Fore.RED}[!] No accounts found{Style.RESET_ALL}")
        return

    cycle = 1
    while True:
        print(f"\n{Fore.CYAN}╭── Cycle #{cycle} ───")
        print(f"╰── Started at: {datetime.now().strftime('%H:%M:%S')}{Style.RESET_ALL}")
        
        for i, init_data in enumerate(accounts, 1):
            try:
                if i > 1:
                    logger.info(f"\n{Fore.CYAN}[*] Waiting 5 seconds...{Style.RESET_ALL}")
                    await asyncio.sleep(5)
                await process_account(init_data, i, len(accounts))
            except Exception as e:
                logger.error(f"{Fore.RED}[!] Error on account {i}: {e}{Style.RESET_ALL}")
                continue

        print(f"\n{Fore.GREEN}[+] Cycle {cycle} completed{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Waiting 1 hour before next cycle...{Style.RESET_ALL}")
        
        # Show countdown timer
        for minutes in range(59, -1, -1):
            print(f"\r{Fore.CYAN}[*] Next cycle in: {minutes:02d}:00{Style.RESET_ALL}", end="")
            await asyncio.sleep(60)
        print()
        
        cycle += 1

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}[!] Script terminated by user{Style.RESET_AS}")
    except Exception as e:
        print(f"\n{Fore.RED}[!] Fatal error: {e}{Style.RESET_ALL}")