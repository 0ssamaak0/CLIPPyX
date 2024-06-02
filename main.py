import subprocess
import yaml

# Load the configuration file
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

subprocess.run(["python", "Index/everything_images.py"])
if config["server_os"] == "wsl":
    print("Running in WSL")
    subprocess.check_call(["wsl", "-e", "bash", "server_wsl.sh"])
elif config["server_os"] == "windows":
    print("Running in Windows")
    subprocess.run(["python", "server.py"])
