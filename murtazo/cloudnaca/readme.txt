Files:
readme.txt: this file, instructions
runair.sh: bash script controlling the execution of generating GMSH .msh mesh files, convert to .xml and run airfoil
naca2gmsh_geo.py: python script generatimng GMSH .geo geometry files
geo: directory where geo files are stored
msh: directory where msh files are stored

runair INPUT:
# num_samples : number of samples you want to save
# visc        : viscosity
# speed       : speed
# T           : total time
# angle       : anglem of attack (degrees)
# n_nodes     : number of nodes on one side of airfoil
# n_levels    : number of refinement steps in meshing 0=no refinement 1=one time 2=two times etc...
