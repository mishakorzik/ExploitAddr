#!/usr/bin/python3
from censys.search import CensysHosts
import requests, threading, time
import subprocess as sp
censys = CensysHosts()

author  = "Misha Korzhik"
version = "1.0.1"
global result
global update
update = "unknown"
result = False
sort = "None"

def check():
    global update
    try:
        get = str(requests.get("https://raw.githubusercontent.com/mishakorzik/ExploitAddr/main/version.txt", timeout=5).text)
        get = get.replace("\n", "")
        if get == version:
            update = f"\033[01;33mNo updates\033[0m"
        else:
            update = f"\033[01;32mFound new version\033[0m"
    except:
        update = f"\033[01;31mFailed to check\033[0m"

def detect(host):
    _, detect = sp.getstatusoutput("curl --head --connect-timeout 4 "+host)
    if ": Apache" in detect:
        print(f" \033[01;32m[\033[0ms\033[01;32m]\033[0m {host} - \033[01;33mApache Server\033[0m")
    elif ": gunicorn" in detect:
        print(f" \033[01;32m[\033[0ms\033[01;32m]\033[0m {host} - \033[01;33mGunicorn Server\033[0m")
    elif ": nginx" in detect:
        print(f" \033[01;32m[\033[0ms\033[01;32m]\033[0m {host} - \033[01;33mNginx Server\033[0m")
    elif ": Werkzeug" in detect:
        print(f" \033[01;32m[\033[0ms\033[01;32m]\033[0m {host} - \033[01;33mWerkzeug Server\033[0m")
    elif ": cloudflare" in detect:
        print(f" \033[01;32m[\033[0ms\033[01;32m]\033[0m {host} - \033[01;33mCloudflare Server\033[0m")
    else:
        print(f" \033[01;31m[\033[0ms\033[01;31m]\033[0m {host} - \033[01;33munknown server\033[0m")

def banner():
    print("   ____           __     _ __  ___     __   __   ")
    print("  / __/_ __ ___  / /__  (_) /_/ _ |___/ /__/ /___")
    print(" / _/ \ \ // _ \/ / _ \/ / __/ __ / _  / _  / __/")
    print("/___//_\_\/ .__/_/\___/_/\__/_/ |_\_,_/\_,_/_/   ")
    print("         /_/                                     ")
    print(" ")
    print(f"   \033[01;34mAuthor\033[0m   : "+author)
    print(f"   \033[01;34mVersion\033[0m  : v"+version)
    print(f"   \033[01;34mUpdate\033[0m   : "+update)
    print(" ")

def main():
    banner()
    host = str(input("Enter host (\033[01;34mex\033[0m. github.com): "))
    if "." in host:
        pass
    else:
        print(" \033[01;31m[\033[0m-\033[01;31m] \033[0merror: unknown host")
        exit(1)
    query = f"({host}) and services.service_name=`HTTP`"
    software = str(input("Sort by specific software (\033[01;32myes\033[0m/\033[01;31mno\033[0m): "))
    if software == "yes" or software == "Yes" or software == "Y" or software == "y":
        software = str(input("Enter software name (\033[01;34mex\033[0m. Nginx): "))
        if software == "apache":
            query = f"(({host}) and services.service_name=`HTTP`) and services.software.vendor=`Apache`"
        elif software == "synology":
            query = f"(({host}) and services.service_name=`HTTP`) and services.software.vendor=`Synology`"
        elif software == "Nginx":
            query = f"(({host}) and services.service_name=`HTTP`) and services.software.vendor=`nginx`"
        elif software == "php":
            query = f"(({host}) and services.service_name=`HTTP`) and services.software.vendor=`PHP`"
        elif software == "kenivia":
            query = f"(({host}) and services.service_name=`HTTP`) and services.software.vendor=`Kenivia`"
        elif software == "dovecot":
            query = f"(({host}) and services.service_name=`HTTP`) and services.software.vendor=`Dovecot`"
        elif software == "ubuntu":
            query = f"(({host}) and services.service_name=`HTTP`) and services.software.vendor=`Ubuntu`"
        elif software == "debian":
            query = f"(({host}) and services.service_name=`HTTP`) and services.software.vendor=`Debian`"
        elif software == "oracle":
            query = f"(({host}) and services.service_name=`HTTP`) and services.software.vendor=`Oracle`"
        elif software == "mariadb":
            query = f"(({host}) and services.service_name=`HTTP`) and services.software.vendor=`MariaDB`"
        elif software == "openbsd":
            query = f"(({host}) and services.service_name=`HTTP`) and services.software.vendor=`OpenBSD`"
        elif software == "parallels":
            query = f"(({host}) and services.service_name=`HTTP`) and services.software.vendor=`Parallels`"
        elif software == "genivia":
            query = f"(({host}) and services.service_name=`HTTP`) and services.software.vendor=`Genivia`"
        elif software == "postfix":
            query = f"(({host}) and services.service_name=`HTTP`) and services.software.vendor=`Postfix`"
        else:
            query = f"(({host}) and services.service_name=`HTTP`) and services.software.vendor=`{software}`"
    query = censys.search(query, per_page=100)
    query = query()
    detect(host)
    for check in query:
        threading.Thread(target=scan, kwargs={"check": check, "host": host}).start()
    time.sleep(10)
    if result == False:
        print(" \033[01;31m[\033[0m-\033[01;31m] \033[0merror: no result")

def scan(check, host):
    ip = check["ip"]
    if ":" in ip: ip = "["+ip+"]"
    try: dns = check["dns"]["reverse_dns"]["names"][0]
    except: dns = "None"
    route = str(check["autonomous_system"]["bgp_prefix"])
    code = str(check["autonomous_system"]["country_code"])
    for services in check["services"]:
        port = str(services["port"])
        name = str(services["extended_service_name"])
    try:
        if dns == "None":
            status = "000"
        else:
            status = str(requests.get("http://"+dns, timeout=5, headers={"User-Agent": "He1Zen Scanner "+version}).status_code)
    except:
        status = "408"
    if status == "200":
        status = "» \033[01;32m200\033[0m"
        show = f"\033[01;32m[\033[0m+\033[01;32m]"
    elif status == "201":
        status = "» \033[01;32m201\033[0m"
        show = f"\033[01;32m[\033[0m+\033[01;32m]"
    elif status == "301":
        status = "» \033[01;32m301\033[0m"
        show = f"\033[01;32m[\033[0m+\033[01;32m]"
    elif status == "302":
        status = "» \033[01;32m302\033[0m"
        show = f"\033[01;32m[\033[0m+\033[01;32m]"
    elif status == "400":
        status = "» \033[01;32m302\033[0m"
        show = f"\033[01;32m[\033[0m+\033[01;32m]"
    elif status == "403":
        status = "» \033[01;32m302\033[0m"
        show = f"\033[01;32m[\033[0m+\033[01;32m]"
    elif status == "404":
        status = "» \033[01;32m302\033[0m"
        show = f"\033[01;32m[\033[0m+\033[01;32m]"
    elif status == "408":
        status = "» \033[01;31m408\033[0m"
        show = f"\033[01;33m[\033[0m?\033[01;33m]"
    elif status == "000":
        dns = ""
        status = ""
        show = f"\033[01;31m[\033[0m-\033[01;31m]"
    elif status == "":
        status = ""
        show = f"\033[01;31m[\033[0m-\033[01;31m]"
    else:
        status = f"» \033[01;31m{status}\033[0m"
        show = f"\033[01;31m[\033[0m-\033[01;31m]"
    if dns == "":
        pass
    else:
        route = route + ","
    if name == "HTTP" or name == "HTTPS" or name == "POSTGRES":
        global result
        result = True
        print(f" {show} \033[0m{host} - {code} - \033[01;33m{ip}\033[0m:\033[01;33m{port}\033[0m, \033[01;32m{name}\033[0m - {route} \033[01;33m{dns}\033[0m {status}")

check()
main()
