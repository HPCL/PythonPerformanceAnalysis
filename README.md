# Python Performance Analysis
A set of python scripts and programs that can be used to analyze performance data from TAU experiments.

## Detailed Description
This repository contains a set of python fucntions that can be used to organize, analyze, and plot results from measuring performance data using TAU.

Data for analysis should be stored in TAU profiles or our pickled format.

The scripts rely heavily on the functionality provided by pandas dataframes (https://pandas.pydata.org/) to store and manage the data. Pandas also provides considerable statistical analysis functionality and some plotting functions to further the analysis. Additionally, we use pyplot to create figures not available in pandas.

We recommned using the functions in conjuntion with jupyter notebooks (which is how our examples are written) as it provides easy visualization, documentation, and sharing of the work.

## Getting Started

Make sure that you have a working C++ compiler. To use a specific compiler, set your CXX environment variable, e.g., `export CXX=g++-8`. 

The quickest way to install prerequisites is to run the provided `install.sh` script, e.g., `./install.sh 2>&1 | tee install.log`. If that fails, you can adjust the process by following the following steps.

1. Create a project directory, e.g, `$HOME/performance`, and continue the following steps inside that project directory, `$PROJECT_DIR`.

2. Install [TAU Commander](http://taucommander.paratools.com/). This also installs Miniconda3 and several python packages we will need later.
```
cd $PROJECT_DIR
git clone --branch unstable https://github.com/ParaToolsInc/taucmdr.git taucmdr-unstable
cd taucmdr-unstable
make install 
```
You should add the TAU Commander binary directory to your path:
```
export PATH=$PROJECT_DIR/taucmdr/bin:$PATH
```
3. Configure your Conda environment for the newly installed Miniconda3 (under your taucmdr directory): 

```
MYSHELL=`basename $SHELL`
$PROJECT_DIR/taucmdr/installed/conda/bin/conda init $MYSHELL
exec $MYSHELL
$PROJECT_DIR/taucmdr/installed/conda/bin/conda install matplotlib
```

4. Install Hatchet:
```
cd $PROJECT_DIR
git clone https://github.com/LLNL/hatchet.git
cd hatchet
./install.sh
```

5. Test your installation:
```
python -c 'import taucmdr' 
python -c 'import hatchet'
```

