import os
import socket
import requests
import csv
from colorama import Fore, Style
from telethon import TelegramClient, events, utils


def test_proxy_connection(host, port):
    try:
        # Create a socket and connect to the proxy
        proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        proxy_socket.settimeout(5)
        proxy_socket.connect((host, port))
        proxy_socket.close()
        return True
    except:
        return False


def get_proxy_info(url):
    response = requests.get(url)
    data = response.json()

    for proxy in data:
        host = proxy['ip']
        port = proxy['port']
        country = proxy['country']
        ping = proxy['ping']

        print("Proxy Information:")
        print(f"Host: {host}")
        print(f"Port: {port}")
        print(f"Country: {country}")
        print(f"Ping: {ping}")

        # Test the proxy connection
        print("Testing connection...")
        if test_proxy_connection(host, port):
            print("Connection successful")

            # Set the proxy in TelegramClient configuration
            proxy_config = (host, int(port), '', '', '')
            configure_telegram_client(proxy_config)

            break
        else:
            print("Connection failed")
        print()


def configure_telegram_client(proxy_config):
    # Set up your Telegram API credentials
    api_id = 25041499
    api_hash = 'd67bc7f743de8e8816f6de798ccc7845'

    # Create a new Telegram client instance
    client = TelegramClient('scraper_acc', api_id, api_hash)
    client.proxy = proxy_config

    # Define an event handler to print the username of new messages in groups
    @client.on(events.NewMessage)
    async def new_message_handler(event):
        print(Fore.CYAN + f'{event.message.sender.username}' + Style.RESET_ALL)

    # Start the client
    client.start()

    # Get a list of all the dialogues (including both groups and private chats)
    with client:
        client.loop.run_until_complete(main(client))


async def main(client):
    # Get a list of all the dialogues (including both groups and private chats)
    async for dialog in client.iter_dialogs():
        if dialog.is_group:
            print(Fore.GREEN + f'{dialog.title}' + Style.RESET_ALL)

            # Get a list of all the users in the group
            participants = await client.get_participants(dialog)

            print(f"Found {len(participants)} users in {dialog.title}")

            # Create a filename based on the group title
            group_name = dialog.title
            # Replace any illegal characters in the filename
            safe_group_name = "".join(x for x in group_name if x.isalnum() or x in " -_")
            filename = f'{safe_group_name}.txt'

            with open(filename, 'w', encoding='utf-8') as f:
                for user in participants:
                    username = user.username
                    if username:
                        f.write(f'{username}\n')

            print(f"Members of {dialog.title} saved to {filename}")

    # Print "done" when finished
    print("done")

    # Disconnect the client
    await client.disconnect()

    # Count total number of usernames in all files
    total_usernames = 0
    for file in os.listdir('.'):
        if file.endswith('.txt'):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    usernames = f.readlines()
                    total_usernames += len(usernames)
            except FileNotFoundError:
                print(f"{file} file not found.")
    print(f"Total number of usernames: {total_usernames}")

if __name__ == '__main__':
    import asyncio

    # Replace the URL below with the actual API URL you have
    api_url = 'https://mtpro.xyz/api/?type=socks'
    get_proxy_info(api_url)
