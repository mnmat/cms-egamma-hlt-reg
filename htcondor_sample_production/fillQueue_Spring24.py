import os
import sys
import subprocess
import io
import argparse

def get_files(dataset):
    cmd = "dasgoclient --query='file dataset=%s | grep file.name, file.nevents'"%dataset
    #cmd = "dasgoclient --query='file dataset=%s'"%dataset
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,shell=True)
    output = proc.stdout.read()
    output = output.decode('utf-8').split('\n')
    
    ret = []
    for o in output:
        if o == "": continue
        f,e = o.split("   ")
        e.strip(" ")
        ret.append([f,e])

    return ret # files,events

def get_event(file):
    # This function works but takes way too long"
    cmd = "dasgoclient --query='file=%s | grep file.nevents'"%file
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,shell=True)
    output = proc.stdout.read()
    evt = output.decode('utf-8').split('\n')
    return evt

parser = argparse.ArgumentParser()
parser.add_argument("--total_events",type=int,default=300000)
parser.add_argument("--events_per_job",type=int,default=100)
parser.add_argument("--dataset",type=str,default="/DoubleElectron_FlatPt-1To100-gun/Phase2Spring24DIGIRECOMiniAOD-PU200_Trk1GeV_140X_mcRun4_realistic_v4-v2/GEN-SIM-DIGI-RAW-MINIAOD")
args = parser.parse_args()
dataset = args.dataset
total_events = args.total_events
events_per_job = args.events_per_job

try:
    files = get_files(dataset)
except:
    print("Failed getting dataset. Do you have a valid grid proxy?")
    exit()

if "lectron" in dataset:
    ptype = "ele"
elif "hoton" in dataset:
    ptype = "pho"
else:
    print("Incorrect dataset specified. Exit")
    exit() 

try:
    os.remove("files.txt")
except OSError:
    pass

with open("files.txt","w") as file:
    idx = 0
    for f,e in files:  # or another encoding
        for i in range(0,int(e),events_per_job):
            line = "%s,%s,%s,%s,%s\n"%(f,events_per_job,i,ptype,idx)
            idx = idx+1
            file.write(line)
            if idx*events_per_job >= total_events:
                exit()

