#!/bin/bash
#input:
# num_samples : number of samples you want to save
# visc        : viscosity
# speed       : speed
# T           : total time
# angle       : anglem of attack (degrees)
# n_nodes     : number of nodes on one side of airfoil
# n_levels    : number of refinement steps in meshing 0=no refinement 1=one time 2=two times etc...


# Path to GMSH binary
GMSHBIN="/usr/bin/gmsh"
# Path to dir where geo files will be stored
GEODIR="geo"
# Path to dir where msh files will be stored
MSHDIR="msh"
# NACA four digit airfoil (typically NACA0012)
NACA1=0
NACA2=0
NACA3=1
NACA4=2

num_samples="$1"
visc="$2"
speed="$3"
T="$4"
angle="$5"
n_nodes="$6"
n_levels="$7"

geofile=a${angle}n${n_nodes}.geo
./naca2gmsh_geo.py $NACA1 $NACA2 $NACA3 $NACA4 $angle $n_nodes > $GEODIR/$geofile
mshfile="$(echo $geofile|sed -e 's/geo/msh/')";
$GMSHBIN -v 0 -nopopup -2 -o $MSHDIR/r0$mshfile $GEODIR/$geofile;
newname=r0$mshfile

if [ "$n_levels" -gt "0" ]; then
  for i in `seq 1 $n_levels`;
  do
	  pm=r$(($i-1));
	  pmn=r$(($i));
	  oldname=${pm}${mshfile};
	  newname="$(echo ${oldname}|sed -e s/"$pm"/"$pmn"/)";
	  cp $MSHDIR/${oldname} $MSHDIR/$newname;
	  $GMSHBIN -refine -v 0 $MSHDIR/$newname;
  done
fi
xmlfile="$(echo $newname|sed -e 's/msh/xml/')"
dolfin-convert ./$MSHDIR/$newname ./$MSHDIR/$xmlfile
cd ../navier_stokes_solver
sudo docker exec -t -i fenics_cont ./murtazo/navier_stokes_solver/airfoil  $num_samples $visc $speed $T ../cloudnaca/$MSHDIR/$xmlfile

