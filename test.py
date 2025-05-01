import subprocess

def get_wifi_info():
    try:
        process = subprocess.Popen(['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport','-I'], stdout=subprocess.PIPE)
        out, err = process.communicate()
        process.wait()

        wifi_info = {}
        for line in out.decode("utf-8").split("\n"):
            if ": " in line:
                key, val = line.split(": ")
                key = key.replace(" ", "")
                val = val.strip()

                wifi_info[key] = val
    except:
        process = subprocess.Popen(['netsh', 'wlan', 'show', 'interfaces'],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               shell=True)
        out, err = process.communicate()
        process.wait()

        wifi_info = {}
        for line in out.decode('utf-8', errors='ignore').split('\n'):
            if ':' in line:
                parts = line.split(':', 1)
                key = parts[0].strip().replace(' ', '')
                val = parts[1].strip()
                wifi_info[key] = val

    return wifi_info


wifi_info = get_wifi_info()
print(wifi_info["SSID"])