# Raspberry Pi Cluster Setup

A simple way to help automate the setup of Raspberry Pi computers into a small computing cluster using MPI. This is not meant to be particularly efficient or even the right way to accomplish the setup of a Raspberry Pi cluster. The following is meant to be a no-frills and simple method to set up an MPI cluster relatively quickly.

## Hardware
- Raspberry Pi computers, flashed with Raspbian OS
  - All necessary cables for power
  - SD card for each Pi. Ideally all should be the same size
  - OPTIONAL: mounting hardware for Pi's
  - OPTIONAL: monitor, keyboard, mouse
    - Monitor/Keyboard/Mouse not required if relying on SSH 
- One ethernet cable per Pi
  - An extra + necessary adapter if using SSH
- Ethernet switch with enough ports for Pi's
- Power supply, make sure this is strong enough to power your Pi's

## Software
- nmap
- MPICH2
- mpi4py

## Initial Setup

### Setup Master Node
Choose a Pi to be your master node and flash a [fresh copy of the Raspbian OS](https://www.raspberrypi.org/downloads/raspbian/) to it. Create a blank file called "ssh" without any extension and place it in the root of the SD card. This will enable ssh access to the Pi.

Boot the Pi, make sure it is connected to the internet via an ethernet cable or wifi, and run the following:

```bash
sudo apt-get update
```

```bash
sudo apt-get upgrade
```

This may take some time.

Run the following command in the terminal to open the configuration menu:

```bash
sudo raspi-config
```

In order:
1. Change the user password (REMEMBER THIS)
2. Under 2, Network Options, change the Hostname to node0001
3. Under 3, Boot Options, B1, Desktop/CLI, change to B2, Console Autologin
4. Under 4, Localization, change to your region/time zone
5. Under 7, Advanced Options, A1 Expand Filesystem
6. Click finish, if it asks to reboot, click yes
  * If it does not ask you to reboot, type `sudo reboot`

This will have set up the desired parameters for the operating system.

Next, it is necessary to install MPI to the system. At the terminal and in the root directory, the following will accomplish this:

1. `mkdir mpich2 && cd ~/mpich2`
2. `wget http://www.mpich.org/static/downloads/3.1/mpich-3.1.tar.gz`
3. `tar xfz mpich-3.1.tar.gz`
4. `sudo mkdir /home/rpimpi/`
5. `sudo mkdir /home/rpimpi/mpi-install`
6. `mkdir /home/pi/mpi-build`
7. `cd /home/pi/mpi-build`
8. `sudo apt-get install gfortran`
9. `sudo /home/pi/mpich2/mpich-3.1/configure -prefix=/home/rpimpi/mpi-install`
* This and the next steps will take some time
10. `sudo make`
11. `sudo make install`

MPICH2 is now installed, but it must be put on the PATH so that it can be used. From the root directory:

1. `nano .bashrc`
2. At the end of this file, add the following: `PATH=$PATH:/home/rpimpi/mpi-install/bin`
3. `sudo reboot`

To test the installation, type the following:

```bash
mpiexec -n 1 hostname
```

This should output `node0001`

Programs can now be written for the system in Fortran and C/C++, however, we want this to work with Python. Type the following:

```bash
pip install -r requirements.txt
```

This will install `mpi4py`, an MPI implementation for Python, and `nmap`, which will be used to find IP addresses for each computer on the local network.

Once this completes, type `sudo reboot`

Run the sample helloworld program, `hello_mpi.py`:

```bash
mpiexec -n 4 python hello_mpi.py
```

This should indicate that 4 processes have run on the processor by the name of node0001. 

### Flash SD to other Pi's
Copy the SD card from the Master node which was set up priorly, to the SD cards for each other Pi which is to be used. Boot each of these Pi's and change the hostnames to a sequential pattern: `node0002`, `node0003`, ..., `node000N`, where N is the number of Pi's that are to be in the cluster. It might be worthwhile to run `mpiexec -n 1 hostname` on each Pi to ensure that MPI is working.

On each Raspberry Pi, run the command:

```bash
ssh-keygen
```

Simply hit <Enter> without typing anything else until an ssh key pictogram appears, indicating that the RSA key was generated successfully. The public and private keys will be in the directory /home/pi/.ssh on the Pi. 


### Connect Hardware
Connect the Pi's using the ethernet switch, cables, and power supply. 

### Establish Cluster

Run the program `cluster_setup.py` on the master node. This will collect the IP addresses of the nodes in the cluster, collect RSA public keys, create an authorization file, and distribute the authorized hosts back to each Pi in the cluster.

You will be asked to type the passwords to the Pi's and 'yes' repeatedly through this process. Continue to enter the required query until the program completes. A file will be created in /home/pi/ called "machinefile". This file contains the IP addresses and hostnames of each Pi in the cluster, including the master node. 

Test the program's success with:

```bash
mpiexec -f machinefile -n <NUMBER OF NODES> hostname
```

This should print the hostname of each node in the cluster, indicating that MPI has been successfully installed and cluster has been established. The cluster is now ready to run any MPI program desired. 





