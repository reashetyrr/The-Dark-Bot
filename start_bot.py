import atexit
import time
import os
import subprocess


processes = []


print('Starting the rabbitmq listener.')
listener = subprocess.Popen(['C:\\global_python37_venv\\Scripts\\python.exe', 'C:/Users/Administrator/Desktop/TDR/TDR/rabbit_listener.py'], shell=True)
processes.append(listener)


print('Start the bot.')
handler = subprocess.Popen(['C:\\global_python37_venv\\Scripts\\python.exe', 'C:/Users/Administrator/Desktop/TDR/TDR/run.py'], shell=True)
processes.append(handler)


def exit_called():
    timeout_sec = 5
    for p in processes:  # list of your processes
        p_sec = 0
        for second in range(timeout_sec):
            if p.poll() is None:
                time.sleep(1)
        p_sec += 1
        if p_sec >= timeout_sec:
            p.kill()


atexit.register(exit_called)


exit_codes = [process.wait() for process in processes]
