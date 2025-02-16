#!/usr/bin/env python
import os
import placentagen as pg
import numpy as np

#from get_stats import *
from os.path import expanduser

home = expanduser("~")

##########################################
# Parameters that define placental shape #
##########################################

#setting the 3 parameters below to 0 as we will not be using seeds that fill an ellipsoid
#volume of ellipsoid
volume=0 #mm^3
#thickness of ellipsoid (z-axis dimension)
thickness=0 #mm
#ellipticity  - ratio of y to x axis dimensions
ellipticity=0 #no units


###############################################################
# Parameters that define branching within the placenta volume #
###############################################################
#Number of seed points targeted for growing tree
n_seed=32000
#Maximum angle between two branches
angle_max_ft =  90 * np.pi /180 #convert from degrees to radians by multipling by np.pi / 180
#Minimum angle between two branches
angle_min_ft = 0 * np.pi /180
#Fraction that the branch grows toward data group centre of mass at each iteration
fraction_ft =   0.4
#Minimum length of a branch
min_length_ft =  0.0 #mm
#minimum number of data points that can be in any group after a data splitting proceedure
point_limit_ft =  1


###################
# Export controls #
###################
#If you want to see how each step in the process builds on the last set this to be true
export_intermediates = True
#If you want final results set this to be true
export_results = True
#Define a directory to export (do not write over expected-results unless you have made a (peer-reviewed) change to the process)

export_directory = 'output-grow-existing'
chor_node_in_file = 'example-data-files/chor_nodes.exnode'
chor_elem_in_file = 'example-data-files/chor_elems.exelem'

seed_points_in_file = 'example-data-files/placenta_seeds_transformed.exdata'

seed_points_option = 'read_in' #or 'generate'


if(export_intermediates or export_results):
    if not os.path.exists(export_directory):
        os.makedirs(export_directory)

#Import chorion and stem geometry
chorion_and_stem = {}

chorion_and_stem['nodes'] = pg.import_exnode_tree(chor_node_in_file)['nodes'][:, 0:4]
chorion_and_stem['elems'] = pg.import_exelem_tree(chor_elem_in_file)['elems']


#populate element connectivity
elem_connectivity = pg.element_connectivity_1D(chorion_and_stem['nodes'],chorion_and_stem['elems'])
chorion_and_stem['elem_up'] = elem_connectivity['elem_up']
chorion_and_stem['elem_down'] = elem_connectivity['elem_down']

if (seed_points_option== 'generate'):
    # Define data points that represent the density of villous tissue, equispaced within an ellipsoidal geometry
    datapoints_villi=pg.equispaced_data_in_ellipsoid(n_seed,volume,thickness,ellipticity)
else:
    #read in seed points filling the volume of the placenta based on images
    datapoints_villi = pg.import_exnode_tree(seed_points_in_file)['nodes'][:, 1:4]

if(export_intermediates):
    export_file = export_directory + '/villous_data'
    pg.export_ex_coords(datapoints_villi,'villous',export_file,'exdata')

random_seed = 2 #random seed number for reproducability
#Now grow a tree to these data points, optimised for larger trees
full_geom=pg.grow_large_tree(angle_max_ft, angle_min_ft, fraction_ft, min_length_ft, point_limit_ft, volume, thickness, ellipticity, datapoints_villi, chorion_and_stem,random_seed)

# Export the final results
if(export_results or export_intermediates):
    export_file = export_directory + '/full_tree'
    pg.export_ex_coords(full_geom['nodes'],'placenta', export_file,'exnode')
    pg.export_exelem_1d(full_geom['elems'],'placenta', export_file)
    pg.export_ip_coords(full_geom['nodes'][:, 1:4], 'placenta', export_file)
    pg.export_ipelem_1d(full_geom['elems'], 'placenta', export_file)
    export_file = export_directory + '/terminals'
    pg.export_ex_coords(full_geom['term_loc'],'villous',export_file,'exdata')

#`get_tree_stats(export_directory)
