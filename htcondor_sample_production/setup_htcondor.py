import os

def setup_condor_folder(path="."):
    os.makedirs(os.path.join(path,"condor/error"))
    os.makedirs(os.path.join(path,"condor/log"))
    os.makedirs(os.path.join(path,"condor/output"))
    
def write_exec_file(path="."):
    content = """#!/bin/bash

file="$1"
evts="$2"
skip="$3"
ptype="$4"
idx="$5"
outdir="/afs/cern.ch/work/m/mmatthew/private/delete_me/cms-egamma-hlt-reg"

cmsRun rerunL1_cfg.py $file $evts $skip $idx
cmsRun Phase2_L1P2GT_HLT.py $ptype

xrdcopy -f output.root $outdir/output_$idx.root"""
    fname = os.path.join(path,"create_samples.sh")
    with open(fname,"w") as f:
        f.write(content)


def write_cond_file(path="."):
    content = """executable            = create_samples.sh
arguments             = $(file) $(evts) $(skip) $(ptype) $(idx)
+JobFlavour           = "workday"
should_transfer_files = YES
transfer_input_files  = rerunL1_cfg.py,Phase2_L1P2GT_HLT.py
getenv                = true
output                = condor/output/create_samples.out
error                 = condor/error/create_samples.err
log                   = condor/log/create_samples.log
MY.XRDCP_CREATE_DIR   = True
+DesiredOS            = "EL9"
max_materialize       = 500
queue file,evts,skip,ptype,idx from files.txt
"""

    fname = os.path.join(path,"condor.sub")
    with open(fname,"w") as f:
        f.write(content)

def find_line_in_block(lines,block,substring):
    inside_process = False
    for idx, line in enumerate(lines):
        stripped = line.strip()
        
        if line.startswith("process.") and inside_process:
                inside_process = False
        if stripped.startswith(block):
            inside_process = True
        if inside_process:
            if substring in stripped:
                return idx
            
        
    return 0

def process_l1_config(file,path="."):

    with open(file,"r") as f:
        lines = f.readlines()

    # Include input variables

    idx = lines.index("import FWCore.ParameterSet.Config as cms\n")
    content = ["import sys\n","import os,errno\n","file = sys.argv[1]\n","evts = sys.argv[2]\n","skip = sys.argv[3]\n"]

    for i,l in enumerate(content):
        lines.insert(idx+i,l)
    lines.insert(idx+i+1,"\n")
   
    # Set variable event number 
    idx = lines.index("process.maxEvents = cms.untracked.PSet(\n")
    lines[idx+1] = "input = cms.untracked.int32(int(evts)),\n"
    
    # Set variable file name
    idx = find_line_in_block(lines,"process.source","fileNames")
    lines[idx] = "fileNames = cms.untracked.vstring(file),\n" 

    # Include skipping of events
    lines.insert(idx+1,"skipEvents = cms.untracked.uint32(int(skip)),\n")

    # Set output filename

    idx = find_line_in_block(lines,"process.FEVTDEBUGHLToutput","fileName")
    lines[idx] = "fileName = cms.untracked.string('file:output_Phase2_L1T.root'),\n"

    new_file = os.path.join(path,file.split("/")[-1])
    with open(new_file,"w") as f:
        for l in lines:
            f.write(l)

def process_hlt_config(file,path="."):

    with open(file,"r") as f:
        lines = f.readlines()

    idx = lines.index("import FWCore.ParameterSet.Config as cms\n")
    content = ["ptype = sys.argv[1]\n","if ptype == 'ele': print('Setting workflow for electron samples')\n","elif ptype == 'pho': print('Setting workflow for photon samples')\n","else:\n","\tprint('Incorrect setting for ptype')\n","\texit()"]
    for i,l in enumerate(content):
        lines.insert(idx+i,l)
    lines.insert(idx+i+1,"\n")

    idx = lines.index("process = customiseHLTForEGammaNtuples(process)\n")
    lines.insert(idx+1,"process.EGammaNtuples.pType = cms.string(ptype)\n")

    idx = find_line_in_block(lines,"process.FEVTDEBUGHLToutput","fileName")
    lines[idx] = "fileName = cms.untracked.string('file:Phase2_L1P2GT_HLT.root'),\n"

    idx = find_line_in_block(lines,"process.source","fileNames")
    lines[idx] = "fileNames = cms.untracked.vstring('file:output_Phase2_L1T.root'),\n"

    new_file = os.path.join(path,file.split("/")[-1])
    with open(new_file,"w") as f:
        for l in lines:
            f.write(l)

def setup_directory(path="."):
    os.makedirs(path)
    setup_condor_folder(path)


path = "Spring24"
l1_file = "../rerunL1_cfg.py"
hlt_file = "../Phase2_L1P2GT_HLT.py"
setup_directory(path)
write_cond_file(path)
write_exec_file(path)
process_l1_config(l1_file,path)    
process_hlt_config(hlt_file,path)

# Make grid proxy available for htcondor to use xrootd. You can also follow the recommendations here: https://twiki.cern.ch/twiki/bin/view/CMSPublic/CRABPrepareLocal 
os.system("export X509_USER_PROXY=~/.gridProxy")
os.system("voms-proxy-init --rfc --voms cms -valid 192:00")
