import os
import subprocess

dataset = "/DoubleElectron_Pt-1To300_gun/Run3Summer23BPixDRPremix-130X_mcRun3_2023_realistic_postBPix_v2-v2/GEN-SIM-RAW"
cmd = ["dasgoclient", "-query='file dataset=%s'"%dataset]
cmd = "dasgoclient -query='file dataset=%s'"%dataset
tmp_file = "tmp_output.txt"
os.system(f"{cmd} > {tmp_file}")
out_file = "fileQueue.txt"

N = 4000000
nevts = 3000

with open(tmp_file, "r") as infile, open(out_file, "w") as outfile:
    for i,line in enumerate(infile):
        line = line.replace("\n","")
        row = "%s %s %s"%(line,i,nevts)
        row = row + '\n'
        outfile.write(row)
        print(row)
        if (i+1)*nevts>N:
            break
#txt=subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,text="True")

