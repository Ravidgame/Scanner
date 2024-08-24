import tkinter as tk
from tkinter import scrolledtext, messagebox
import ipaddress
import subprocess
import platform

def load_ip_ranges(file_path):
    try:
        with open(file_path, 'r') as file:
            ranges = file.readlines()
        return [ip.strip() for ip in ranges if ip.strip()]
    except FileNotFoundError:
        messagebox.showerror("Error", f"File {file_path} not found!")
        return []

def ping_ip(ip):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", str(ip)]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0, result.stdout.decode()
    except Exception as e:
        return False, str(e)

def extract_ping_time(output):
    try:
        lines = output.splitlines()
        for line in lines:
            if "time=" in line:
                time_str = line.split("time=")[-1].split()[0]
                return float(time_str.replace('ms', ''))
    except Exception:
        return float('inf')

def scan_ips():
    result_display.delete('1.0', tk.END)
    selected_range = ip_range_var.get().strip()

    ip_results = []

    try:
        network = ipaddress.ip_network(selected_range, strict=False)

        for ip in network.hosts():
            result_display.insert(tk.END, f"Checking {ip}...\n")

            success, output = ping_ip(ip)
            if success:
                ping_time = extract_ping_time(output)
                ip_results.append((ip, ping_time, output))

    except ValueError as e:
        result_display.insert(tk.END, f"Invalid IP range: {e}\n")
        return

    # مرتب‌سازی IPها براساس پینگ
    ip_results.sort(key=lambda x: x[1])

    # نمایش فقط IPهایی که پاسخ داده‌اند
    for ip, ping_time, output in ip_results:
        if ping_time < float('inf'):
            result_display.insert(tk.END, f"IP: {ip}\nPing: {ping_time} ms\nOutput:\n{output}\n")
            result_display.insert(tk.END, "-"*40 + "\n")

def update_ip_ranges(*args):
    file_name = "RENG IP.TXT" if ip_type_var.get() == "Cloudflare RENG IP" else "RENG IP WARP.TXT"
    ip_ranges = load_ip_ranges(file_name)
    ip_range_var.set("")  # Clear previous selection
    ip_range_menu['menu'].delete(0, 'end')  # Clear existing menu options
    for ip_range in ip_ranges:
        ip_range_menu['menu'].add_command(label=ip_range, command=tk._setit(ip_range_var, ip_range))

# ساخت پنجره اصلی
window = tk.Tk()
window.title("Cloudflare IP Scanner")
window.geometry('900x650')
window.configure(bg='#e3f2fd')  # رنگ پس‌زمینه پنجره

# فریم اصلی
main_frame = tk.Frame(window, bg='#ffffff', padx=20, pady=20, relief=tk.RAISED, borderwidth=2)
main_frame.pack(fill=tk.BOTH, expand=True)

# عنوان
title_label = tk.Label(main_frame, text="Cloudflare IP Scanner", font=('Helvetica', 26, 'bold'), bg='#ffffff', fg='#0288d1')
title_label.pack(pady=(0, 20))

# فریم برای منوهای انتخاب
menu_frame = tk.Frame(main_frame, bg='#ffffff')
menu_frame.pack(pady=(0, 20))

# منوی انتخاب نوع IP
ip_type_var = tk.StringVar(window)
ip_type_var.set("Cloudflare RENG IP")  # پیش‌فرض

label_ip_type = tk.Label(menu_frame, text="Select IP Type:", font=('Helvetica', 14, 'bold'), bg='#ffffff', fg='#0288d1')
label_ip_type.grid(row=0, column=0, padx=(0, 10), pady=10, sticky='w')

ip_type_menu = tk.OptionMenu(menu_frame, ip_type_var, "Cloudflare RENG IP", "WARP RENG IP")
ip_type_menu.config(bg='#03a9f4', fg='#ffffff', font=('Helvetica', 12), width=20, borderwidth=1, relief=tk.RAISED)
ip_type_menu.grid(row=0, column=1, pady=10, sticky='w')

# منوی کشویی برای انتخاب رنج IP
label_select_range = tk.Label(menu_frame, text="Select IP Range:", font=('Helvetica', 14, 'bold'), bg='#ffffff', fg='#0288d1')
label_select_range.grid(row=1, column=0, padx=(0, 10), pady=10, sticky='w')

ip_range_var = tk.StringVar(window)
ip_range_menu = tk.OptionMenu(menu_frame, ip_range_var, [])
ip_range_menu.config(bg='#03a9f4', fg='#ffffff', font=('Helvetica', 12), width=40, borderwidth=1, relief=tk.RAISED)
ip_range_menu.grid(row=1, column=1, pady=10, sticky='w')

# دکمه اسکن
button_scan = tk.Button(main_frame, text="Start Scan", command=scan_ips, font=('Helvetica', 14, 'bold'), bg='#0288d1', fg='#ffffff', relief=tk.RAISED, borderwidth=1)
button_scan.pack(pady=(0, 20))

# بخش نمایش نتایج
result_display = scrolledtext.ScrolledText(main_frame, width=100, height=25, font=('Helvetica', 12), bg='#ffffff', fg='#000000', borderwidth=2, relief=tk.SUNKEN)
result_display.pack(pady=(0, 20))

# بارگذاری اولیه رنج‌ها
update_ip_ranges()

# تنظیمات برای بروزرسانی منو
ip_type_var.trace('w', update_ip_ranges)

# اجرای پنجره اصلی
window.mainloop()
