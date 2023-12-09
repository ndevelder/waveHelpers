#!/bin/bash

module purge
module load openmpi-gnu/4.1
module load cmake/3.25.2

source /projects/wind/ndeveld/sm-openfoam-amber/start.sh && spack-start

spack env activate /projects/wind/ndeveld/sm-openfoam-amber/environments/waves_2106_gcc_20231104
