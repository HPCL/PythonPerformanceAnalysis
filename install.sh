#!/bin/sh

# First, check compilers
success=0
for compiler in $CXX g++ icpc c++; do
   $compiler --version && success=1 && break
done

if [ "$success" = "0" ]; then
    echo "You need to have a working C++ compiler. If you have one and this script is failing to find it, please set your CXX environment variable and try running ./install.sh again.";
    exit 1;
fi
    
PROJECT_DIR="${PROJECT_DIR:-${PWD}/tools}"
echo "Installing TAU Commander and Hatchet in $PROJECT_DIR"

if [ ! -d $PROJECT_DIR ]; then 
    mkdir $PROJECT_DIR
fi

cd $PROJECT_DIR

git clone --branch sane-dependencies https://github.com/ParaToolsInc/taucmdr.git taucmdr
cd taucmdr
make install INSTALLDIR=$PROJECT_DIR/taucmdr/installed && \
$PROJECT_DIR/taucmdr/installed/system/configure

if [ "$?" != 0 ]; then
    echo "ERROR: Could not configure system-wide TAU; this is probably fine, it just means that some TAU Commander commands will take longer. Continuing with installation..."" 
fi

MYSHELL=`basename $SHELL`
$PROJECT_DIR/taucmdr/installed/conda/bin/conda init $MYSHELL

cd $PROJECT_DIR
git clone https://github.com/LLNL/hatchet.git
cd hatchet
./install.sh

cd $PROJECT_DIR
echo "Testing your installation"
exec $MYSHELL -c "$PROJECT_DIR/taucmdr/installed/conda/bin/conda install -y matplotlib && \
$PROJECT_DIR/taucmdr/installed/conda/bin/python -c 'import hatchet; import taucmdr' && echo \"SUCCESS! Add $PROJECT_DIR/taucmdr/installed/bin to your PATH and take a look at GettingStarted.ipynb\" || echo \"Installation failed: could not import hatchet or taucmdr\""

echo "You may wish to add $PROJECT_DIR/taucmdr/installed/bin to your PATH, e.g., export PATH=$PROJECT_DIR/taucmdr/installed/bin:$PATH"
