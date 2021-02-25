# Python Performance Analysis - Roofline Visualization

The Roofline performance visualization method provides a technique to visualize
the potential performance of a system and how a particular kernel performs relative
to that potential.

There are two parts to a roofline: the system peak data and the kernel performance.
For the two parts there will need to be two sets of data to plot.

## Data for Rooflines
Currently data for the roof lines must come from a tool such as the ERT, Intel's VTUNE,
or Nvidia's nsys. Currently, this must be manually added to the Jupyter notebook.

Required Data:
* 

## Data for Kernels
To plot a point you can also add data manually, but we hope to soon add automatic 
methods of pulling the data from the TAU and Caliper scripts.

Required data:
* GFlops/s
* Operational Intensity


## Roofline options
Generally speaking the roofline compare GFlops/s to Operational intensity. OI is a 
measure of how many "useful operations", generally Flops, are completed for each
byte of data moved from a particluar level of memory. GFlops/s are obviously a measure
of the rate of computation. These two can be modified in several ways depending on
the needs of your application.

### Operational Intensity
Operational Intensity can be modified for other operations than floating point ops,
but scietific computing.



