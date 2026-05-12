from scapy.all import ARP, Ether, srp
import socket

def get_vendor_from_mac(mac):
    vendor_prefixes = {
        "00:1A:79": "Ziggo",
        "A4:77:33": "Google",
        "3C:5A:B4": "Google",
        "D8:BB:C1": "Apple",
        "F0:18:98": "Apple",
        "B8:27:EB": "Raspberry Pi",
        "DC:A6:32": "Raspberry Pi",
        "E4:5F:01": "Raspberry Pi",
        "F4:F5:D8": "Samsung",
        "90:18:7C": "Samsung",
        "28:39:26": "Samsung",
        "00:1B:44": "SanDisk",
        "00:E0:4C": "Realtek",
        "3C:7C:3F": "ASUS",
        "FC:34:97": "ASUS",
        "14:CC:20": "TP-Link",
        "50:C7:BF": "TP-Link",
        "C0:25:E9": "TP-Link",
        "00:1D:0F": "Intel",
        "F8:B1:56": "Intel",
        "A0:36:BC": "Intel",
    }

    prefix = mac.upper()[0:8]
    return vendor_prefixes.get(prefix, "Unknown Vendor")


def detect_device_type(vendor, hostname):
    name = hostname.lower()
    vendor_lower = vendor.lower()

    if "ziggo" in name or "router" in name:
        return "Router"

    if "samsung" in vendor_lower or "phone" in name or "android" in name:
        return "Phone"

    if "apple" in vendor_lower or "iphone" in name or "ipad" in name:
        return "Apple Device"

    if "raspberry" in vendor_lower:
        return "Raspberry Pi"

    if "tp-link" in vendor_lower:
        return "Network Device"

    if "intel" in vendor_lower or "desktop" in name or "laptop" in name or "pc" in name:
        return "Computer"

    return "Unknown Device"


def get_local_ip():
    try:
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_socket.connect(("8.8.8.8", 80))
        local_ip = temp_socket.getsockname()[0]
        temp_socket.close()
        return local_ip
    except:
        return None


def get_network_range():
    local_ip = get_local_ip()

    if local_ip is None:
        return "192.168.178.0/24"

    parts = local_ip.split(".")

    if len(parts) != 4:
        return "192.168.178.0/24"

    return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"


def scan_network():
    devices = []

    ip_range = get_network_range()

    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")

    packet = ether / arp

    result = srp(packet, timeout=2, verbose=0)[0]

    for sent, received in result:
        ip = received.psrc
        mac = received.hwsrc

        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except:
            hostname = "Unknown"

        vendor = get_vendor_from_mac(mac)
        device_type = detect_device_type(vendor, hostname)

        devices.append({
           "ip": ip,
           "mac": mac,
           "hostname": hostname,
           "vendor": vendor,
           "device_type": device_type
})

    return devices