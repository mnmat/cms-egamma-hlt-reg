#https://egamma-regression.readthedocs.io/en/latest/GetHLTConfig.html#setup
#https://twiki.cern.ch/twiki/bin/viewauth/CMS/EGMHLTRun3RecommendationForPAG
#----------------------------------------
#Setup egamma regression packages 
#----------------------------------------
export SCRAM_ARCH=el9_amd64_gcc12
cmsrel CMSSW_14_2_0_pre2 
cd CMSSW_14_2_0_pre2/src

cmsenv
git cms-init

git cms-merge-topic Sam-Harper:EGHLTCustomisation_1230pre6
mkdir EgRegresNtuples
cd EgRegresNtuples
git clone git@github.com:mnmat/EGammaNtuples.git
scram b -j 8
cd ..

git clone -b Run3_2023_mmatthew_CMSSW_13_1_0 git@github.com:mnmat/EgRegresTrainerLegacy.git 
cd EgRegresTrainerLegacy
gmake RegressionTrainerExe -j 8
gmake RegressionApplierExe -j 8
gmake RegressionApplier_newExe - j 8
