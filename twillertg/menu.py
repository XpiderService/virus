import os
import pickle
import random
import socket
import time
import requests
from telethon.sync import TelegramClient


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
            add_session(proxy_config)

            break
        else:
            print("Connection failed")
        print()


def get_random_api(lines):
    num_lines = len(lines)
    if num_lines % 2 != 0:
        print("Invalid number of lines in the API.txt file. Each API ID should have a corresponding API hash.")
        return None, None

    random_index = random.randrange(0, num_lines, 2)
    api_id = lines[random_index].strip()
    api_hash = lines[random_index + 1].strip()
    # Create a new Telegram client instance
    return api_id, api_hash


def add_session(proxy_config):
    # Load API ID and hash from the API.txt file
    if os.path.exists("API.txt"):
        with open("API.txt", "r") as f:
            lines = f.readlines()
            if len(lines) >= 2:
                api_id, api_hash = get_random_api(lines)
                if api_id is None or api_hash is None:
                    return
            else:
                print("Insufficient data in the API.txt file.")
                return
    else:
        print("API.txt file not found. Please make sure to provide the API ID and hash.")
        return

    while True:
        print(f"Using API ID: {api_id}")
        print(f"Using API Hash: {api_hash}")

        phone_number = input(
            "Enter your phone number, 'menu' or 'exit': ")

        if phone_number.lower() == 'exit':
            print("Exiting...")
            return
        elif phone_number.lower() == 'menu':
            print("Returning to the menu...")
            break

        session_dir = "accounts"
        # Create session directory if it does not exist
        if not os.path.exists(session_dir):
            os.makedirs(session_dir)

        session_file = os.path.join(session_dir, f'{phone_number}')

        client = TelegramClient(session_file, api_id, api_hash)
        client.proxy = proxy_config
        try:
            client.connect()
            if not client.is_user_authorized():
                client.send_code_request(phone_number)
                code = input("Enter the confirmation code: ")
                client.sign_in(phone_number, code)
        except Exception as e:
            print(f"Error creating session for {phone_number}: {e}")
            return
        finally:
            client.disconnect()

        print(f"Session file for {phone_number} created: {session_file}")

        # Load the existing session dictionary
        if os.path.exists("session_dict.pickle"):
            with open("session_dict.pickle", "rb") as f:
                session_dict = pickle.load(f)
        else:
            session_dict = {}

        # Update the session dictionary
        session_dict[phone_number] = session_file

        # Save the updated session dictionary
        with open("session_dict.pickle", "wb") as f:
            pickle.dump(session_dict, f)

        time.sleep(5)
        print("Session added successfully.")


def main_menu():
    while True:
        print("\n=== Main Menu ===")
        print("\n=== Powered with Proxy===")
        print("1. Add Session Account")
        print("2. Check for Banned Accounts")
        print("3. Add Active User to Public Group")
        print("4. scrape Private or Public")
        print("5. Mass Direct Message")
        print("6. Exit")

        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            # Replace the URL below with the actual API URL you have
            api_url = 'https://mtpro.xyz/api/?type=socks'
            get_proxy_info(api_url)
        elif choice == "2":
            # Execute the connect.py file
            os.system("python plugins/check.py")
        elif choice == "3":
            # Execute the connect.py file
            os.system("python plugins/memberadd.py")
        elif choice == "4":
            # Execute the connect.py file
            os.system("python plugins/scrape.py")
        elif choice == "5":
            # Execute the connect.py file
            os.system("python plugins/main.py")
        elif choice == "6":
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")


# Run the main menu
main_menu()
