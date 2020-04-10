# -*- coding: utf-8 -*-
# @Author: Charlie Gallentine
# @Date:   2020-04-10 17:45:33
# @Last Modified by:   Charlie Gallentine
# @Last Modified time: 2020-04-10 17:48:24

from mpi4py import MPI 
import sys

rank = MPI.COMM_WORLD.Get_rank()
size = MPI.COMM_WORLD.Get_size()

processor = MPI.Get_processor_name()

sys.stdout.write("Hello from %s process[%d/%d]\n" % (processor,rank,size))
