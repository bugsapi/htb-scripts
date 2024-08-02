import asyncio
import aiohttp
import ipaddress
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import socket
import multiprocessing
import os

# List of common ports to check first
COMMON_PORTS = [
    80, 443, 8080, 8443,  # Common web ports
    554, 8000, 8081, 8888,  # CCTV and other streaming ports
    8080, 8081, 8082, 8083, 8084, 8085, 8086, 8087, 8088,  # Jenkins and other web services
    3000, 4000, 5000, 8000, 9000,  # Common development server ports
    135, 139, 445, 3389,  # Windows services
    8200,  # HashiCorp Vault
    21, 22, 23, 25, 53, 110, 115, 123, 143, 161, 194, 443, 465, 587, 993, 995,  # Other common service ports
    1433, 1521, 3306, 5432,  # Database ports
    6379, 11211, 27017,  # Cache and NoSQL database ports
]

async def fetch(session, url):
    try:
        async with session.get(url, timeout=1) as response:
            if response.status == 200:
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')
                title = soup.title.string if soup.title else 'No title found'
                return url, title
            else:
                return url, f"Failed with status code: {response.status}"
    except Exception as e:
        return url, f"Error: {str(e)}"

async def check_port(ip, port, session):
    url = f"http://{ip}:{port}"
    result = await fetch(session, url)
    return result

async def scan_port(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        result = s.connect_ex((ip, port))
        if result == 0:
            return True
        return False

async def scan_ip(ip):
    open_ports = []
    
    # First, scan common ports
    for port in COMMON_PORTS:
        print(f"Scanning {ip}:{port}")
        if await scan_port(ip, port):
            open_ports.append(port)
            print(f"Open port found: {ip}:{port}")
    
    # If no common ports are open, scan all ports
    if not open_ports:
        print(f"No common ports open for {ip}. Scanning all ports...")
        for port in range(1, 65536):
            print(f"Scanning {ip}:{port}")
            if await scan_port(ip, port):
                open_ports.append(port)
                print(f"Open port found: {ip}:{port}")
    
    return ip, open_ports

async def process_chunk(ip_chunk):
    tasks = [scan_ip(str(ip)) for ip in ip_chunk]
    return await asyncio.gather(*tasks)

def worker(ip_chunk):
    return asyncio.run(process_chunk(ip_chunk))

def scan_range(ip_range):
    ip_list = list(ipaddress.IPv4Network(ip_range))
    cpu_count = os.cpu_count()
    chunk_size = max(1, len(ip_list) // cpu_count)
    ip_chunks = [ip_list[i:i + chunk_size] for i in range(0, len(ip_list), chunk_size)]

    with multiprocessing.Pool(processes=cpu_count) as pool:
        results = pool.map(worker, ip_chunks)

    flattened_results = [item for sublist in results for item in sublist]

    async def process_results():
        async with ClientSession() as session:
            for ip, ports in flattened_results:
                if ports:
                    print(f"IP: {ip}, Open Ports: {ports}")
                    for port in ports:
                        url, title = await check_port(str(ip), port, session)
                        print(f"URL: {url}, Title: {title}")

    asyncio.run(process_results())

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python script.py <ip_range>")
        sys.exit(1)
    
    ip_range = sys.argv[1]
    scan_range(ip_range)
