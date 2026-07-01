All codes are based on the work :
On Ki Angel Ling, Simon C. Stähler, Domenico Giardini, the AlpArray Working Group; Visualizing Global Seismic Phases with AlpArray. Seismological Research Letters 2021; 92 (6): 3845–3855. doi: https://doi.org/10.1785/0220210046



# GMV_MACIV

Python code for ground motion visualization for MACIV nodes.

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

author(s) : Hazurya (exept for GMV_plot_MACIV mostly inspired by GMV_plot original function from Angel Ling)

### draft_GMV_plot.py

- Minimalist program to test the layout

author(s) : Hazurya

### create_quakeml_file.py

- program to create a quakeml file for the desired event (required for GMV.py)

author(s) : Hazurya

## Detailed description of all features

### Paths

The files paths should look like the following :


parent_file/ (no particular name)
│
├── data/
│   ├── processed/
│   │   └── mseed files (one per trace)
│   │
│   ├── stationxml/
│   │   └── xml files (one per station)
│   │
│   └── EVENT_INFO/
│       └── .ml or .pkl file about event
│
├── images/
│   ├── map backgroung file (has to be a png and have a Plate carree projection)
│   └── logo png
│
└── GMV_scripts/ (should contain all .py files)
    ├── GMV.py
    ├── GMV_utils.py
    └── GMV_complt_func.py

IMPORTANT : The program DOES NOT remove the instrument response from the data


All file path should look like the following :

file_path = folder1 / folder2 / file
with folder1, folder2 and file beeing strings or PurePath objects.

example :
logo_localisation = parent_file / "images" / "logo.png" -> gives path to the logo

parent_file being the path to the folder (as a PurePath object) containing all scripts, data and images (initialized at the beginnning of the code (parent_file = Path(__file__).resolve().parent.parent))

*if the data is stored in one miniseed file, see the function "extract_to_mutliple_mseed" in GMV_complt_func.py


### GMV.py

Parameters that can be changed depending on the event :

- event_name

- plot_local - True/False depending on the event is local or not

- plot_3c - True/False, if False, only the vertical motion will be shown

- plot_rotate (?)

- create_video - True/False, if True, will try to create the video

- ouftile - if create_video = True, name of the video file, has to be a .avi (exemple : "test_animation.avi")


- if data follows the file paths above, 
    - data              -> data folder
    - prodata_directory -> mseed files
    - resp_directory    -> xml files
do NOT need to be changed

- evt_info_directory - the name of the quakeml file needs to be changed to fit the desired event (IMPORTANT)

- movie_directory - where you want the images to be saved within the parent folder, does NOT need to be changed
WILL BE CREATED IF DOES NOT EXIST


- if data follows the file paths above, you may just need to change the png's names in :
    - logo_loc (IMPORTANT)
    - map_loc (IMPORTANT)

- map_region - coordonates of the delimited region by the map ([lon min, lon max, lat min, lat max]) (IMPORTANT)

- start, end - Choose the starting and ending time in seconds after OT shown in reference seismograms (min: 0, max: 7200)

- decimate_fc - Downsample data by an integer factor (0 to avoid data downsampling)

- timeframes - this parameter might need to be adjuted to fit beginning/end of the animation / have more/less images

- timelabel - "s"/"min"/"hr" for seismograms

- fps - if create_video = True, frame per seconds for the video

- filter_type - "bandpass"/"lowpass"/"highpass" for data processing

- f1, f2 - cutoff frequencies for bandpass filter (don't need to be indicated if "lowpass"/"highpass")

- f - cutoff frequencie for "lowpass"/"highpass" filter (don't need to be indicated if "bandpass")

- station - name of the reference station -> can be found with the middle_station function in GMV_complt_func.py that finds the station the closest to the middle of the map

- model (?)

- phases (?)

- save_option - Save format

- save_dp - Saved figure resolution (Default: 120)

- vmin - colorbar min, default: -0.1
- vmax - colorbar max, default: 0.1


### GMV_utils.py


### GMV_complt_func.py

A brief descriptions of the functions :

- extract_to_mutliple_mseed : if the data is stored in one miniseed file, can create one miniseed per trace with names compatible with the GMV.py program

**may be useful prior to using GMV.py**

- extract_to_one_mseed : does the oppositite as extract_to_mutliple_mseed, takes several mseed files to make only one for all data

- GMV_plot_MACIV - final function of GMV.py, plots all the data to create the animation

- GMV_plot_MACIV_pygmt - obsolete version of GMV_plot_MACIV only using the pygmt library (*never came to fruition*)

- generate_video - create a video using images (used at the end of GMV.py)

**May be used in an independant python file to create the video**

- map_maciv - creates a map of the French Massif Central, used to work with GMV_plot_MACIV_pygmt (*never came to fruition*)


- middle_station - finds the closest station to the middle of the map
