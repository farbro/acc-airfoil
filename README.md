# acc-airfoil

In deploy, worker-init 
- installs docker
- creates fenics container
- sends zipped murtazo folder to container (assuming that its in the current dir)
- unpacks and compiles airfoil executable.

- maybe instead of compiling airfoil can run shuyi's shell file to convers mesh files and compile airfoil
