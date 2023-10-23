import csv
import random
import socket
import threading
import ftplib
import re

# FTPサーバーからバナー情報を取得する関数
def get_ftp_banner_version(url, port):
    try:
        ftp_socket = ftplib.FTP()
        ftp_socket.connect(url, port)
        banner = ftp_socket.getwelcome()
        return banner
    except Exception as e:
        return None

# MySQLサーバーからバナー情報を取得する関数
def get_mysql_banner_version(url, port):
    try:
        mysql_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mysql_socket.connect((url, port))
        banner = mysql_socket.recv(1024).decode('utf-8')
        mysql_socket.close()
        return banner
    except Exception as e:
        return None

# UnrealIRCDのバージョンを取得する関数
def get_unrealircd_version(url, port):
    try:
        irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        irc_socket.connect((url, port))
        banner = irc_socket.recv(1024).decode('utf-8')
        irc_socket.close()
        return banner
    except Exception as e:
        return None

# バナー情報からFTPサーバーのバージョンを抽出する関数
def extract_ftp_version(banner):
    version_pattern = r"\(.*?([0-9]+\.[0-9]+\.[0-9]+).*?\)"
    match = re.search(version_pattern, banner)
    if match:
        return match.group(1)
    else:
        return None

# ポートスキャン関数
def port_scan(url, ftp_versions, mysql_version, unrealircd_version):
    open_ports = []

    for port, version in ftp_versions.items():
        try:
            banner = get_ftp_banner_version(url, port)
            if banner:
                ftp_version = extract_ftp_version(banner)
                if ftp_version == version:
                    open_ports.append(port)
        except Exception as e:
            pass

    try:
        banner = get_mysql_banner_version(url, 3306)  # MySQLの標準ポート
        if banner and mysql_version in banner:
            open_ports.append(3306)
    except Exception as e:
        pass

    try:
        banner = get_unrealircd_version(url, 6667)  # UnrealIRCDの標準ポート
        if banner and unrealircd_version in banner:
            open_ports.append(6667)
    except Exception as e:
        pass

    return open_ports

# IPアドレス生成関数
def generate_random_url():
    while True:
        first_octet = random.randint(1, 191)  # 1-191の範囲で生成
        if first_octet == 10:
            continue  # 10.0.0.0 - 10.255.255.255はプライベートIPアドレスの範囲
        if first_octet == 172:
            second_octet = random.randint(16, 31)  # 172.16.0.0 - 172.31.255.255はプライベートIPアドレスの範囲
        else:
            second_octet = random.randint(0, 255)
        if first_octet == 192 and second_octet == 168:
            continue  # 192.168.0.0 - 192.168.255.255はプライベートIPアドレスの範囲
        return f"{first_octet}.{second_octet}.{random.randint(1, 255)}.{random.randint(1, 255)}"

# CSVファイルに結果を記録
def write_to_csv(url, open_ports):
    with open('open_ports.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([url, open_ports])

# スレッドでポートスキャンを実行
def scan_in_thread(ftp_versions, mysql_version, unrealircd_version):
    while True:
        url = generate_random_url()
        open_ports = port_scan(url, ftp_versions, mysql_version, unrealircd_version)
        if open_ports:
            print(f"Open ports for {url}: {open_ports}")
            write_to_csv(url, open_ports)

# スレッド数
num_threads = 30

# 検出対象のFTPサーバーのバージョンとMySQLのバージョン
ftp_versions = {"vsftpd": "2.3.4", "ProFTPd": "1.3.3c"}
mysql_version = "phpMyAdmin 3.5.2.2"
unrealircd_version = "3.2.8.1"

# CSVファイルを初期化
with open('open_ports.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['URL', 'Open Ports'])

# スレッドを開始
threads = []
for _ in range(num_threads):
    t = threading.Thread(target=scan_in_thread, args=(ftp_versions, mysql_version, unrealircd_version))
    t.start()
    threads.append(t)

# スレッドが終了するまで待つ
for t in threads:
    t.join()

# 無限に繰り返す
while True:
    pass
