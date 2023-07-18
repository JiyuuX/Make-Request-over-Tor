import subprocess
import secrets
import string
import requests
from stem import Signal
from stem.control import Controller
from fake_useragent import UserAgent

TOR_CONTROL_PORT = 9051
TOR_PROXY = "socks5://127.0.0.1:9050"

def generate_tor_control_password():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for _ in range(32))
    return password

# torrc file may have different path on other OS. You have to check it.
def save_tor_control_password_to_torrc(password):
    with open('/etc/tor/torrc', 'a') as torrc_file:
        torrc_file.write(f'\nHashedControlPassword {password}\n')

def change_tor_identity():
    with Controller.from_port(port=TOR_CONTROL_PORT) as controller:
        controller.authenticate()
        controller.signal(Signal.NEWNYM)

def send_request(url):
    session = requests.session()
    session.proxies = {'http': TOR_PROXY, 'https': TOR_PROXY}

    user_agent = UserAgent().random
    headers = {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }

    try:
        response = session.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"Request to {url} succeeded. IP: {response.json().get('origin', 'Unknown')}")
        else:
            print(f"Request to {url} failed. Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request to {url} failed. Error: {e}")

if __name__ == "__main__":
    TOR_PASSWORD = generate_tor_control_password()
    save_tor_control_password_to_torrc(TOR_PASSWORD)

    urls = [
        "https://whatismyipaddress.com",
        # you can add more URLs here
    ]

    # Initialize Tor with the new password
    subprocess.run(['sudo', 'service', 'tor', 'restart'], check=True)

    for url in urls:
        change_tor_identity()
        send_request(url)
