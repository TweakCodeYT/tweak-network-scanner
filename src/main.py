import customtkinter as ctk
import threading
import csv
import os
from scanner import scan_network
DEMO_MODE = True
last_scan_results = []

# --------------------------------
# APP SETTINGS
# --------------------------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# --------------------------------
# FUNCTIONS
# --------------------------------
def sanitize_device(ip, hostname, mac):
    if not DEMO_MODE:
        return ip, hostname, mac

    fake_ip = "10.0.0." + str(abs(hash(ip)) % 250)

    if "router" in hostname.lower():
        fake_hostname = "Demo-Router"
    elif "desktop" in hostname.lower():
        fake_hostname = "Demo-PC"
    else:
        fake_hostname = "Unknown Device"

    fake_mac = "XX:XX:XX:XX:XX"

    return fake_ip, fake_hostname, fake_mac

def export_to_csv():
    if not last_scan_results:
        status_label.configure(text="Status: No scan data")
        return

    os.makedirs("exports", exist_ok=True)

    filepath = os.path.join("exports", "network_scan.csv")

    with open(filepath, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "IP Address",
            "Hostname",
            "MAC Address",
            "Vendor",
            "Device Type",
            "Status"
        ])

        for device in last_scan_results:
            writer.writerow(device)

    status_label.configure(text="Status: CSV Exported")

def clear_device_list():
    for widget in devices_list.winfo_children():
        widget.destroy()


def add_device(ip, hostname, mac, vendor, device_type, status):
    device_row = ctk.CTkFrame(devices_list)
    device_row.pack(fill="x", pady=6, padx=5)

    device_info = ctk.CTkLabel(
        device_row,
        text=f"IP: {ip}   |   Hostname: {hostname}   |   MAC: {mac}   |   Vendor: {vendor}   |   Type: {device_type}   |   Status: {status}",
        font=("Arial", 14)
    )
    device_info.pack(anchor="w", padx=15, pady=12)


def start_scan():
    scan_thread = threading.Thread(target=run_scan)
    scan_thread.start()

def run_scan():
    status_label.configure(text="Status: Scanning...")
    app.update()

    clear_device_list()

    devices = scan_network()
    global last_scan_results
    last_scan_results = []
    online_devices = 0

    for device in devices:
        try:
            ip = device.get("ip", "Unknown")
            hostname = device.get("hostname", "Unknown")
            mac = device.get("mac", "Unknown")
            vendor = device.get("vendor", "Unknown Vendor")
            device_type = device.get("device_type", "Unknown Device")

            ip, hostname, mac = sanitize_device(ip, hostname, mac)

            add_device(
                ip,
                hostname,
                mac,
                vendor,
                device_type,
                "Online"
            )
            last_scan_results.append([
    ip,
    hostname,
    mac,
    vendor,
    device_type,
    "Online"
])
            online_devices += 1

        except Exception as e:
            print(f"Device processing error: {e}")

    device_count.configure(text=str(len(devices)))
    online_count.configure(text=str(online_devices))

    status_label.configure(text="Status: Scan Complete")

# --------------------------------
# MAIN WINDOW
# --------------------------------

app = ctk.CTk()
app.title("Tweak Network Scanner V1")
app.geometry("1400x800")

# --------------------------------
# SIDEBAR
# --------------------------------

sidebar = ctk.CTkFrame(app, width=250, corner_radius=0)
sidebar.pack(side="left", fill="y")

title_label = ctk.CTkLabel(
    sidebar,
    text="Tweak Scanner",
    font=("Arial", 26, "bold")
)
title_label.pack(pady=(30, 20))

scan_button = ctk.CTkButton(
    sidebar,
    text="Start Scan",
    height=40,
    command=start_scan
)
export_button = ctk.CTkButton(
    sidebar,
    text="Export CSV",
    height=40,
    command=export_to_csv
)
export_button.pack(padx=20, pady=10, fill="x")
scan_button.pack(padx=20, pady=10, fill="x")

status_label = ctk.CTkLabel(
    sidebar,
    text="Status: Idle",
    font=("Arial", 14)
)
status_label.pack(pady=10)

# --------------------------------
# MAIN CONTENT
# --------------------------------

main_frame = ctk.CTkFrame(app)
main_frame.pack(side="right", fill="both", expand=True)

topbar = ctk.CTkFrame(main_frame, height=80)
topbar.pack(fill="x", padx=20, pady=20)

dashboard_label = ctk.CTkLabel(
    topbar,
    text="Network Dashboard",
    font=("Arial", 28, "bold")
)
dashboard_label.pack(side="left", padx=20, pady=20)

stats_frame = ctk.CTkFrame(main_frame)
stats_frame.pack(fill="x", padx=20, pady=(0, 20))

device_card = ctk.CTkFrame(stats_frame, height=100)
device_card.pack(side="left", padx=10, pady=10, fill="both", expand=True)

device_title = ctk.CTkLabel(
    device_card,
    text="Devices Found",
    font=("Arial", 18)
)
device_title.pack(pady=(20, 5))

device_count = ctk.CTkLabel(
    device_card,
    text="0",
    font=("Arial", 32, "bold")
)
device_count.pack()

online_card = ctk.CTkFrame(stats_frame, height=100)
online_card.pack(side="left", padx=10, pady=10, fill="both", expand=True)

online_title = ctk.CTkLabel(
    online_card,
    text="Online Devices",
    font=("Arial", 18)
)
online_title.pack(pady=(20, 5))

online_count = ctk.CTkLabel(
    online_card,
    text="0",
    font=("Arial", 32, "bold")
)
online_count.pack()

devices_frame = ctk.CTkFrame(main_frame)
devices_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

devices_title = ctk.CTkLabel(
    devices_frame,
    text="Detected Devices",
    font=("Arial", 22, "bold")
)
devices_title.pack(anchor="w", padx=20, pady=20)

devices_list = ctk.CTkScrollableFrame(devices_frame)
devices_list.pack(fill="both", expand=True, padx=20, pady=(0, 20))

# --------------------------------
# RUN APP
# --------------------------------

app.mainloop()