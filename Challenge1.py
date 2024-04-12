import subprocess

process1 = subprocess.Popen(["python", "Challenge1Client1.py"]) # Create and launch process pop.py using python interpreter
process2 = subprocess.Popen(["python", "Challenge1Client2.py"])
process3 = subprocess.Popen(["python", "Challenge1RecvClient.py"])

process1.wait() # Wait for process1 to finish (basically wait for script to finish)
process2.wait()
process3.wait()