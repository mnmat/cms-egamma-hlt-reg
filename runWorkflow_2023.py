import os
import sys
import subprocess
sys.dont_write_bytecode = True
from optparse import OptionParser

#https://egamma-regression.readthedocs.io/en/latest/GetHLTConfig.html
#----------------------------------------
#INPUT command-line arguments 
#----------------------------------------
parser = OptionParser()
parser.add_option("--input", "--input",         dest="input", action="store", default=None ,help="Specify input sample")
parser.add_option("--outDir", "--outDir",         dest="outDir", action="store", default=None ,help="Specify outdir")
parser.add_option("--n", "--n",                 dest="n", action="store", default=None,help="Specify number of events to process")
parser.add_option("--s1Conf",   "--s1Conf",     dest="s1Conf",action="store_true",default=False, help="Get HLT Configuration") 
parser.add_option("--s2Crab",   "--s2Crab",     dest="s2Crab",action="store_true",default=False, help="Crab submission")
parser.add_option("--s2CmsRun",   "--s2CmsRun",     dest="s2CmsRun",action="store_true",default=False, help="Run cmsRun (testing)")
parser.add_option("--s3Ntuple", "--s3Ntuple",   dest="s3Ntuple",action="store_true",default=False, help="Ntuples")
parser.add_option("--s4Flat",   "--s4Flat",   dest="s4Flat",action="store_true",default=False, help="Flat Flats")
parser.add_option("--s5Reg",    "--s5Reg",      dest="s5Reg",action="store_true",default=False, help="Perform regression")
parser.add_option("--s6Plot",   "--s6Plot",     dest="s6Plot",action="store_true",default=False, help="Plot reg output")
parser.add_option("--s7NewGT",  "--s7NewGT",    dest="s7NewGT",action="store_true",default=False, help="Create new GT")
(options, args) = parser.parse_args()



if options.input:
    sample = options.input  
    print(sample)
else:
    #sample   = "/DoublePhoton_Pt-5To300_gun/Run3Summer23BPixDRPremix-130X_mcRun3_2023_realistic_postBPix_v2-v2/GEN-SIM-RAW"
    sample   = "/DoubleElectron_Pt-1To300_gun/Run3Summer23BPixDRPremix-130X_mcRun3_2023_realistic_postBPix_v2-v2/GEN-SIM-RAW"


if options.n:
    n = options.n
else:
    n = 100

s1Conf = options.s1Conf
s2Crab = options.s2Crab
s2CmsRun = options.s2CmsRun
s3Ntuple = options.s3Ntuple
s4Flat = options.s4Flat
s5Reg = options.s5Reg
s6Plot = options.s6Plot
s7NewGT = options.s7NewGT

#eosDir = "/eos/cms/store/group/dpg_hgcal/comm_hgcal/mmatthew/BDT/eg_reg/DoublePhoton"
#eosDir = "/eos/cms/store/group/dpg_hgcal/comm_hgcal/mmatthew/BDT/test_work/126X_REAL_126X_IDEAL/n100"
#eosDir = "/eos/home-m/mmatthew/BDT/eg_reg/130X_REAL_126X_IDEAL"
#----------------------------------------
# Steo-1: Get HLT Configuration file
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/EGMHLTRun3RecommendationForPAG
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideGlobalHLT
#----------------------------------------
typeIC = {}
customIC = {}
commonIC = {}
typeIC["REAL"]  = "130X_mcRun3_2023_forPU65_v1"
typeIC["IDEAL"] = "126X_mcRun3_2023_forPU65_v1_ECALIdealIC"
gRunMenu = "/dev/CMSSW_13_1_0/GRun"
custom  = "HLTrigger/Configuration/customizeHLTforEGamma.customiseEGammaMenuDev,HLTrigger/Configuration/customizeHLTforEGamma.customiseEGammaInputContent"
commonIC["REAL"]   = "--mc --process MYHLT --prescale none --max-events %s --eras Run3 --l1-emulator FullMC --l1  L1Menu_Collisions2023_v1_2_0_xml --output minimal  --paths HLTriggerFirstPath,MC_Egamma_Open_v*,MC_Egamma_Open_Unseeded_v*,HLTriggerFinalPath"%n
commonIC["IDEAL"]   = "--mc --process MYHLT --prescale none --max-events %s --eras Run3 --l1-emulator FullMC --l1   L1Menu_Collisions2023_v1_0_0_xml --output minimal  --paths HLTriggerFirstPath,MC_Egamma_Open_v*,MC_Egamma_Open_Unseeded_v*,HLTriggerFinalPath"%n

for ele in sample.split("/"):
    if "Electron" in ele  or "Photon" in ele:
        samp = ele

 



#samp="DoublePhoton"
l1REAL = commonIC["REAL"].split("Collisions2023")[1].split("_xml")[0]
l1IDEAL = commonIC["IDEAL"].split("Collisions2023")[1].split("_xml")[0]


if options.outDir:
    eosDir = options.outDir
    print(eosDir)
else:
    eosDir = "/eos/cms/store/group/dpg_hgcal/comm_hgcal/mmatthew/BDT/test_work/%s_%s/l1_%s_%s/n%s/"%(typeIC["REAL"],typeIC["IDEAL"],l1REAL,l1IDEAL,n)
    eosDir = "/eos/cms/store/group/dpg_hgcal/comm_hgcal/mmatthew/BDT/htcondor_test"

def set_pid():
    print(samp)
    if "Photon" in samp:
        replace_text = "pid=22"
        search_text = "pid=11"
        print("Photon sample. Set EgHLTRun3Tree line 198 to pid=22")
    elif "Electron" in samp:
        replace_text = "pid=11"
        search_text = "pid=22"
        print("Electron sample. Set EgHLTRun3Tree line 198 to pid=11")
    else:
        print("Sample not recognized!")

    with open("./Analysis/HLTAnalyserPy/python/EgHLTRun3Tree.py","r") as file:
        content = file.read()
    content = content.replace(search_text, replace_text)
    with open("./Analysis/HLTAnalyserPy/python/EgHLTRun3Tree.py","w") as file:
        file.write(content)


#set_pid()

def getFile(sample):
    print("voms-proxy-init --voms cms --valid 24:00")
    das = "dasgoclient --query='file dataset=%s status=*'"%sample
    print(das)
    std_output, std_error = subprocess.Popen(das,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
    files = std_output.decode("ascii").replace('\n',' ')
    files_ = files.split(" ")
    if len(files_)==0:
        print("No files found")
        exit(0)
    return files_[0]


if s1Conf:
    if options.input:
        inFile = sample
    else:
        inFile = getFile(sample)
    inFile_ = "root://cms-xrd-global.cern.ch/%s"%inFile
    #inFile_ = sample
    #inFile_ = "file:2560000/8c0c4efa-ab57-4152-b313-4ae24aaaf04e.root"
    print(inFile_)
    for t in typeIC.keys():
        print(sample)
        cmd = "hltGetConfiguration %s --globaltag %s --input %s --customise %s %s > hlt_%s.py"%(gRunMenu, typeIC[t], inFile_, custom, commonIC[t], t)
        print(cmd)
        os.system(cmd)
        print("\ncmsRun hlt_%s.py\n"%t)

#----------------------------------------
# Step-2: Crab submission 
#----------------------------------------
crab = """
from CRABClient.UserUtilities import config
config = config()

# config.section_('General')
config.General.requestName = 'crab_%s'
config.General.workArea = 'crab_%s'
config.General.transferOutputs = True
config.General.transferLogs = True

# config.section_('JobType')
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'hlt_%s.py'
config.JobType.numCores = 4

# config.Data.inputDBS = 'phys03'
config.JobType.allowUndistributedCMSSW = True
config.JobType.maxMemoryMB = 4000

# config.JobType.numCores = 8
config.Data.inputDataset ='%s'
# config.Data.splitting = 'Automatic'
config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 10

config.Data.outLFNDirBase = '%s'
config.Data.publication = False
config.Site.storageSite = 'T2_CH_CERN'
"""
if s2Crab:
    os.system("rm -rf crab_*")
    os.system("source /cvmfs/cms.cern.ch/crab3/crab.sh")
    for t in typeIC.keys():
        outFile = open("crab_%s.py"%t, "w")
        dirName = "%s_%s"%(samp, t)
        eosDir_ = "%s/s2Crab"%eosDir
        outStr  = crab%(dirName, dirName, t, sample, eosDir_)
        print(outStr)
        print("/eos/cms/%s"%eosDir_) 
        outFile.write(outStr)
        #os.system("crab submit %s"%outFile)
        outFile.close()

if s2CmsRun:
    #os.system("rm -rf cmsRun_*")
    for t in typeIC.keys():
        os.system("mkdir cmsRun_%s"%(t))
        os.system("cp hlt_%s.py cmsRun_%s"%(t,t))
        os.chdir("cmsRun_%s"%t)
        os.system("cmsRun hlt_%s.py"%(t))
        os.chdir("./..")
        os.system("mkdir -p %s/%s"%(eosDir,samp))
        os.system("mv cmsRun_%s/output.root %s/%s/hlt_%s.root"%(t,eosDir,samp,t))
#----------------------------------------
# Step-3: Edm to ntuples 
#----------------------------------------
def getFile2(dir_):
    edm = "find %s -type f | grep output_99\.root"%dir_
    #edm = "find %s -type f | grep root"%dir_
    #edm = "find %s -type f -name *.root"%dir_
    std_output, std_error = subprocess.Popen(edm,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
    files = std_output.decode("ascii").replace('\n',' ')
    files_ = files.split(" ")
    if len(files_)==0:
        print("No files found")
        exit(0)
    return files

if s3Ntuple:
    for t in typeIC.keys():
        crabEOSDir = "%s/%s/s2Crab/crab_crab_%s_%s"%(eosDir, samp, samp,t)
        edmFiles = getFile2(crabEOSDir)
        edmFiles = "%s/%s/hlt_%s.root"%(eosDir, samp, t)
        ntupDir = "%s/%s/s3Ntuple"%(eosDir, samp)
        
        os.system("mkdir -p %s"%ntupDir)
        ntup = "%s/HLTAnalyzerTree_%s.root"%(ntupDir, t)
        print(t)
        cmd = "python3 Analysis/HLTAnalyserPy/test/makeRun3Ntup.py -r 1000 %s -o %s"%(edmFiles, ntup)
        print(cmd)
        os.system("%s"%cmd)
        #os.system("python3 Analysis/HLTAnalyserPy/test/runMultiThreaded.py --cmd \" %s \" %s -o %s --hadd"%(cmd, edmFiles, ntup))

#----------------------------------------
# Step-4: Flat ntuples 
#----------------------------------------
if s4Flat:
    for t in typeIC.keys():
        ntupDir = "%s/%s/s3Ntuple"%(eosDir,samp)
        flatDir = "%s/%s/s4Flat"%(eosDir,samp)
        os.system("mkdir -p %s"%flatDir)
        ntup = "%s/HLTAnalyzerTree_%s.root"%(ntupDir, t)
        flat = "%s/HLTAnalyzerTree_%s_Flat.root"%(flatDir, t)
        cmd = "root -l -b -q EgRegresTrainerLegacy/GetFlatNtuple/GetFlatNtuple.C\(\\\"%s\\\",\\\"%s\\\"\)"%(ntup, flat)
        print(cmd)
        os.system("%s"%cmd)

if s5Reg:
    cmd1 = "cd EgRegresTrainerLegacy"
    cmd2 = "export PATH=$PATH:./bin/$SCRAM_ARCH"
    cmd3 = "export ROOT_INCLUDE_PATH=$ROOT_INCLUDE_PATH:$PWD/include"
    ntupDir = "%s/%s/s4Flat"%(eosDir, samp)
    regDir  = "%s/%s/s5Reg"%(eosDir, samp)
    os.system("rm -r %s"%regDir)
    os.system("mkdir -p %s"%regDir)
    cmd4 = "python3 scripts/runSCRegTrainings.py --era \"Run3\" -i %s -o %s"%(ntupDir, regDir)
    os.system("%s;%s;%s;%s"%(cmd1, cmd2, cmd3, cmd4))
    print("%s && %s && %s && %s && cd .."%(cmd1, cmd2, cmd3, cmd4))

if s6Plot:
    regDir  = "%s/%s/s5Reg"%(eosDir, samp)
    cmd = "python3 EgRegresTrainerLegacy/Plot_mean.py -i %s"%regDir
    print(cmd)
    os.system(cmd)

