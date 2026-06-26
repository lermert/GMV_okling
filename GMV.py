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
from GMV_complt_func import GMV_plot_MACIV # (H)


# ====================
# %% Parameter Box
prog_starttime = time.time() # Execution time of this program

## Event name (Folder name)
event_name = "drake_earthquake"

# local event or not?
plot_local = False # init True (H)

# plot 3 components for seismogram?
plot_3c = True # init True (H)

# ENZ (plot_rotate=False) or RTZ (plot_rotate=True)?
plot_rotate = True

# Location of the data directoy
directory = "/Users/sommi/Desktop/stage_ISTerre/animations" # (H)
# directory  = "/Users/angelling/Documents/obspyDMT/syngine_data/" 
#directory  = "/home/aling/obspyDMT/CorePhases/" # Tris

# Location of the figure directoy
fig_directory = "/Users/sommi/Desktop/stage_ISTerre/animations/test_animations" # (H)
#fig_directory = '/home/aling/obspyDMT/CorePhases/' # Tris

# Path of AA logo
logo_loc = '/Users/sommi/Desktop/stage_ISTerre/animations/LogoMaciv2-LargeFull_Color.png' # (H)
#logo_loc = '/home/aling/AA_logo.png' # Tris

# Path to the map (has to be a png and the projection has to be Plate carree) (H)
map_loc = '/Users/sommi/Desktop/stage_ISTerre/animations/GMV_okling/fond_de_carte_clair_plate_carree.png'
map_region = [1.8, 4.2, 44.8, 46.5]

map_files = "/Users/sommi/Desktop/stage_ISTerre/animations/GMV_okling/map_files" # obsolete (H)


# Waveform setting
# Choose the starting and ending time in seconds after OT shown in reference seismograms (min: 0, max: 7200)
start       = 0  # min: 0    # default: 500
end         = 7200 # max: 7200 # default: 7000 
decimate_fc = 0   # Downsample data by an integer factor (Default: 2)   (0 to avoid data downsampling (H))

# Movie setting
# Choose movie interval (default: 1s)
# plot only certain time frame in list or array, e.g.[1772,2220,2527] (Default: None)

timeframes      = range(0, 7200, 30) # init range(0, 3600, 30) (H)
timelabel       = "min"   # "s"/"min"/"hr" for seismograms

# Choose bandpass freq
f1 = 0.005 # min freq, default 1/200
f2 = 0.05  # max freq, default 1/50

# Select a reference station to plot by network, name, and location (e.g. CH.FUSIO.,CH.GRIMS.)
station = "2025-10-10T20-19-20.7M.S083" # "FR.SALF." 

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


#### (H) #####

print("data_directory : ", data_directory)
print("prodata_directory : ", prodata_directory)
print("resp_directory : ", resp_directory)


# Set up figure directory
fig_directory = fig_directory + "/" + "figures_" + event_name + "/" # (H) added "/" at the begenning
if not path.exists(fig_directory):  # If figure directory doesn't exist, it will create one
    makedirs(fig_directory)
movie_directory = fig_directory + "movie/"
if not path.exists(movie_directory):  # If movie directory doesn't exist, it will create one
    makedirs(movie_directory)
    print("New movie directory "+movie_directory+" is created.")
else:
    print("Movie directory "+movie_directory+ " exists.")

## Read event catalog (Read QUAKEML or pkl)
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


GMV_plot_MACIV(GMV, event_dic, stream_info, thechosenone,
         vmin, vmax, arr_img, movie_directory, map_loc=map_loc, map_region=map_region,
         timeframes=timeframes, timelabel=timelabel,
         save_option=save_option, save_dpi=save_dpi, plot_save=False,
         plot_local=plot_local, plot_3c=plot_3c, plot_rotate=plot_rotate)

    
print("--- %.3f seconds ---" % (time.time() - prog_starttime))
print("---- %.3f mins ----" % ((time.time() - prog_starttime)/60))
