# VirtualFD

Repository for VirtualFD application from ISW project **prepared for deployment on MEE**.
**VirtualFD project in ISW** is to calculate the blood flow in a 3D artery domain with deployed flow diverters.
The code is based on the **Palabos** Lattice-Boltzmann Computational Fluid Dynamics software.

# Requirements

Required modules:
- `plgrid/tools/gcc`
- `plgrid/tools/impi`  or `plgrid/tools/openmpi`
- `plgrid/tools/cmake`
- `plgrid/libs/hdf5/1.8.16`


# Building process

Inside hemoflowcfd directory:

    mkdir build
    cd build
    cmake ..
    make -j 8

# Running

The software can be used with `mpirun` or `mpiexe` by passing generated `executable` and the `.xml datafile.`

    mpirun -n 4 ./hemoFlow ../../NAP122_testcase/NAP122_ane/NAP122_ane.xml