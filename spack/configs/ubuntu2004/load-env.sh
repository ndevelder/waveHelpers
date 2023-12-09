#!/bin/bash

module purge
module load sparc-git/2.19.1

source /projects/wind/ndeveld/sm-openfoam/start.sh && spack-start

spack env activate /projects/wind/ndeveld/sm-openfoam/environments/openfoam_2106_gcc8_20231208
