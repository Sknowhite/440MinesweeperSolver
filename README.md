# 440 Minesweeper Solver
Minesweeper client and solver using CSP with Backtracking, Forward Checking and Generalized Arc Consistency

TO RUN:

python3 ms.py

#### If that doesn't work:
DOWNLOAD AND INSTALL: https://sourceforge.net/projects/xming/

using Linux terminal: 

sudo nano ~/.bashrc
  add: export DISPLAY=:0;
  to the bottom of the file
  
source ~/.bashrc

cd /pathToRepo/msCsp

python3 ms.py
  
NOTES:
    Has different propagators to use and test with such as plain Backtracking, Forward checking 
  and GAC (generalized arc consistency algo).
  
  To change propagator go to line 315 in and change the prop_ argument. Options: prop_BT, prop_FC, prop_GAC
  
  
