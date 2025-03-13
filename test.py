import platform
import subprocess
import re

def get_wifi_signal_strength():
    system = platform.system()
    
    if system == "Linux":
        try:
            result = subprocess.run(["iwconfig"], capture_output=True, text=True)
            match = re.search(r"Signal level=(-?\d+) dBm", result.stdout)
            if match:
                return f"WiFi Signal Strength: {match.group(1)} dBm"
        except Exception as e:
            return f"Error: {e}"
    
    elif system == "Darwin":  # macOS
        try:
            result = subprocess.run(["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-I"], capture_output=True, text=True)
            match = re.search(r"agrCtlRSSI: (-?\d+)", result.stdout)
            if match:
                return f"WiFi Signal Strength: {match.group(1)} dBm"
        except Exception as e:
            return f"Error: {e}"
    
    elif system == "Windows":
        try:
            result = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True)
            match = re.search(r"Signal\s*: (\d+)", result.stdout)
            if match:
                signal_percent = int(match.group(1))
                return f"WiFi Signal Strength: {signal_percent}%"
        except Exception as e:
            return f"Error: {e}"
    
    else:
        return "Unsupported OS"
while True:
    if __name__ == "__main__":
        print(get_wifi_signal_strength())
     