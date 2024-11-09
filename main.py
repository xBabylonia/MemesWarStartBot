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

    async def get_quests(self, quest_type: str = "daily") -> List[Dict]:
        """Get list of quests with proper error handling."""
        endpoint = "daily" if quest_type == "daily" else "single"
        try:
            async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
                async with session.get(f"{self.base_url}/quest/{endpoint}/list") as response:
                    if response.status == 200:
                        data = await response.json()
                        quests = data.get("data", {}).get("quests", [])
                        quest_info = [{"id": quest["id"], "type": quest["type"], "title": quest["title"]} 
                                    for quest in quests]
                        logger.info(f"{Fore.GREEN}[+] Successfully fetched {len(quest_info)} {quest_type} quests{Style.RESET_ALL}")
                        return quest_info
                    else:
                        logger.error(f"{Fore.RED}[!] Failed to get {quest_type} quests. Status: {response.status}{Style.RESET_ALL}")
                        return []
        except Exception as e:
            logger.error(f"{Fore.RED}[!] Error getting {quest_type} quests: {str(e)}{Style.RESET_ALL}")
            return []

    async def complete_all_quests(self, quest_type: str = "daily"):
        """Complete all quests of specified type with improved handling."""
        try:
            quests = await self.get_quests(quest_type)
            if not quests:
                logger.info(f"{Fore.YELLOW}[*] No {quest_type} quests found to complete{Style.RESET_ALL}")
                return

            # Get all available quest types from response
            available_types = {quest["type"] for quest in quests}
            filtered_quests = quests  # No need to filter since we're using all types

            completed = 0
            total = len(filtered_quests)

            if total == 0:
                logger.info(f"{Fore.YELLOW}[*] No quests found{Style.RESET_ALL}")
                return

            for quest in filtered_quests:
                quest_id = quest["id"]
                logger.info(f"\n{Fore.CYAN}[*] Processing {quest_type} quest: {quest['title']} (Type: {quest['type']}) (ID: {quest_id}){Style.RESET_ALL}")
                
                result = await self.complete_quest(quest_id, quest_type)
                if result:
                    completed += 1
                
                if completed < total:
                    await asyncio.sleep(2)

            logger.info(f"\n{Fore.GREEN}[+] {quest_type.capitalize()} quest completion summary: {completed}/{total} processed successfully{Style.RESET_ALL}")

        except Exception as e:
            logger.error(f"{Fore.RED}[!] Error in complete_all_quests: {str(e)}{Style.RESET_ALL}")

    async def complete_quest(self, quest_id: int, quest_type: str = "daily") -> bool:
        """Complete a quest with improved error handling."""
        endpoint = "daily" if quest_type == "daily" else "single"
        try:
            async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
                # Step 1: Send initial progress request
                progress_url = f"{self.base_url}/quest/{endpoint}/{quest_id}/progress"
                async with session.post(progress_url) as progress_response:
                    # Handle various response statuses
                    if progress_response.status == 409:
                        logger.info(f"{Fore.BLUE}[*] Quest {quest_id} already completed{Style.RESET_ALL}")
                        return True
                    
                    if progress_response.status != 200:
                        logger.error(f"{Fore.RED}[!] Quest progress failed for ID {quest_id}. Status: {progress_response.status}{Style.RESET_ALL}")
                        return False
                    
                    try:
                        progress_data = await progress_response.json()
                        status = progress_data.get("data", {}).get("status")
                        reward_amount = progress_data.get("data", {}).get("reward", {}).get("rewardAmount", "")
                        logger.info(f"{Fore.CYAN}[*] Initial status: {status}{Style.RESET_ALL}")
                        
                        if status == "DONE":
                            logger.info(f"{Fore.GREEN}[+] Quest {quest_id} completed! Reward: {reward_amount} WARBOND{Style.RESET_ALL}")
                            return True
                        
                        if status == "VERIFY":
                            logger.info(f"{Fore.YELLOW}[*] Quest {quest_id} requires verification. Waiting 3 seconds...{Style.RESET_ALL}")
                            await asyncio.sleep(3)
                            
                            async with session.post(progress_url) as verify_response:
                                if verify_response.status == 409:
                                    logger.info(f"{Fore.BLUE}[*] Quest {quest_id} already claimed{Style.RESET_ALL}")
                                    return True
                                
                                verify_data = await verify_response.json()
                                status = verify_data.get("data", {}).get("status")
                                logger.info(f"{Fore.CYAN}[*] Status after verify: {status}{Style.RESET_ALL}")
                        
                        if status == "CLAIM":
                            claim_url = f"{self.base_url}/quest/{endpoint}/{quest_id}/claim"
                            async with session.post(claim_url) as claim_response:
                                if claim_response.status == 200:
                                    logger.info(f"{Fore.GREEN}[+] Successfully claimed quest {quest_id}{Style.RESET_ALL}")
                                    return True
                                elif claim_response.status == 409:
                                    logger.info(f"{Fore.BLUE}[*] Quest {quest_id} already claimed{Style.RESET_ALL}")
                                    return True
                        
                        logger.info(f"{Fore.YELLOW}[!] Quest {quest_id} not completed. Final status: {status}{Style.RESET_ALL}")
                        return False
                        
                    except (KeyError, TypeError) as e:
                        logger.error(f"{Fore.RED}[!] Error parsing quest response: {e}{Style.RESET_ALL}")
                        return False
                    
        except Exception as e:
            logger.error(f"{Fore.RED}[!] Error completing quest {quest_id}: {str(e)}{Style.RESET_ALL}")
            return False

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
                    # Fix the malformed line
                    reward_amount = rewards['rewards'][0]['rewardAmount']
                    logger.info(f"{Fore.GREEN}[+] Treasury claimed: {reward_amount} WARBOND{Style.RESET_ALL}")
                    return rewards
                return {}

    async def send_warbonds(self, guild_id: str, warbond_count: int) -> bool:
        """Send warbonds to a guild with proper type handling."""
        payload = {
            "guildId": guild_id,
            # Convert warbond_count to string as required by the API
            "warbondCount": str(warbond_count)
        }
        
        try:
            async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
                async with session.post(
                    f"{self.base_url}/guild/warbond",
                    json=payload
                ) as response:
                    if response.status == 200:
                        logger.info(f"{Fore.GREEN}[+] Successfully sent {warbond_count} warbonds to guild{Style.RESET_ALL}")
                        return True
                    else:
                        response_text = await response.text()
                        logger.error(f"{Fore.RED}[!] Failed to send warbonds. Status: {response.status}")
                        logger.error(f"[!] Response: {response_text}{Style.RESET_ALL}")
                        return False
        except Exception as e:
            logger.error(f"{Fore.RED}[!] Error sending warbonds: {str(e)}{Style.RESET_ALL}")
            return False
    
    async def claim_single_treasury(self):
        try:
            await self.claim_treasury()
        except Exception as e:
            logger.error(f"{Fore.RED}[!] Treasury error: {e}{Style.RESET_ALL}")
        return await self.get_user_info(print_info=True)

async def process_account(init_data: str, account_number: int, total_accounts: int):
    """Process a single account with improved warbond handling."""
    logger.info(f"\n{Fore.YELLOW}[*] Account {account_number}/{total_accounts}{Style.RESET_ALL}")
    
    api = MemesWarAPI(init_data)
    
    async def check_and_send_warbonds(stage: str):
        """Helper function to check and send warbonds with proper logging."""
        try:
            user_info = await api.get_user_info(print_info=False)
            if not user_info:
                logger.error(f"{Fore.RED}[!] Could not get user info after {stage}{Style.RESET_ALL}")
                return
                
            warbond_count = int(user_info.get('warbondTokens', '0'))
            logger.info(f"{Fore.CYAN}[*] Current warbonds after {stage}: {warbond_count}{Style.RESET_ALL}")
            
            if warbond_count > 0:
                sent = await api.send_warbonds(GUILD_ID, warbond_count)
                if not sent:
                    logger.error(f"{Fore.RED}[!] Failed to send warbonds after {stage}{Style.RESET_ALL}")
        except Exception as e:
            logger.error(f"{Fore.RED}[!] Error checking/sending warbonds after {stage}: {str(e)}{Style.RESET_ALL}")
    
    # Initial user info
    initial_info = await api.get_user_info(print_info=True)
    if not initial_info:
        logger.error(f"{Fore.RED}[!] Failed to get initial user info{Style.RESET_ALL}")
        return
    
    # Process daily activities
    await api.daily_checkin()
    await api.use_referral_code(REFERRAL_CODE)
    await check_and_send_warbonds("daily check-in")
    
    # Process daily quests
    logger.info(f"\n{Fore.CYAN}[*] Processing daily quests...{Style.RESET_ALL}")
    await api.complete_all_quests(quest_type="daily")
    await check_and_send_warbonds("daily quests")
    
    # Process single quests
    logger.info(f"\n{Fore.CYAN}[*] Processing single quests...{Style.RESET_ALL}")
    await api.complete_all_quests(quest_type="single")
    await check_and_send_warbonds("single quests")
    
    # Final treasury claim
    logger.info(f"\n{Fore.CYAN}[*] Claiming treasury...{Style.RESET_ALL}")
    await api.claim_single_treasury()
    await check_and_send_warbonds("treasury claim")
    
    # Final user info
    await api.get_user_info(print_info=True)

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
                    logger.info(f"\n{Fore.CYAN}[*] Waiting 5 seconds before next account...{Style.RESET_ALL}")
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
        print(f"\n{Fore.YELLOW}[!] Script terminated by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}[!] Fatal error: {e}{Style.RESET_ALL}")