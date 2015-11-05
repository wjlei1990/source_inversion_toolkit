# source_inversion_toolkit

##### Intro
Toolsets that help launch jobs for source inversion on ORNL machine(Rhea and Titan)

##### Preparation
  1. SPECFEM
  SPECFEM should be downloaded and compiled using the right parameter settings and models. Then run the mesher to generate mesh files.


  2. CMTSOLUTIONS 
  Oiginal CMTSOLUTION files should be prepared. Other than that, derivative CMTSOLUTION should also be ready since we are going to launch the source inversion. It is recommended if you put all the CMT files, including the original CMT and derivative ones in one foler. For example, the eventname is "C200502151442A and you want to do 9 parameter source inversion, then you need get a list of CMT files ready, ["C200502151442A", "C200502151442A_Mrr", "C200502151442A_Mtt", "C200502151442A_Mpp", "C200502151442A_Mrt", "C200502151442A_Mrp", "C200502151442A_Mtp", "C200502151442A_dep", "C200502151442A_lon", "C200502151442A_lat"], corresponding to 6 moment tensor, depth, longitude and latitude perturbation CMT files.

##### Usage
  1. Copy specfem stuff into local "./specfem_stuff".
    Detailed description in "./specfem_stuff/README.md"
  
  2. launch the job.
    Detailed description in "./run_scripts/README.md"
  
#### Folder and Content
  * specfem_stuff: specfem related stuff
  * run_scripts: job launch scripts
  * DATA: the job running base. Potentially very large since it has many copies of the model file.
  * Archive: the output seismogram archive directory
