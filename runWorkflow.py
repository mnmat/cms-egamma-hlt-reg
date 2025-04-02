import os
import sys
import subprocess
from optparse import OptionParser


SAMPLE_GENSIM = "/DoubleElectron_FlatPt-1To100-gun/Phase2Spring24GS-140X_mcRun4_realistic_v4-v1/GEN-SIM"
SAMPLE_SPRING24 = "/DoubleElectron_FlatPt-1To100-gun/Phase2Spring24DIGIRECOMiniAOD-PU200_Trk1GeV_140X_mcRun4_realistic_v4-v2/GEN-SIM-DIGI-RAW-MINIAOD"
WORKDIR = "/afs/cern.ch/work/m/mmatthew/private/test_bdt/cms-egamma-hlt-reg/"
N = 20


parser = OptionParser()
parser.add_option("--s1ConfL1", "--s1ConfL1", dest="s1ConfL1", action="store_true", default=False, help="Setup config file to rerun L1")
parser.add_option("--s2ConfHLT", "--s2ConfHLT", dest="s2ConfHLT", action="store_true", default=False, help="Setup config file to run HLT")
parser.add_option("--s3Reg", "--s3Reg", dest="s3Reg",action="store_true",default=False,help="Run regression")

(options, args) = parser.parse_args()
s1ConfL1 = options.s1ConfL1
s2ConfHLT = options.s2ConfHLT
s3Reg = options.s3Reg


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
    print("WIP")

def setup_spring24_l1_cfg():
    file = getFile(SAMPLE_SPRING24)
    setupL1 = " cmsDriver.py Phase2 -s L1,L1TrackTrigger \
--conditions auto:phase2_realistic_T33 \
--geometry ExtendedRun4D110 \
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
    
    os.system("voms-proxy-init --voms cms --valid 168:00")
    os.system(setupL1)

def setup_spring24_hlt_cfg():

    setupHLT = " cmsDriver.py Phase2 -s L1P2GT,HLT:75e33 --processName=HLTX \
--conditions auto:phase2_realistic_T33 \
--geometry ExtendedRun4D110 \
--era Phase2C17I13M9 \
--eventcontent FEVTDEBUGHLT \
--customise SLHCUpgradeSimulations/Configuration/aging.customise_aging_1000 \
--customise EgRegresNtuples/EGammaNtuples/customizeHLTForEgammaNtuples.customiseHLTForEGammaNtuples \
--customise HLTrigger/Configuration/customizeHLTforEGamma.customiseEGammaMenuDev \
--filein file:output_Phase2_L1T.root \
--procModifiers ticl_v5 \
--dirin %s \
--dirout %s \
--inputCommands='keep *, drop *_hlt*_*_HLT, drop triggerTriggerFilterObjectWithRefs_l1t*_*_HLT' \
--mc \
-n -1 --nThreads 1"%(WORKDIR,WORKDIR) 
    os.system("voms-proxy-init --voms cms --valid 168:00")
    os.system(setupHLT)

def run_reg():
    ntupDir = "%s/Flat"%WORKDIR
    regDir = "%s/Reg"%WORKDIR
    cmd1 = "mkdir %s"%ntupDir
    cmd2 = "mkdir %s"%regDir
    os.system("%s;%s"%(cmd1,cmd2))

    cmd3 = "cd CMSSW_15_1_0_pre1/src/EgRegresTrainerLegacy"
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


if s1ConfL1:  
    setup_spring24_l1_cfg()
if s2ConfHLT:
    setup_spring24_hlt_cfg()
if s3Reg:
    create_train_test_split()
    run_reg()

if not (s1ConfL1 or s2ConfHLT or s3Reg):
    setup_spring24_l1_cfg()
    setup_spring24_hlt_cfg()
    create_train_test_split()
    run_reg()
