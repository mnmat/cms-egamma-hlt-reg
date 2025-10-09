import glob
import os
import argparse


parser = argparse.ArgumentParser()

parser.add_argument("--work_dir", type=str, default="/afs/cern.ch/work/m/mmatthew/private/test_workflow/cms-egamma-hlt-reg/Data") 
args = parser.parse_args()

path = args.work_dir
outdir = os.path.join(path,"Flat")

if not os.path.exists(outdir):
    os.mkdir(outdir)

ls_ideal = glob.glob(os.path.join(path,"output_*.root"))

ls_ideal = sorted(ls_ideal)

ls_ideal_filtered = []

for i in range(len(ls_ideal)):
    if (os.stat(ls_ideal[i]).st_size>500):
        ls_ideal_filtered.append(ls_ideal[i])

split = int(len(ls_ideal_filtered)*0.8)
ls_train = ls_ideal_filtered[:split]
ls_test = ls_ideal_filtered[split:]

print(len(ls_train))
print(len(ls_test))

def merge_files(ls,name,run=False):
    cmd = "hadd %s "%name
    for i in range(len(ls)):
        cmd += "%s "%ls[i]

    if run: os.system(cmd)
    else: print(cmd)

merge_files(ls_train,os.path.join(outdir,"HLTAnalyzerTree_IDEAL_Flat_train.root"),run=True)
merge_files(ls_test,os.path.join(outdir,"HLTAnalyzerTree_IDEAL_Flat_test.root"),run=True)


#merge_files(ls_test,os.path.join(outdir,"HLTAnalyzerTree_IDEAL_Flat_test.root"),run=True)
