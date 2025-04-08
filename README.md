# brown_sdc_2025_scripts

Repository for scripts to run the test casese and plot the results for Brown 2025 paper: Fast-wave slow-wave spectral deferred correction methods applied to the
compressible Euler equations

The test case scripts in this repository use the `Gusto` model, which can be accessed here: [https://github.com/firedrakeproject/gusto]. 

The plotting scripts in this repository use the `tomplot` plotting
library, which can be accessed here: [https://github.com/tommbendall/tomplot]

How to get results & plots:

----------------------------------------------------------------------------------

1. Make sure you have a firedrake with gusto installed, and tomplot installed.

----------------------------------------------------------------------------------
2. Run the following commands from the `test_cases` directory:

  For Figure 1 simply run `python williamson1_convergence.py`, this should generate all the data for the self convergence test
  
  For Figure 2 run:
  1. `python gravity_wave.py` to generate the example solution in the plot
  2. run `mpiexec -n N python 1 gw_convergence_true.py`, `mpiexec -n N python 3 gw_convergence_true.py` and `mpiexec -n N python 5 gw_convergence_true.py` to generate the order 1, 3 and 5 reference solutions. Note this takes some time. N = 20 would be a reasonable choice here
  3. run `mpiexec -n N python gw_convergence_o1.py`, `mpiexec -n N python gw_convergence_o3.py` and `mpiexec -n N python gw_convergence_o5.py` to generate the solutions for the convergence test. N = 3 would be a reasonable choice here
  
  For Figure 3 run: 
  1. `mpiexec -n N python moist_bf.py` to generate the solution with the LU and FE Qdelta matrices
  2. `mpiexec -n N python moist_bf_parallel.py` to generate the solution with the MIN-SR-FLEX and MIN-SR-NS Qdelta matrices
  N = 5 would be a reasonable choice here
 
  For Figure 4 run `mpiexec -n N python dry_baroclinic_channel.py`. N = 30 to N = 60 would be reasonable choices here

----------------------------------------------------------------------------------

3. Run all plotting scripts from the `plotting_scripts` directory. They are named based on which figure in the paper they produce.

----------------------------------------------------------------------------------
