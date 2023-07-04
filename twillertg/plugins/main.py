import random
import socket
import time
import os
import itertools
import asyncio
from datetime import datetime
import colorama
from colorama import Fore, Style
import requests
from telethon import TelegramClient
from telethon.errors.rpcerrorlist import FloodWaitError, PhoneNumberInvalidError, UsernameInvalidError
from telethon.tl.types import InputMediaPhoto

# Set up your Telegram API credentials
api_id = 20918706
api_hash = 'a7de8dabdc9206f91400d6dca0968ed9'

# Function to log the message details
session_folder = "accounts"


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


async def get_proxy_info(url, session_name, recipient, message, image_path):
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
            await send_secret_message(
                proxy_config, session_name, recipient, message, image_path)  # Await the send_secret_message coroutine
            break
        else:
            print("Connection failed")
        print()
    return proxy_config


def log_message(recipient, status):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f'{timestamp} - Recipient: {recipient}, Status: {status}'
    print(log_entry)


# Define a function to send a secret message
async def send_secret_message(proxy_config, session_name, recipient, message, image_path):
    session_path = os.path.join(session_folder, session_name)
    async with TelegramClient(session_path, api_id, api_hash) as client:
        client.proxy = proxy_config
        try:
            if not await client.is_user_authorized():
                print("Error authorization")
                # Remove the session file from the folder
                os.remove(session_path)
                return False

            # Get the input entity of the recipient
            entity = await client.get_input_entity(recipient)

            # Check if user is currently online or recently online
            user = await client.get_entity(entity)
            if user.status:
                print(
                    f'User {recipient} has a status. Sending secret message...')
                try:
                    # Upload the image and get its file ID
                    image = await client.upload_file(image_path)
                    # Send the message with the image as a caption in the secret chat
                    await client.send_file(entity, file=image, caption=message)
                    print('Secret message sent!')
                    time.sleep(70)
                    with open("usernames.txt", "r") as f:
                        recipients = f.readlines()
                    recipients.remove(recipient + '\n')
                    with open("usernames.txt", "w") as f:
                        f.writelines(recipients)
                    log_message(recipient, 'Sent')
                except FloodWaitError as e:
                    print(
                        f'Flood limit exceeded. Sleeping for {e.seconds} seconds...')
                    await asyncio.sleep(e.seconds)
                    log_message(recipient, 'Failed')
                except Exception as e:
                    if "Too many requests" in str(e):
                        print(
                            f"{Fore.RED}Too many requests error occurred for {session_name}. Skipping...{Fore.RESET}")
                        # Mark the session as excluded
                        with open("excluded_sessions.txt", "a") as f:
                            f.write(f"{session_name}\n")
                        log_message(recipient, 'Failed')
                        os.remove(session_path)

                        return False
                    elif "A wait of" in str(e):
                        print(
                            f"{Fore.RED}Failed to send Shill to {user.username} Session {session_name}, {session_name.title()}. Error: {e}{Fore.RESET}")
                        print("Skipping...")
                        log_message(recipient, 'Failed')
                        with open("usernames.txt", "r") as f:
                            recipients = f.readlines()
                        recipients.remove(recipient + '\n')
                        with open("usernames.txt", "w") as f:
                            f.writelines(recipients)
                        return False
                    else:
                        print(colorama.Fore.RED +
                              f"[x] Failed to send Shill {recipient} Session {session_name}, {session_name.title()}. Error: {e}{Fore.RESET}")
                        print('[x] skipping..........')
                        log_message(recipient, 'Failed')
                        print(colorama.Fore.GREEN +
                              f"[✓] Changing Account.......... ")
                        print(colorama.Fore.GREEN +
                              f"[✓] {session_name}..........")
                        print(Style.RESET_ALL)
                        with open("usernames.txt", "r") as f:
                            recipients = f.readlines()
                        recipients.remove(recipient + '\n')
                        with open("usernames.txt", "w") as f:
                            f.writelines(recipients)
                        # Remove the session file from the folder

                        return False
            else:
                print(
                    f'User {recipient} is not currently online. Skipping...')
                with open("usernames.txt", "r") as f:
                    recipients = f.readlines()
                recipients.remove(recipient + '\n')
                with open("usernames.txt", "w") as f:
                    f.writelines(recipients)
                log_message(recipient, 'Failed')
        except PhoneNumberInvalidError:
            print("Failed session")
            log_message(recipient, 'Failed')
            os.remove(session_path)
            return False
        except UsernameInvalidError:
            print(f'Invalid username: {recipient}. Skipping...')
            with open("usernames.txt", "r") as f:
                recipients = f.readlines()
            recipients.remove(recipient + '\n')
            with open("usernames.txt", "w") as f:
                f.writelines(recipients)
            log_message(recipient, 'Failed')
        except Exception as e:
            if "Too many requests" in str(e):
                print(
                    f"{Fore.RED}Too many requests error occurred for {session_name}. Skipping...{Fore.RESET}")
                # Mark the session as excluded
                with open("excluded_sessions.txt", "a") as f:
                    f.write(f"{session_name}\n")
                log_message(recipient, 'Failed')
                os.remove(session_path)
                return False
            elif "A wait of" in str(e):
                print(
                    f"{Fore.RED}Failed to send Shill to {user.username} Session {session_name}, {session_name.title()}. Error: {e}{Fore.RESET}")
                print("Skipping...")
                log_message(recipient, 'Failed')
                with open("usernames.txt", "r") as f:
                    recipients = f.readlines()
                recipients.remove(recipient + '\n')
                with open("usernames.txt", "w") as f:
                    f.writelines(recipients)
                return False
            else:
                print(colorama.Fore.RED +
                      f"[x] Failed to send Shill {recipient} Session {session_name}, {session_name.title()}. Error: {e}{Fore.RESET}")
                print('[x] skipping..........')
                log_message(recipient, 'Failed')
                print(colorama.Fore.GREEN +
                      f"[✓] Changing Account.......... ")
                print(colorama.Fore.GREEN + f"[✓] {session_name}..........")
                print(Style.RESET_ALL)
                with open("usernames.txt", "r") as f:
                    recipients = f.readlines()
                recipients.remove(recipient + '\n')
                with open("usernames.txt", "w") as f:
                    f.writelines(recipients)
                # Remove the session file from the folder

                return False
        # Close the client session
        await client.disconnect()
    return False


# Main function to send secret messages
async def main():
    # Read session names from the session folder
    session_names = [file for file in os.listdir(
        session_folder) if file.endswith('.session')]

    # Read excluded session names from the excluded_sessions file
    # Read excluded session names from the excluded_sessions file
    excluded_sessions = set()
    if os.path.isfile("excluded_sessions.txt"):
        with open("excluded_sessions.txt", "r") as f:
            excluded_sessions = set([line.strip() for line in f.readlines()])

    # Remove excluded sessions from the list of session names
    session_names = [
        session_name for session_name in session_names if session_name not in excluded_sessions]

    session_cycle = itertools.cycle(session_names)
    current_session = next(session_cycle)  # Initialize with the first session

    # Read recipients from file
    with open('usernames.txt', 'r', encoding='utf-8') as f:
        recipients = [line.strip() for line in f.readlines()]

    # Get a list of message files in the messages directory
    message_files = [os.path.join("messages", f) for f in os.listdir(
        "messages") if os.path.isfile(os.path.join("messages", f))]

    success_count = 0
    failure_count = 0

    for recipient in recipients:
        # Select a random message file
        random_message_file = random.choice(message_files)

        # Read the message content from the file
        with open(random_message_file, 'r') as f:
            message_content = f.read().strip()

        # Select a random media file from the media folder
        media_folder = 'media'
        media_files = [os.path.join(media_folder, f) for f in os.listdir(
            media_folder) if os.path.isfile(os.path.join(media_folder, f))]
        random_media_file = random.choice(media_files)

        # Check if session file exists, if not, skip the recipient
        session_path = os.path.join(session_folder, current_session)
        if not os.path.isfile(session_path):
            print(
                f"Session file {current_session} not found. Skipping recipient {recipient}.")
            continue
        session_names = [file for file in os.listdir(
            "accounts") if file.endswith('.session')]
        api_url = 'https://mtpro.xyz/api/?type=socks'
        proxy_config = await get_proxy_info(
            api_url, current_session, recipient, message_content, random_media_file)  # Await the get_proxy_info coroutine
        await send_secret_message(proxy_config, current_session, recipient, message_content, random_media_file)
        # Change session if an error occurs
        current_session = next(session_cycle)

    print(f"Total Success Count: {success_count}")
    print(f"Total Failure Count: {failure_count}")


# Example usage
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
