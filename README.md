Code are based on the work of :
```
On Ki Angel Ling, Simon C. Stähler, Domenico Giardini, the AlpArray Working Group; Visualizing Global Seismic Phases with AlpArray. Seismological Research Letters 2021; 92 (6): 3845–3855. doi: https://doi.org/10.1785/0220210046`
```



# GMV_MACIV

Python code for ground motion visualization for MACIV nodes.

Note : lines ending by # (H) have been added or modified by Hazurya

Plan :

- Where to start ?
- Brief Descriptions of All Features
- Detailed description of all features
- Suggestions for improvement
- Examples of parameters selected for visualizing the Drake Passage earthquake 25/10/10-20:19:20



## Where to start ?

#### I_ Place the files correctly

1) Put the mseed files in the data/processed folder.
There should be one file per trace, and their names must follow this structure: :

yyyy-mm-ddThh-mm-ss.7M.station_name.00.channel.D.mseed

   yyyy-mm-ddThh-mm-ss : time of the event
   channel as DPZ, DPE, DPN, DP1 or DP2

ex : 2025-09-18T12-34-08.7M.C055.00.DPE.D.mseed

To do this, you can use the “extract_to_multiple_mseed” and “extract_to_one_mseed” functions (in the GMV_complt_func.py file; see below).


2) Put the xml files in the data/stationxml folder.
There should be one per station, and their name must follow this structure :

7M.station_name.xml

ex : 7M.C003.xml


3) Put the .pkl or .ml file in the folder data/EVENT_INFO
(if needed, info can also be entered manually, see "readevent" in "GMV.utils.py")

The .ml file can be created using the create_quakeml_file.py (see description below).

In the end, your data should follow the file paths shown in the diagram below.

4) You can also put your background map and logo (as a png with a Plate Carree projection) in the folder "images".
A map background and logo are provided as examples so you can skip this step at first try.

#### II_ Change the most important parameters

In the GMV.py file, when you try this for the first time, here are the most important settings to change:

- *plot_local* - True/False depending on the event is local or not

- check that :
    *prodata_directory* points to "processed"
    *resp_directory* points to "stationxml"
    *evt_info_directory* points to your .ml or .pkl files


- *map_region* - Specify the region in which the coordinates of your stations will be plotted, using a list in the format [minimum longitude, maximum longitude, minimum latitude, maximum latitude]

- set the *start* and end *parameters* (starting and ending time in seconds)

- *decimate* - how much your data is going to be downsampled

- set the data process parameters :
    *filer_type* - "bandpass"/"highpass"/"lowpass"
    f1, f2 - cutoff frequences if filter_type = "bandpass"
    f - cutoff frequency if filter_type = "highpass" or "lowpass"

- station - choose a reference stations (indicate its name)

The program should now be ready to run.

For your next tests, you can also adjust other settings (described below).

## Brief Descriptions of All Features:

### GMV.py

- main code
- contains all parameters for data processing and animation

author(s) : Angel Ling, revisited by Hazurya for adaptation to MACIV nodes

### GMV_utils.py

- contains most functions for GMV.py

author(s) : Angel Ling, revisited by Hazurya for adaptation to MACIV nodes (a lot of non useful functions for MACIV nodes visualization have been deleted)

### GMV_complt_func.py

- contains complementary functions for nodes visualization

author(s) : Hazurya (exept for GMV_plot_MACIV mostly inspired by GMV_plot original function by Angel Ling)

### draft_GMV_plot.py

- Minimalist program to test the layout

Note : somehow the logo's place isn't the same when draft_GMV_plot.py and GMV.py run, even with identical parameters.

author(s) : Hazurya

### create_quakeml_file.py

- program to create a quakeml file for the desired event (required for GMV.py (information on event can also be entered by hand, see below))

author(s) : Hazurya

### FMC_map.py

- program to create a map background of the French Massif Central using pygmt

author(s) : Coralie A., revisited by Hazurya


### environment.yml

- yml file about the environnement in which the programs where run and tested

author(s) : Hazurya


## Detailed description of all features

### Paths

The files paths should look like the following :

```text
parent_file/ (no particular name)
│
├── data/
│   ├── processed/
│   │   └── mseed files (one per trace*)
│   │
│   ├── stationxml/
│   │   └── xml files (one per station**)
│   │
│   └── EVENT_INFO/
│       └── .ml or .pkl file about event (required***)
│
├── images/
│   ├── map backgroung file (has to be a png and have a Plate carree projection)
│   └── logo (png)
│
├── GMV_scripts/ (should contain all .py files)
│   ├── GMV.py
│   ├── GMV_utils.py
│   └── GMV_complt_func.py
│
└── test_animations (this path will be created if does not exist, this is where the images and video will be stored)
```

**IMPORTANT** : The program DOES NOT remove the instrument response from the data


All file path should look like the following :

file_path = folder1 / ... / folder2 / file
with folder1 a PurePath object, folder2 and file beeing strings or PurePath objects.

example :
logo_localisation = parent_file / "images" / "logo.png" -> gives path to the logo

parent_file being the path to the folder (as a PurePath object) containing all scripts, data and images (initialized at the beginnning of the code (line : "parent_file = Path(__file__).resolve().parent.parent"))

*if the data is stored in one miniseed file, see the function "extract_to_mutliple_mseed" in GMV_complt_func.py

**IMPORTANT :** all mseed files should be named according to the following structure :

yyyy-mm-ddThh-mm-ss.7M.station_name.00.channel.D.mseed

   yyyy-mm-ddThh-mm-ss : time of the event
   channel as DPZ, DPE, DPN, DP1 or DP2

ex : 2025-09-18T12-34-08.7M.C055.00.DPE.D.mseed

if not, see read_data_inventory in GMV_utils.py

** **IMPORTANT :** all xml files should be named according to the following structure :

7M.station_name.xml

ex : 7M.C003.xml

if not, see read_data_inventory in GMV_utils.py

*** information about event also may be entered by hand in the function readevent in GMV_utils.py, if enter_info_by_hand is set to True.
Note : this version of the program has never been tested with a .pkl file, only with a .ml.


### GMV.py

Parameters that can be changed depending on the event :

- event_name

- plot_local - True/False depending on the event is local or not

- plot_3c - True/False, if False, only the vertical motion will be shown

- plot rotate - if true, then rotates from North/East to Radial/Transverse

- create_video - True/False, if True, will try to create the video

- ouftile - if create_video = True, name of the video file, has to be a .avi (exemple : "test_animation.avi")


- if data follows the file paths above, 
    - data              -> data folder
    - prodata_directory -> mseed files
    - resp_directory    -> xml files
do NOT need to be changed

- evt_info_directory - the name of the quakeml file needs to be changed to fit the desired event **(IMPORTANT)**

- movie_directory - where you want the images to be saved within the parent folder, does NOT need to be changed
WILL BE CREATED IF DOES NOT EXIST


- if data follows the file paths above, you may just need to change the png's names in :
    - logo_loc **(IMPORTANT)**
    - map_loc **(IMPORTANT)**

- map_region - coordonates of the delimited region by the map ([lon min, lon max, lat min, lat max]) **(IMPORTANT)**

- start, end - Choose the starting and ending time in seconds after OT shown in reference seismograms (min: 0, max: 7200)

- decimate_fc - Downsample data by an integer factor (0 to avoid data downsampling)

- timeframes - this parameter might need to be adjuted to fit beginning/end of the animation / have more/less images

- timelabel - "s"/"min"/"hr" for seismograms

- fps - if create_video = True, frame per seconds for the video

- filter_type - "bandpass"/"lowpass"/"highpass" for data processing

- f1, f2 - cutoff frequencies for bandpass filter (don't need to be indicated if "lowpass"/"highpass")

- f - cutoff frequencie for "lowpass"/"highpass" filter (don't need to be indicated if "bandpass")

- station - name of the reference station -> can be found with the middle_station function in GMV_complt_func.py that finds the station the closest to the middle of the map

- model - 1D velocity model to use for ray tracing

- phases - phases to include in tracing

- save_option - Save format

- save_dp - Saved figure resolution (Default: 120)

- vmin - colorbar min, default: -0.1
- vmax - colorbar max, default: 0.1
- scale - lateral motion amplification factor (default : 0.65)


### GMV_utils.py

- readevent :
Reads QUAKEML or pkl (or information entered manually, directly in the function) and returns a dictionnary with those information

- read_data_inventory :
    - Read raw data and station inventory
    - Returns a dictionary with station data and inventory

**Note :**
line 196 ('if file.endswith('DPZ.D.mseed'): # (H))
to
line 335 ('continue')
have been adapted to follow the file name pattern described above.

If the new files don't follow this pattern, the program won't work.
The lines that would need to be changed to fit the new files name structure are indicated with # (H)

Lines 337 ('# Read all OBS channels') to 412 ('data_dict_list.sort(key=itemgetter('dist_sta'))') HAVE NOT been adapted at all for the nodes.

- normalize :
Filter and normalize streams
Return 2 disctionnaries

data is :
    - filtered
    - trimmed between start and end
    - interpolated
    - downsampled
    - traces are normalized by their maximum value

according to parameters entered at the beginning of GMV.py

- station_phase :
get information on the reference station (the chosen one) and store it in a dictionnary

Note : in order to chose a reference station, the function middle_station in GMV_complt_func.py can be used.



### GMV_complt_func.py

A brief descriptions of the functions :

- extract_to_mutliple_mseed : 
if the data is stored in one miniseed file, can create one miniseed per trace with names compatible with the GMV.py program

**may be useful prior to using GMV.py**

- extract_to_one_mseed :
does the oppositite as extract_to_mutliple_mseed, takes several mseed files to make only one for all data

- GMV_plot_MACIV :
final function of GMV.py, plots all the data to create the animation

**Note :** The map's projection uses (43, 49) standard parallel by default, this parameter might need to be changed (directly into the function) depending on the map's background location.

- GMV_plot_MACIV_pygmt :
 obsolete version of GMV_plot_MACIV only using the pygmt library (*never came to fruition*)

 Note :
    - need a path to the kml files in order to work (since that version of the function has never been updated, the path files aren't made for relativ paths like the rest of the program, but absolute paths)

- generate_video - create a video using images (used at the end of GMV.py)

**may be used in an independant python file to create the video**

- map_maciv - create a map of the French Massif Central, used to work with GMV_plot_MACIV_pygmt (*never came to fruition*)


- middle_station - find the closest station to the middle of the map (Note : read only mseed file with station's name ending by "DPZ.D.mseed")


## Suggestions for improvement

- enable more flexibility in the files' names so they don't necessarily have to follow the structure :
    yyyy-mm-ddThh-mm-ss.7M.station_name.00.channel.D.mseed
    7M.station_name.xml
Those changes would have to be made in the "read_data_inventory" function in "GMV_utils.py"


- So far, in the "read_data_inventory" function in "GMV_utils.py", only the lines 196 ("if file.endswith('DPZ.D.mseed'): # (H)") to 335 ("continue") have been adapted for the nodes data. Those correspond to the channels DPZ, DPE, DPN, DP1 and DP2 (parts of the code corresponding to DP1 and DP2 have never been tested).
Lines 338 ("elif file.endswith('CHZ'):") to 409 ("print ('Read ' + str(Z12_count)+ ' Z12 stations.')) have never been adapted.

In conclusion, the "read_data_inventory" could be improved to make it cleaner and more convinient and universal.



## Examples of parameters selected for visualizing the Drake Passage earthquake 25/10/10-20:19:20

```
############# SETTINGS ##############################################################

prog_starttime = time.time() # Execution time of this program

## Event name (Folder name)
event_name = "drake_passage"

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
evt_info_directory = parent_file / "data" / "EVENT_INFO" / "catalog_drake.ml"  # path to pkl of QUAKEML file (H)


# Location of the figures directoy (where images will be stored) (H)
movie_directory = parent_file / "test_animations" / str("figure_" + event_name) / "png_images"

# Path to images (logo and map background)
logo_loc = parent_file / "images" / "logo_maciv.png" # path to logo
map_loc = parent_file / "images" / "light_FMC_map_background.png"   # path to map (has to be a png and the projection has to be Plate carree) (H)
map_region = [1.8, 4.2, 44.8, 46.5]             # [lon min, lon max, lat min, lat max]


# Waveform setting
# Choose the starting and ending time in seconds after OT shown in reference seismograms (min: 0, max: 7200)
start       = 0  # min: 0    # default: 500
end         = 7200 # max: 7200 # default: 7000 
decimate_fc = 0   # Downsample data by an integer factor (Default: 2)   (0 to avoid data downsampling (H))

# Movie setting
# Choose movie interval (default: 1s)
# plot only certain time frame in list or array, e.g.[1772,2220,2527] (Default: None)

timeframes      = range(0, end, 20)    # init range(0, 3600, 30) (H)
timelabel       = "s"                 # "s"/"min"/"hr" for seismograms
fps             = 10                    # frame per second parameter for movie creation (H)

# Data process parameters (H)
filer_type = "lowpass" # filter type

f1 = 1  # min freq, default 1/200 = 0.005 (if bandpass)
f2 = 20 # max freq, default 1/50 = 0.05 (if bandpass)
f = 1   # cutoff frequency, default None (if low/high pass)

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
vmin = -0.1   # colorbar min, default: -0.1
vmax =  0.1   # colorbar max, default: 0.1
scale = 0.15  # lateral motion amplification factor (default : 0.65)

##################################################################################################
```
