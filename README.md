# cms-egamma-hlt-reg

This repo provides tools to setup and run the phase2 egamma regression for Spring24 samples.
Before starting, make sure to set your preferred working directory in:
- `run_workflow.py`
- `setup_htcondor.py``
- `merge.py`
 

### Setup Environment

```
.setWorkflow.sh
```

### Test workflow

Running the following will go through the entire workflow, rerunning the HLT and running the regression on 20 samples. Make sure this works before moving on to larger sample productions

```
python3 runWorkflow.py
```

### Large sample production using HTCondor

#### Setup HTCondor

The following will setup the scripts necessary to rerun the hlt menu on htcondor. It will take the files produced in the previous step and reformat them to input larger datasets. It does this by adding input arguments to the config files, i.e. 'evts'(number of events to process by single node),'skip' (from which event to start processing for single node),'ptype' (type of gen particle that created the SC), and 'file'. 

```
cd htcondor_sample_production/
python3 setup_htcondor.py
```

The input variables mentioned above are provided with the help of a queue. To create the queue, use:

```
python3 fillQueue_Spring24.py
```
Move the queue into the folder containing the htcondor scripts, "Spring24" when following this tutorial.

```
mv files.txt Spring24
```

#### Run HTCondor

To run the htcondor, you must make the grid proxy available to the computing nodes. Otherwise you cannot access files via xrootd. Do the following before running htcondor scripts.

```
export X509_USER_PROXY=~/.gridProxy
voms-proxy-init --rfc --voms cms -valid 192:00
```

Finally, you can send the jobs to htcondor via:

```
cd Spring24
condor_submit condor.sub
```

Make sure that the settings in the condor.sub file are appropriate with respect to duration, how many jobs you want to start simultaneously etc. It is recommended to start with a low event and file count, i.e. 1 file and a couple of events only, and test htcondor using the `espresso` setting for duration to limit computing resources.

#### Prepare output files for BDT

To prepare the output data as input to the BDT, merge the individual files into a training and test sample, using:

```
python3 merge.py
```

#### Apply regression only

The BDT can be trained on the samples using

```
python3 run_Workflow --reg_only
``` 
