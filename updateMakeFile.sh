#!bin/bash

# File used to replace the flags in the EgRegresTrainer that can be cloned here: git clone -b Run3_2023_rverma_CMSSW_12_6_3 git@github.com:ravindkv/EgRegresTrainerLegacy.git 
# It updates the CXX flags to the correct path for CMSSW_13_1_0 and sets the directory of the boost library to an updated version compatible.

# TODO: This File should be deleted once a more robust update for the EgRegresTrainer Makefile can be found.

dir=$(pwd)
file="$dir/EgRegresTrainerLegacy/MakeFile"
file="/afs/cern.ch/user/m/mmatthew/TestReg/cms-egamma-hlt-reg/CMSSW_13_1_0/src/EgRegresTrainerLegacy/MakeFile"
file="/afs/cern.ch/user/m/mmatthew/TestReg/CMSSW_13_1_0/src/EgRegresTrainerLegacy/Makefile"
old_cxx_flags='CXXFLAGS     += $(ROOTCFLAGS) -I$(INCLUDE_DIR) $(CMSSWFLAGS)  -fexceptions  -I$(BOOST_DIR)/include -I/cvmfs/cms.cern.ch/${SCRAM_ARCH}/cms/vdt/0.4.0-cms/include/'
new_cxx_flags='CXXFLAGS     += $(ROOTCFLAGS) -I$(INCLUDE_DIR) $(CMSSWFLAGS) -fexceptions -I$(BOOST_DIR)/include -I/cvmfs/cms.cern.ch/${SCRAM_ARCH}/cms/vdt/0.4.0-9cfb337f7ee459af6d2825bd3518d492/include/'

old_boost='BOOST_DIR     = $(shell ls $$CMSSW_DATA_PATH/../external/boost/* -d  | head -n 1)'
new_boost='BOOST_DIR     = $(shell find $$CMSSW_DATA_PATH/../external/boost/* -maxdepth 1 -type d -name "1.80*" -printf "%f\\n" | head -n 1)'

escaped_old_boost=$(echo "$old_boost" | sed 's/\*/\\*/g')
escaped_new_boost=$(echo "$new_boost" | sed 's/\*/\\*/g')

#sed -i "s|$new_cxx_flags|$old_cxx_flags|" $file

if test -e "$file"; then
    echo "$file exists. Continue."
    if grep -q "$new_cxx_flags" "$file"; then
        echo "CXX Flags already updated."
    else
        echo "sed -i \"s|$old_cxx_flags|$new_cxx_flags|\" $file"
        sed -i "s|$old_cxx_flags|$new_cxx_flags|" $file        
        echo "Replaced CMSSW_13_1_0 CXX flags."
    fi
    
    if grep -q "$escaped_new_boost" "$file"; then
        echo "BOOST_DIR already updated."
    else
        echo "sed -i 's@$escaped_old_boost@$escaped_new_boost@' $file"
        sed -i "s@$escaped_old_boost@$escaped_new_boost@" $file
        echo "Replaced CMSSW_13_1_0 incompatible BOOST_DIR"
    fi

else
    echo "$file does not exist. Download EgRegresTrainerLecacy using 'git clone -b Run3_2023_rverma_CMSSW_12_6_3 git@github.com:ravindkv/EgRegresTrainerLegacy.git'"
fi
