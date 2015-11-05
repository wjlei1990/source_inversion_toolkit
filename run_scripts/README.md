### Job Submission Tools

### Usage:
1. Set up runbase directory using X01_setup_dir.bash  
  The default runbase is "../DATA"

2. Copy mesh files into runbase  
  See the scripts copy_mesh.pbs. Please use command: "qsub -q dtn copy_mesh.pbs". This should be done only once unless you changed the any settings related to the model.

3. Go to the job submission stage  
  1. Prepare directories for the runbase.  
    First, copy Par_file, STATIONS, xspecfem3D, values_from_mesher.h, addressing.txt to the runbase subdirectory. Second, create job pbs files. See "job_running_template_event_bundle/X01_prepare_dir.bash"

  2.  Job submission  
    After step.1, there should be a bunch of *job_solver_bundle.pbs.*" generated. Submit them.
  
  3. After all jobs are finished, archive the data.
    Use "qsub -q dtn X03_archive_data.pbs"
