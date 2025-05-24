import requests
import ipaddress
from concurrent.futures import ThreadPoolExecutor
from requests.auth import HTTPDigestAuth
import threading

def send_blink_command(ip: str, blink_state: bool, success_counter: list, lock: threading.Lock):
    url = f"http://{ip}/cgi-bin/blink.cgi"
    headers = {"Content-Type": "application/json"}
    data = {"blink": blink_state}
    auth = HTTPDigestAuth("root", "root")
    
    try:
        response = requests.post(url, json=data, headers=headers, auth=auth, timeout=10)
        if response.status_code == 200:
            with lock:
                success_counter[0] += 1
            print(f"Success: {ip} - Blink set to {blink_state}")
        else:
            print(f"Failed: {ip} - Status code {response.status_code}")
    except requests.ConnectionError:
        print(f"Error: {ip} - Connection refused")
    except requests.Timeout:
        print(f"Error: {ip} - Request timed out")
    except requests.HTTPError as e:
        print(f"Error: {ip} - HTTP error: {str(e)}")
    except requests.RequestException as e:
        print(f"Error: {ip} - Request error: {str(e)}")
    except Exception as e:
        print(f"Error: {ip} - Unexpected error: {str(e)}")

def process_ip_range(blink_state: bool):
    network = ipaddress.ip_network("172.16.30.0/23")  # Covers 172.16.10.0 to 172.16.11.255
    success_counter = [0]  # Use list to allow modification in threads
    lock = threading.Lock()  # Thread-safe lock for success_counter
    
    with ThreadPoolExecutor(max_workers=50) as executor:  # Limit to 50 concurrent requests
        executor.map(lambda ip: send_blink_command(str(ip), blink_state, success_counter, lock), network)
    
    print(f"{success_counter[0]}")

def main():
    while True:
        print("\nBlink Control Menu:")
        print("1. Set blink to True")
        print("2. Set blink to False")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == "1":
            print("Sending blink: true to all IPs...")
            process_ip_range(True)
        elif choice == "2":
            print("Sending blink: false to all IPs...")
            process_ip_range(False)
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()