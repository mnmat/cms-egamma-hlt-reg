import os
import sys
import subprocess
import argparse

SAMPLE_GENSIM = "/DoubleElectron_FlatPt-1To100-gun/Phase2Spring24GS-140X_mcRun4_realistic_v4-v1/GEN-SIM"
SAMPLE_SPRING24 = "/DoubleElectron_FlatPt-1To100-gun/Phase2Spring24DIGIRECOMiniAOD-PU200_Trk1GeV_140X_mcRun4_realistic_v4-v2/GEN-SIM-DIGI-RAW-MINIAOD"
WORKDIR = "/afs/cern.ch/work/m/mmatthew/private/delete_me/cms-egamma-hlt-reg/" 
N = 20

def getFile(sample):
    os.system("voms-proxy-init --voms cms --valid 168:00")
    das = "dasgoclient --query='file dataset=%s status=*'"%sample
    print(das)
    std_output, std_error = subprocess.Popen(das,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
    files = std_output.decode("ascii").replace('\n',' ')
    files_ = files.split(" ")
    if len(files_)==0:
        print("No files found")
        exit(0)
    return files_[0]

def setup_gensim_cfg():
    file = "/eos/cms/store/group/dpg_hgcal/comm_hgcal/mmatthew/BDT/high_stats/electrons/s1GenSim/00c66fb0-0aae-421d-a429-12abec9dbb2e.root"
    setupHLT = "cmsDriver.py \
--python_filename test_noL1P2GT_cfg.py \
--eventcontent FEVTDEBUGHLT \
--pileup AVE_200_BX_25ns \
--customise SLHCUpgradeSimulations/Configuration/aging.customise_aging_1000,SimGeneral/MixingModule/customiseStoredTPConfig.higherPtTP,Configuration/DataProcessing/Utils.addMonitoring,L1Trigger/Configuration/customisePhase2FEVTDEBUGHLT.customisePhase2FEVTDEBUGHLT,L1Trigger/Configuration/customisePhase2TTOn110.customisePhase2TTOn110,EgRegresNtuples/EGammaNtuples/customizeHLTForEgammaNtuples.customiseHLTForEGammaNtuples,HLTrigger/Configuration/customizeHLTforEGamma.customiseEGammaMenuDev,HLTrigger/Configuration/customizeHLTforEGamma.customiseEGammaInputContent \
 --datatier GEN-SIM-DIGI-RAW \
--fileout file:test.root \
--pileup_input dbs:/MinBias_TuneCP5_14TeV-pythia8/Phase2Spring24GS-140X_mcRun4_realistic_v4-v1/GEN-SIM \
--conditions 140X_mcRun4_realistic_v4 \
--step DIGI:pdigi_valid,L1TrackTrigger,L1,DIGI2RAW,HLT:75e33 \
--nThreads 8 \
--geometry Extended2026D110 \
--nStreams 2 \
--filein file:/eos/cms/store/group/dpg_hgcal/comm_hgcal/mmatthew/BDT/high_stats/electrons/s1GenSim/4d53b6f8-d99b-407f-a03a-516709227b66.root \
--era Phase2C17I13M9 \
--mc \
-n 8"
    os.system("voms-proxy-init --voms cms --valid 168:00")
    os.system(setupHLT)
 
    

def setup_spring24_cfg():
    file = getFile(SAMPLE_SPRING24)
    setupL1 = " cmsDriver.py Phase2 -s L1,L1TrackTrigger \
--conditions auto:phase2_realistic_T33 \
--geometry Extended2026D110 \
--era Phase2C17I13M9 \
--eventcontent FEVTDEBUGHLT \
--datatier GEN-SIM-DIGI-RAW-MINIAOD \
--customise SLHCUpgradeSimulations/Configuration/aging.customise_aging_1000,Configuration/DataProcessing/Utils.addMonitoring,L1Trigger/Configuration/customisePhase2FEVTDEBUGHLT.customisePhase2FEVTDEBUGHLT,L1Trigger/Configuration/customisePhase2TTOn110.customisePhase2TTOn110 \
--filein %s  \
--fileout file:output_Phase2_L1T.root \
--dirout %s \
--python_filename rerunL1_cfg.py \
--inputCommands='keep *, drop l1tPFJets_*_*_*, drop l1tTrackerMuons_l1tTkMuonsGmt*_*_HLT' \
--outputCommands='drop l1tTrackerMuons_l1tTkMuonsGmt*_*_HLT' \
--mc \
-n %s --nThreads 1"%(file,WORKDIR,N)
    

    setupHLT = " cmsDriver.py Phase2 -s L1P2GT,HLT:75e33 --processName=HLTX \
--conditions auto:phase2_realistic_T33 \
--geometry Extended2026D110 \
--era Phase2C17I13M9 \
--eventcontent FEVTDEBUGHLT \
--customise SLHCUpgradeSimulations/Configuration/aging.customise_aging_1000 \
--customise EgRegresNtuples/EGammaNtuples/customizeHLTForEgammaNtuples.customiseHLTForEGammaNtuples \
--customise HLTrigger/Configuration/customizeHLTforEGamma.customiseEGammaMenuDev \
--filein file:output_Phase2_L1T.root \
--dirin %s \
--dirout %s \
--inputCommands='keep *, drop *_hlt*_*_HLT, drop triggerTriggerFilterObjectWithRefs_l1t*_*_HLT' \
--mc \
-n -1 --nThreads 1"%(WORKDIR,WORKDIR) 

    os.system("voms-proxy-init --voms cms --valid 168:00")
    os.system(setupL1)
    os.system(setupHLT)


def run_reg():
    ntupDir = "%s/Flat"%WORKDIR
    regDir = "%s/Reg"%WORKDIR
    cmd1 = "mkdir %s"%ntupDir
    cmd2 = "mkdir %s"%regDir
    os.system("%s;%s"%(cmd1,cmd2))

    cmd3 = "cd CMSSW_14_2_0_pre2/src/EgRegresTrainerLegacy"
    cmd4 = "export PATH=$PATH:./bin/$SCRAM_ARCH"
    cmd5 = "export ROOT_INCLUDE_PATH=$ROOT_INCLUDE_PATH:$PWD/include"
    cmd6 = "python3 scripts/runSCRegTrainings.py --era \"Run3\" -i %s -o %s"%(ntupDir, regDir)
    os.system("%s;%s;%s;%s"%(cmd3, cmd4, cmd5, cmd6))

def create_train_test_split():
    # TODO: Change to realistic train-test split
    # Currently only serves to set up a working dummy setup for the RegressionTrainer
    ntupDir = "%s/Flat"%WORKDIR
    cmd1 = "mkdir %s"%ntupDir
    cmd2 = "mv %s/output.root %s/HLTAnalyzerTree_IDEAL_Flat_train.root"%(WORKDIR,ntupDir)
    cmd3 = "cp %s/HLTAnalyzerTree_IDEAL_Flat_train.root %s/HLTAnalyzerTree_IDEAL_Flat_test.root"%(ntupDir,ntupDir)
    os.system("%s;%s;%s"%(cmd1,cmd2,cmd3))

parser = argparse.ArgumentParser()
parser.add_argument("--reg_only",action="store_true",default=False)
parser.add_argument("--sample_gensim",type=str,default = "/DoubleElectron_FlatPt-1To100-gun/Phase2Spring24GS-140X_mcRun4_realistic_v4-v1/GEN-SIM")
parser.add_argument("--sample_spring24",type=str,default = "/DoubleElectron_FlatPt-1To100-gun/Phase2Spring24DIGIRECOMiniAOD-PU200_Trk1GeV_140X_mcRun4_realistic_v4-v2/GEN-SIM-DIGI-RAW-MINIAOD")
parser.add_argument("--n",type=int,default=20)
parser.add_argument("--work_dir",type=str,default="/afs/cern.ch/work/m/mmatthew/private/delete_me/cms-egamma-hlt-reg/")
parser.add_argument("--gen_sim",action="store_true",default=False)
args = parser.parse_args()



WORKDIR = args.work_dir
N = args.n
SAMPLE_GENSIM = args.sample_gensim
SAMPLE_SPRING24 = args.sample_spring24

print(args)

if not args.reg_only:
    if not args.gen_sim:
        setup_spring24_cfg()
    else: 
        setup_gensim_cfg()
    create_train_test_split()
    run_reg()
else:
    run_reg()
