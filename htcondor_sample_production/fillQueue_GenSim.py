import os
import sys
import subprocess
import io
import ROOT
import time

def get_files_from_dir(d,tree="Events"):
    ls = os.listdir(d)
    files = [os.path.join(d,x) for x in ls if ".root" in x]
    ret = []
    
    for file in files:
        t = time.time()
        f = ROOT.TFile.Open(file)
        e = f.Get(tree).GetEntries()
        ret.append([file,e])
        print(time.time()-t)
    return ret

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

def get_sites(file):
    cmd = "dasgoclient --query='%s'"%file
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    output = proc.stdout.read()
    site = output.decode('utf-8').split('\n')
    return site

total_events = 2000000 # 2M samples
events_per_job = 1000
dataset = "/DoubleElectron_FlatPt-1To100-gun/Phase2Spring24GS-140X_mcRun4_realistic_v4-v1/GEN-SIM"
#dataset = "/DoublePhoton_FlatPt-1To100-gun/Phase2Spring24GS-140X_mcRun4_realistic_v4-v1/GEN-SIM"

if "lectron" in dataset:
    ptype = "ele"
elif "hoton" in dataset:
    ptype = "pho"
else:
    print("Incorrect dataset specified. Exit")
    exit()    


path = "/eos/cms/store/group/dpg_hgcal/comm_hgcal/mmatthew/BDT/high_stats/ruccio/electrons/s1GenSim"
#path = "/eos/cms/store/group/dpg_hgcal/comm_hgcal/mmatthew/BDT/high_stats/pho/s1GenSim"

#files = get_files(dataset)
files = get_files_from_dir(path)
try:
    os.remove("files.txt")
except OSError:
    pass

event_counter = 0
with open("files.txt","w") as file:
    idx = 0
    for f,e in files:  # or another encoding
        for i in range(0,int(e),events_per_job):
            line = "%s,%s,%s,%s,%s\n"%(f,events_per_job,i,ptype,idx)
            idx = idx+1
            file.write(line)
            if event_counter > total_events:
                exit()
            event_counter = event_counter + events_per_job 
