#!/usr/bin/env python3

__author__ = "Angel Ling, revisited by Hazurya in 06-07/2026"

import warnings
warnings.filterwarnings('ignore') 
import time
from os import path, makedirs
import matplotlib.pyplot as plt
from matplotlib.cbook import get_sample_data
from GMV_utils import readevent, read_data_inventory, normalize, station_phases
from GMV_complt_func import GMV_plot_MACIV, generate_video # (H)
from pathlib import Path # (H)
import numpy as np

parent_file = Path(__file__).resolve().parent.parent

############# SETTINGS ##############################################################

prog_starttime = time.time() # Execution time of this program

## Event name (Folder name)
event_name = "event_name"

# local event or not?
plot_local = False

# plot 3 components for seismogram?
plot_3c = True

# ENZ (plot_rotate=False) or RTZ (plot_rotate=True)?
plot_rotate = True

# Create video or not ? (H)
create_video = True
outfile = f"{event_name}.avi" # has to end by .avi

# Location of the data directoy (miniseed, xml, pkl or QUAKEML files) (H)
prodata_directory = parent_file / "data" / "processed"   # path to folder containing miniseed files (H)
resp_directory = parent_file / "data" / "stationxml"     # path to folder containing xml files (H)
evt_info_directory = parent_file / "data" / "EVENT_INFO" / "catalog.ml"  # path to pkl of QUAKEML file (H)


# Location of the figures directoy (where images will be stored) (H)
movie_directory = parent_file / "test_animations" / str("figure_" + event_name) / "png_images"

# Path to images (logo and map background)
logo_loc = parent_file / "images" / "logo_example.png" # path to logo
map_loc = parent_file / "images" / "background_example.png"   # path to map (has to be a png and the projection has to be Plate carree) (H)
map_region = [1.8, 4.2, 44.8, 46.5]             # [lon min, lon max, lat min, lat max]


# Waveform setting
# Choose the starting and ending time in seconds after OT shown in reference seismograms (min: 0, max: 7200)
start       = 0  # min: 0    # default: 500
end         = 3600 # max: 7200 # default: 7000 
decimate_fc = 0   # Downsample data by an integer factor (Default: 2)   (0 to avoid data downsampling (H))

# Movie setting
# Choose movie interval (default: 1s)
# plot only certain time frame in list or array, e.g.[1772,2220,2527] (Default: None)

timeframes      = np.arange(0, end, 20.0)    # init range(0, 3600, 30) (H) can use fractions of second ! Does not have to start at zero or end at end
timelabel       = "s"                 # "s"/"min"/"hr" for seismograms
fps             = 10                    # frame per second parameter for movie creation (H)

# Data process parameters (H)
filer_type = "bandpass" # filter type

f1 = 1.  # min freq, default 1/200 = 0.005 (if bandpass)
f2 = 20. # max freq, default 1/50 = 0.05 (if bandpass)
f = None   # cutoff frequency, default None (if low/high pass)

# Select a reference station to plot by network, name, and location (e.g. CH.FUSIO.,CH.GRIMS.)
station = "S062"

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
vmin = -0.2   # colorbar min, default: -0.1
vmax =  0.2   # colorbar max, default: 0.1
scale = 0.15  # lateral motion amplification factor (default : 0.65)

##################################################################################################

# Set up figure directory

if not path.exists(movie_directory):  # If movie directory doesn't exist, it will create one
    makedirs(movie_directory)
    print("New movie directory "+ str(movie_directory) +" is created.")
else:
    print("Movie directory "+ str(movie_directory) + " exists.")

## Read event catalog (Read QUAKEML or pkl)
event_dic = readevent(event_name, evt_info_directory)

# %% Read data and inventory

## Read processed data and inventories
data_dic = read_data_inventory(prodata_directory, resp_directory, event_dic, plot_3c=plot_3c, tend=end)


# ==================== # %% normalize displacement and store good data

# Filter and normalize one single event
GMV, stream_info = normalize(data_dic, event_dic, f1, f2, start, end, ftype=filer_type, f=f, decimate_fc=decimate_fc, threshold=None)


# Select a reference station for plotting seismogram
thechosenone = station_phases(GMV, station, event_dic, model, phases)


# prepare for plotting

# logo
with get_sample_data(logo_loc) as file_img:
    arr_img = plt.imread(file_img, format='png')
    
# Choose movie interval and turn into index
interval = int(stream_info["sample_rate"])  


GMV_plot_MACIV(GMV, event_dic, stream_info, thechosenone,
         vmin, vmax, arr_img, movie_directory, map_loc=map_loc, map_region=map_region,
         timeframes=timeframes, timelabel=timelabel, scale=scale,
         save_option=save_option, save_dpi=save_dpi, plot_save=True,
         plot_local=plot_local, plot_3c=plot_3c, plot_rotate=plot_rotate)


if create_video :
    try:
        print(movie_directory)
        print(movie_directory.parent / outfile)
        generate_video(movie_directory, movie_directory.parent / outfile, fps=fps)

    except Exception as e :
        print(e)
        print("Video could not be generated, try to use function generate_video in an independant program to compile images")
        

    
print("--- %.3f seconds ---" % (time.time() - prog_starttime))
print("---- %.3f mins ----" % ((time.time() - prog_starttime)/60))
