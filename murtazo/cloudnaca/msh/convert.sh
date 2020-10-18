#!/bin/bash

filelist=`ls /home/fenics/shared/murtazo/cloudnaca/msh/`
for file in $filelist
	do
	name=$(ls $file | cut -d. -f1)
	dolfin-convert $file ./xml/${name}.xml
	done
echo "done!"
