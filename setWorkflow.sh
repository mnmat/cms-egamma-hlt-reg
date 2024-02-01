#https://egamma-regression.readthedocs.io/en/latest/GetHLTConfig.html#setup
#https://twiki.cern.ch/twiki/bin/viewauth/CMS/EGMHLTRun3RecommendationForPAG
#----------------------------------------
#Setup egamma regression packages 
#----------------------------------------
export SCRAM_ARCH=slc7_amd64_gcc11
#cmsrel CMSSW_13_1_0
cd CMSSW_13_1_0/src

##Setup for creating hltConfig and produce edm files from GEN-SIM-RAW
#eval `scramv1 runtime -sh`
#git cms-addpkg HLTrigger
#scramv1 b -j 8
#git cms-merge-topic Sam-Harper:EGHLTCustomisation_1230pre6
#git cms-merge-topic Sam-Harper:L1NtupleFWLiteFixes_1230pre5
#scramv1 b -j 8

#Setup for producing ntuple from edm files
git clone -b RegNtupleRun3 ssh://git@gitlab.cern.ch:7999/rverma/HLTAnalyserPy.git Analysis/HLTAnalyserPy
scramv1 b -j 8

#Setup for making flat ntuple and doing regression
git clone -b Run3_2023_rverma_CMSSW_12_6_3 git@github.com:ravindkv/EgRegresTrainerLegacy.git 
. ../../../updateMakeFile.sh
# The RegressionTrainer might not compile for CMSSW_13_1_0. If there is an issue with including <vdt/vdtMath> then you
# need to specify the path in the MakeFile for the RegressionTrainer. Replace /cms/vdt/0.4.0-cms with one you can find in the "/cvmfs/cms.cern.ch/${SCRAM_ARCH}/cms/vdt/" folder. E.g.:
# CXXFLAGS += $(ROOTCFLAGS) -I$(INCLUDE_DIR) $(CMSSWFLAGS) -fexceptions -I$(BOOST_DIR)/include -I/cvmfs/cms.cern.ch/${SCRAM_ARCH}/cms/vdt/0.4.0-9cfb337f7ee459af6d2825bd3518d492/include/
# If you get linking errors relating to the RooLibrary simply clear the build environment and compile again
cd EgRegresTrainerLegacy
gmake RegressionTrainerExe -j 8
gmake RegressionApplierExe -j 8
cd .. && cp ../../runWorkflow.py .
