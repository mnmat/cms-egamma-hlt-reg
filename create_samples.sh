#!/bin/bash


#inputFile="/store/mc/Run3Summer23BPixDRPremix/DoubleElectron_Pt-1To300_gun/GEN-SIM-RAW/130X_mcRun3_2023_realistic_postBPix_v2-v2/2550000/40573acb-3967-4821-aaaf-f7d7b1949f26.root"
#n="1"
#idx="1"
#outDir="outDir"
#tmpDir="tmpDir"
sample="DoubleElectron_Pt-1To300_gun"

inputFile="$1"
n="$2"
idx="$3"
outDir="/eos/cms/store/group/dpg_hgcal/comm_hgcal/mmatthew/BDT/htcondor_test"
tmpDir="testDir"
REDIRECTOR="root://eosuser.cern.ch//"

tar -xzvf EgRegresTrainerLegacy.tar.gz
tar -xzvf Analysis.tar.gz

echo $inputFile
echo $n
echo $tmpDir
echo $outDir

hostnamectl
#voms-proxy-init --rfc --voms cms -valid 192:00

cmsRun --help

python3 runWorkflow_2023.py --input $inputFile --outDir $tmpDir  --n $n --s1Conf 2>&1
python3 runWorkflow_2023.py --input $inputFile --outDir $tmpDir  --n $n --s2CmsRun 2>&1
python3 runWorkflow_2023.py --input $inputFile --outDir $tmpDir  --n $n --s3Ntuple
python3 runWorkflow_2023.py --input $inputFile --outDir $tmpDir  --n $n --s4Flat

tmpDir="${tmpDir}/${sample}/s4Flat"

echo "$tmpDir"

for file in "${tmpDir}"/*; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        extension="${filename##*.}"
        new_filename="${idx}_${filename}"
        echo "${REDIRECTOR}/${outDir}/${new_filename}$"
        xrdcp "$file" "${REDIRECTOR}$outDir/$new_filename"
    fi
done
