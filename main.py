import aiohttp
import asyncio
import json
from typing import Dict, Optional, List
import logging
from datetime import datetime
from colorama import init, Fore, Back, Style
import urllib.parse
import time
from APIEndpointError import APIEndpointError
from CONFIG import GUILD_ID, REFERRAL_CODE
from fake_useragent import UserAgent

init()

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

EXPECTED_BASE_URL = "https://memes-war.memecore.com/api"

def encode_init_data(raw_init_data: str) -> str:
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
        self.base_url = EXPECTED_BASE_URL
        self.max_retries = 3
        self.endpoint_map = {
            "user": "/user",
            "daily_quests": "/quest/daily/list",
            "single_quests": "/quest/single/list",
            "daily_checkin": "/quest/check-in", 
            "treasury": "/quest/treasury",
            "guild_warbond": "/guild/warbond",
            "referral": "/user/referral/{code}",
            "daily_progress": "/quest/daily/{quest_id}/progress",
            "single_progress": "/quest/single/{quest_id}/progress",
            "daily_claim": "/quest/daily/{quest_id}/claim",
            "single_claim": "/quest/single/{quest_id}/claim"
        }
        ua = UserAgent()
        random_ua = ua.random
        
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
            "user-agent": random_ua
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
        endpoint_key = "daily_quests" if quest_type == "daily" else "single_quests"
        try:
            await self.validate_endpoint(endpoint_key)
            endpoint = self.endpoint_map[endpoint_key]
            
            async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
                async with session.get(f"{self.base_url}{endpoint}") as response:
                    if response.status == 200:
                        data = await response.json()
                        quests = data.get("data", {}).get("quests", [])
                        quest_info = [{"id": quest["id"], "type": quest["type"], "title": quest["title"]} 
                                    for quest in quests]
                        logger.info(f"{Fore.GREEN}[+] Successfully fetched {len(quest_info)} {quest_type} quests{Style.RESET_ALL}")
                        return quest_info
                    raise APIEndpointError(f"Failed to get quests: {response.status}")
        except APIEndpointError as e:
            logger.error(f"{Fore.RED}[!] Quest endpoint error: {str(e)}{Style.RESET_ALL}")
            return []

    async def complete_all_quests(self, quest_type: str = "daily"):
        try:
            quests = await self.get_quests(quest_type)
            if not quests:
                logger.info(f"{Fore.YELLOW}[*] No {quest_type} quests found to complete{Style.RESET_ALL}")
                return

            available_types = {quest["type"] for quest in quests}
            filtered_quests = quests

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
        endpoint_base = "daily" if quest_type == "daily" else "single"
        try:
            progress_endpoint_key = f"{endpoint_base}_progress"
            if progress_endpoint_key not in self.endpoint_map:
                raise APIEndpointError(f"Unknown endpoint key: {progress_endpoint_key}")
                
            progress_endpoint = self.endpoint_map[progress_endpoint_key].format(quest_id=quest_id)
            claim_endpoint = self.endpoint_map[f"{endpoint_base}_claim"].format(quest_id=quest_id)
            
            async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
                async with session.post(f"{self.base_url}{progress_endpoint}") as progress_response:
                    if progress_response.status == 409:
                        logger.info(f"{Fore.BLUE}[*] Quest {quest_id} already completed{Style.RESET_ALL}")
                        return True
                    if progress_response.status != 200:
                        raise APIEndpointError(f"Quest progress failed: {progress_response.status}")
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
                            
                            async with session.post(f"{self.base_url}{progress_endpoint}") as verify_response:
                                if verify_response.status == 409:
                                    logger.info(f"{Fore.BLUE}[*] Quest {quest_id} already claimed{Style.RESET_ALL}")
                                    return True
                                
                                verify_data = await verify_response.json()
                                status = verify_data.get("data", {}).get("status")
                                logger.info(f"{Fore.CYAN}[*] Status after verify: {status}{Style.RESET_ALL}")
                        
                        if status == "CLAIM":
                            async with session.post(f"{self.base_url}{claim_endpoint}") as claim_response:
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
                    
        except APIEndpointError as e:
            logger.error(f"{Fore.RED}[!] Quest endpoint error: {str(e)}{Style.RESET_ALL}")
            return False

    async def use_referral_code(self, code: str) -> bool:
        try:
            endpoint = self.endpoint_map["referral"].format(code=code)
            await self.validate_endpoint("referral", "PUT")
            
            async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
                async with session.put(f"{self.base_url}{endpoint}") as response:
                    if response.status == 200:
                        logger.info(f"{Fore.GREEN}[+] Successfully used referral code: {code}{Style.RESET_ALL}")
                        return True
                    elif response.status == 409:
                        logger.info(f"{Fore.BLUE}[*] Referral code {code} already used{Style.RESET_ALL}")
                        return True
                    else:
                        logger.error(f"{Fore.RED}[!] Failed to use referral code. Status: {response.status}{Style.RESET_ALL}")
                        return False
        except Exception as e:
            logger.error(f"{Fore.RED}[!] Error using referral code: {str(e)}{Style.RESET_ALL}")
            return False

    async def validate_endpoint(self, endpoint_key: str, method: str = "GET", data: dict = None) -> bool:
        endpoint = self.endpoint_map.get(endpoint_key)
        if not endpoint:
            raise APIEndpointError(f"Unknown endpoint key: {endpoint_key}")

        if "{code}" in endpoint:
            endpoint = endpoint.format(code="MK3PV3")

        if endpoint_key == "guild_warbond" and method == "POST":
            data = {
                "guildId": GUILD_ID,
                "warbondCount": 1  # Gunakan nilai minimal untuk test
            }

        retries = 0
        while retries < self.max_retries:
            try:
                async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies) as session:
                    request_method = getattr(session, method.lower())
                    async with request_method(f"{self.base_url}{endpoint}", json=data, timeout=10) as response:
                        if endpoint_key == "guild_warbond" and response.status == 400:
                            return True

                        if response.status == 404:
                            logger.error(f"{Fore.RED}[!] Endpoint {endpoint} not found. API might have changed.{Style.RESET_ALL}")
                            raise APIEndpointError(f"Endpoint {endpoint} not found")
                        elif response.status == 401:
                            logger.error(f"{Fore.RED}[!] Authentication failed for {endpoint}{Style.RESET_ALL}")
                            raise APIEndpointError("Authentication failed")
                        elif response.status not in [200, 409]:
                            if retries < self.max_retries - 1:
                                retries += 1
                                await asyncio.sleep(2 ** retries)
                                continue
                            raise APIEndpointError(f"Unexpected response: {response.status}")
                        return True
            except Exception as e:
                if retries < self.max_retries - 1:
                    retries += 1
                    await asyncio.sleep(2 ** retries)
                    continue
                raise APIEndpointError(f"Error accessing {endpoint}: {str(e)}")

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

    async def process_account(self, init_data: str, account_number: int, total_accounts: int):
        logger.info(f"\n{Fore.YELLOW}[*] Processing Account {account_number}/{total_accounts}{Style.RESET_ALL}")

        try:
            endpoints_to_check = {
                "user": "GET",
                "daily_quests": "GET", 
                "single_quests": "GET",
                "daily_checkin": "POST",
                "treasury": "POST",
                "referral": "PUT",
            }

            logger.info(f"{Fore.CYAN}[*] Validating API endpoints...{Style.RESET_ALL}")
            for endpoint, method in endpoints_to_check.items():
                try:
                    await self.validate_endpoint(endpoint, method)
                except APIEndpointError as e:
                    logger.error(f"{Fore.RED}[!] Critical error validating {endpoint}: {str(e)}{Style.RESET_ALL}")
                    raise SystemExit(f"Script stopped due to {endpoint} API change")

            initial_info = await self.get_user_info(print_info=True)
            if not initial_info:
                logger.error(f"{Fore.RED}[!] Failed to get initial user info{Style.RESET_ALL}")
                return

            async def check_and_send_warbonds(stage: str):
                try:
                    user_info = await self.get_user_info(print_info=False)
                    if not user_info:
                        logger.error(f"{Fore.RED}[!] Could not get user info after {stage}{Style.RESET_ALL}")
                        return
                        
                    warbond_count = int(user_info.get('warbondTokens', '0'))
                    logger.info(f"{Fore.CYAN}[*] Current warbonds after {stage}: {warbond_count}{Style.RESET_ALL}")
                    
                    if warbond_count > 0:
                        await self.validate_endpoint("guild_warbond", "POST")
                        sent = await self.send_warbonds(GUILD_ID, warbond_count)
                        if not sent:
                            logger.error(f"{Fore.RED}[!] Failed to send warbonds after {stage}{Style.RESET_ALL}")
                except Exception as e:
                    logger.error(f"{Fore.RED}[!] Error checking/sending warbonds after {stage}: {str(e)}{Style.RESET_ALL}")

            logger.info(f"\n{Fore.CYAN}[*] Performing daily check-in...{Style.RESET_ALL}")
            await self.daily_checkin()

            logger.info(f"\n{Fore.CYAN}[*] Applying referral code...{Style.RESET_ALL}")
            await self.validate_endpoint("referral", "PUT")
            await self.use_referral_code(REFERRAL_CODE)

            await check_and_send_warbonds("daily check-in")

            logger.info(f"\n{Fore.CYAN}[*] Processing daily quests...{Style.RESET_ALL}")
            await self.complete_all_quests(quest_type="daily")

            logger.info(f"\n{Fore.CYAN}[*] Processing single quests...{Style.RESET_ALL}")
            await self.complete_all_quests(quest_type="single")
            await check_and_send_warbonds("single quests")

            logger.info(f"\n{Fore.CYAN}[*] Claiming treasury...{Style.RESET_ALL}")
            await self.claim_single_treasury()
            await check_and_send_warbonds("treasury claim")

            logger.info(f"\n{Fore.CYAN}[*] Getting final user status...{Style.RESET_ALL}")
            await self.get_user_info(print_info=True)

        except APIEndpointError as e:
            logger.error(f"{Fore.RED}[!] Critical API endpoint error: {str(e)}")
            logger.error(f"{Fore.RED}[!] Stopping script - API structure might have changed{Style.RESET_ALL}")
            raise SystemExit("Script stopped due to API structure change")

        except Exception as e:
            logger.error(f"{Fore.RED}[!] Error processing account {account_number}: {str(e)}{Style.RESET_ALL}")
            import traceback
            logger.error(f"{Fore.RED}[!] Full error traceback:{Style.RESET_ALL}")
            logger.error(traceback.format_exc())

        finally:
            logger.info(f"{Fore.GREEN}[+] Finished processing account {account_number}/{total_accounts}{Style.RESET_ALL}")

async def main():
    api = MemesWarAPI("")
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
                
                api = MemesWarAPI(init_data)
                await api.process_account(init_data, i, len(accounts))
                
            except SystemExit as e:
                logger.error(f"{Fore.RED}[!] Critical error - stopping script: {str(e)}{Style.RESET_ALL}")
                return
                
            except Exception as e:
                logger.error(f"{Fore.RED}[!] Error on account {i}: {e}{Style.RESET_ALL}")
                continue

        print(f"\n{Fore.GREEN}[+] Cycle {cycle} completed{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Waiting 1 hour before next cycle...{Style.RESET_ALL}")
        
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