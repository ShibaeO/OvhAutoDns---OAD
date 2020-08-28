import aiohttp
import asyncio
import json
from datetime import datetime
import logging
import os
import sys
import time

responseCode = {
    "nochg": "Ip is the same as one on ovh",
    "!yours": "This dns isn't yous or isn't exist",
    "good": "The ip has been changed",
    "badsys": "Incorect method on this url",
    "401": "login error",
}


logging.basicConfig(filename="logs.log", filemode="w", format="%(asctime)s [%(name)s] [%(levelname)s] -> %(message)s", level=logging.INFO)


def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


async def currentIp():

    with open("config.json", mode="r") as configFile:
        configRead = json.load(configFile)
        url = configRead["appConfig"]["rawIpUrl"]

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            a = await response.text()
    return a, response.status


async def updateDns(hostUserName, hostPass, ip, hostname):
    url = f"http://www.ovh.com/nic/update?system=dyndns&hostname={hostname}&myip={ip}"
    async with aiohttp.ClientSession(auth=aiohttp.BasicAuth(f"{hostUserName}", f"{hostPass}")) as session:
        async with session.get(url) as response:
            a = await response.text()
    return a, response.status


async def updateLoop(hostUserName, hostPass, hostname, delay: int):
    while True:
        print(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Cheking : {hostname}")
        logging.info(f"Cheking : {hostname}")
        ip = await currentIp()
        if ip[1] == 200:
            updateRequest = await updateDns(hostUserName, hostPass, ip[0], hostname)
            if updateRequest[1] == 401:
                logging.error(f"login error : {hostname}")
            elif "good" in updateRequest[0]:
                logging.info(f"A new ip has been found and chanegd on ovh : {ip[0]} | {hostname}")
            elif "nochg" in updateRequest[0]:
                logging.info(f"Ip is the same one as ovh : {ip[0]} | {hostname}")
            elif "!yours" in updateRequest[0]:
                logging.info(f"This dns isn't yours or isn't exist : {hostname}")
            elif updateRequest[0].split(" ")[0] not in responseCode:
                logging.info(f"unknow error : {hostname}")
        else:
            print("error couldn't get the curent ip")
        await asyncio.sleep(delay)


async def main():
    menu = 0
    if "service" in sys.argv:
        pass
    else:
        clear()
        print("[+] OVH Auto Dyndns by Shiabeo 1.0 :\n")
        print("     1 : Config")
        print("     2 : Start service")
        menu = input(">> ")
        print("dd")

    if menu == "1":
        # TODO: Faire le menu config : un autre menu pour ajouter un dns et pour del un dns
        pass
    elif menu == "2" or "service" in sys.argv:
        clear()
        with open("config.json", mode="r") as configFile:
            configRead = json.load(configFile)

        for dnsNbs in configRead["dns"]:
            hostname = configRead["dns"][dnsNbs]["dns"]
            hostUserName = configRead["dns"][dnsNbs]["user"]
            hostPass = configRead["dns"][dnsNbs]["pass"]
            delay = configRead["dns"][dnsNbs]["delay"]
            print(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | {dnsNbs} : {hostname} -> loaded")
            logging.info(f"{dnsNbs} : {hostname} loaded")
            asyncio.ensure_future(updateLoop(hostUserName, hostPass, hostname, delay))


if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(main())
        loop.run_forever()
    except KeyboardInterrupt:
        clear()
        print(f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Stopping program")
        time.sleep(1)
