#!/usr/bin/env python3

__author__ = "Angel Ling"

import warnings
warnings.filterwarnings('ignore') 
import time
from os import path, listdir, makedirs
import matplotlib.pyplot as plt
from matplotlib.cbook import get_sample_data
from operator import itemgetter
from GMV_utils import readevent, read_data_inventory, Normalize, station_phases
from GMV_plotting import GMV_plot


# ====================
# %% Parameter Box
prog_starttime = time.time() # Execution time of this program

## Event name (Folder name)
event_name = "test"

# local event or not?
plot_local = True

# plot 3 components for seismogram?
plot_3c = True

# ENZ (plot_rotate=False) or RTZ (plot_rotate=True)?
plot_rotate = True

# Location of the data directoy
directory = "/home/laura/Dropbox/Students/Hewen/movie/data/"
# directory  = "/Users/angelling/Documents/obspyDMT/syngine_data/" 
#directory  = "/home/aling/obspyDMT/CorePhases/" # Tris

# Location of the figure directoy
fig_directory = '/home/laura/Dropbox/Students/Hewen/movie/' 
#fig_directory = '/home/aling/obspyDMT/CorePhases/' # Tris

# Path of AA logo
logo_loc = '/home/laura/Dropbox/Students/Hewen/movie/maciv_small.png'
#logo_loc = '/home/aling/AA_logo.png' # Tris

# Waveform setting
# Choose the starting and ending time in seconds after OT shown in reference seismograms (min: 0, max: 7200)
start       = 0  # min: 0    # default: 500
end         = 3600 # max: 7200 # default: 7000 
decimate_fc = 5   # Downsample data by an integer factor (Default: 2)

# Movie setting
# Choose movie interval (default: 1s)
timeframes      = range(0, 3600, 30) # plot only certain time frame in list or array, e.g.[1772,2220,2527] (Default: None)
timelabel       = "min"   # "s"/"min"/"hr" for seismograms

# Choose bandpass freq
f1 = 0.005 # min freq, default 1/200
f2 = 0.05  # max freq, default 1/50

# Select a reference station to plot by network, name, and location (e.g. CH.FUSIO.,CH.GRIMS.)
station = "FR.SALF." 

# Select phases to plot on seismograms
model  = "iasp91" # background model (e.g. iasp91/ak135)
phases = ["P","S", "4kmps"]
# local events: Pg, Sg, surface wave e.g. 3kmps
# phases = ['P','PcP','PP','PPP','S','SS','SSS','SKS','4kmps','4.4kmps'] # Phases to plot on seismograms [Teleseismic events]
# phases = ['P','Pdiff','PKP','PKIKP','PP','PPP','S','SS','SSS','SKS','SKKS','4kmps','4.4kmps'] # Phases to plot on seismograms [100deg<dist<120deg]
# phases = ["P", "S", "p", "s"] #['Pdiff','PKP','PKiKP','PKIKP','PP','PPP','SS','SSS','SKS','SKKS','4kmps','4.4kmps','SKKKS','SKSP','PPPS','SSP']  # Phases to plot on seismograms [Core events]
# phases = ['4kmps','4.4kmps']

# Plotting parameters for movies
save_option = "png" # Save format (Default: "png")
save_dpi    = 120   # Saved figure resolution (Default: 120)

# Parameters for GMV
vmin = -0.1   # colorbar min, default: -0.1
vmax =  0.1   # colorbar max, default: 0.1

# ====================
# %% Read event catalog 

# Data directories
data_directory    = directory + "/"
prodata_directory = data_directory + "processed/"
resp_directory    = data_directory + "stationxml/"
syn_iasp91_directory = data_directory + "syngine_iasp91_2s/"
syn_ak135_directory  = data_directory + "syngine_ak135f_2s/"

# Set up figure directory
fig_directory = fig_directory + "figures_" + event_name + "/"
if not path.exists(fig_directory):  # If figure directory doesn't exist, it will create one
    makedirs(fig_directory)
movie_directory = fig_directory + "movie/"
if not path.exists(movie_directory):  # If movie directory doesn't exist, it will create one
    makedirs(movie_directory)
    print("New movie directory "+movie_directory+" is created.")
else:
    print("Movie directory "+movie_directory+ " exists.")

## Read event catalog (Read QUAKEML or pkl)
# event_dic = readevent(event_name, data_directory)
event_dic = readevent(event_name, data_directory, local=plot_local)

# ==================== 
# %% Read data and inventory

## Read processed data and inventories
data_dic = read_data_inventory(prodata_directory, resp_directory, event_dic, plot_3c=plot_3c, tend=end)

# ==================== 
# %% Normalize displacement and store good data

## Filter and normalize one single event
GMV, stream_info = Normalize(data_dic, event_dic, f1, f2, start, end, decimate_fc=decimate_fc, threshold=None)

# Select a reference station for plotting seismogram
thechosenone = station_phases(GMV, station, event_dic, model, phases)


# %% Prepare for plotting 

# AA logo
with get_sample_data(logo_loc) as file_img:
    arr_img = plt.imread(file_img, format='png')
    
# Choose movie interval and turn into index
interval = int(stream_info["sample_rate"])  

# %% Main GMV plotting      
GMV_plot(GMV, event_dic, stream_info, thechosenone,
         vmin, vmax, arr_img, 
         movie_directory, timeframes=timeframes, timelabel=timelabel,
         save_option=save_option, save_dpi=save_dpi, 
         plot_local=plot_local, plot_3c=plot_3c, plot_rotate=plot_rotate)
    
    
print("--- %.3f seconds ---" % (time.time() - prog_starttime))
print("---- %.3f mins ----" % ((time.time() - prog_starttime)/60))
