import subprocess

def get_wifi_info():
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

	return wifi_info

wifi_info = get_wifi_info()
print(wifi_info["SSID"])