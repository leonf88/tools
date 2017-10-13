# coding: utf-8
import subprocess

process = subprocess.Popen(["networksetup", "-listallnetworkservices"], stdout=subprocess.PIPE)
for line in process.stdout:
    name = line.strip()
    print name
    if "云梯" in name:
        subprocess.call(["networksetup", "-removenetworkservice", name])
#print output
