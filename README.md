# cms-egamma-hlt-reg

## Purpose 
This repo is intended to test the workflow for the egamma supercluster regression for Phase 2. 
The samples used are the ones generated in Spring24
- [Electron](https://cmsweb.cern.ch/das/request?input=dataset%3D%2FDoubleElectron_FlatPt-1To100-gun%2FPhase2Spring24DIGIRECOMiniAOD-PU200_Trk1GeV_140X_mcRun4_realistic_v4-v2%2FGEN-SIM-DIGI-RAW-MINIAOD&instance=prod/global)
- [Photon](https://cmsweb.cern.ch/das/request?input=dataset%3D%2FDoublePhoton_FlatPt-1To100-gun%2FPhase2Spring24DIGIRECOMiniAOD-PU200_Trk1GeV_140X_mcRun4_realistic_v4-v2%2FGEN-SIM-DIGI-RAW-MINIAOD&instance=prod/global)

The cmsDriver commands were taken from the [simplified menu](https://cmshltupgrade.docs.cern.ch/RunningInstructions/)

## Usage

- run `. setup.sh`. This sets up CMSSW\_15\_1\_0\_pre1, the modified [EgRegresTrainerLegacy](https://github.com/mnmat/EgRegresTrainerLegacy), and the Ntuplizer
- run `python3 runWorkflow.py`. This creates and executes the configuration files from the cmsDriver commands from the simplified menu, splits the output ntuples into training and test sets (WIP), and runs the regression.

If everything works, the workflow is set up correctly and one can move on to sample production for the retraining of the BDT for Phase2 HLT.

## Debuging the BDT

There seems to be an issue with the BDT regarding the splitting of the data at the nodes when the following is triggered:

```
 if (_nlefts[bestvar] != nleft)
```

To reproduce this error one can run the script `debugRegression.sh`. The samples stored in the public folder were created using the workflow described above for the electron samples.


