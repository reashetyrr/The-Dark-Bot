import subprocess

print('Starting the rabbitmq listener.')
listener = subprocess.run(['C:\\global_python37_venv\\Scripts\\python.exe', 'C:/Users/Administrator/Desktop/TDR/TDR/rabbit_listener.py'], shell=True, check=True)

print('Start the bot.')
handler = subprocess.run(['C:\\global_python37_venv\\Scripts\\python.exe', 'C:/Users/Administrator/Desktop/TDR/TDR/run.py'], shell=True, check=True)