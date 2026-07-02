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

author(s) : Hazurya (exept for GMV_plot_MACIV mostly inspired by GMV_plot original function by Angel Ling)

### draft_GMV_plot.py

- Minimalist program to test the layout

Note : somehow the logo's place isn't the same when draft_GMV_plot.py and GMV.py run, even with identical parameters.

author(s) : Hazurya

### create_quakeml_file.py

- program to create a quakeml file for the desired event (required for GMV.py (information on event can also be entered by hand, see below))

author(s) : Hazurya

## Detailed description of all features

### Paths

The files paths should look like the following :

(The file path scheme doesn't appear correctly on github with the preview mode, swap to code visulisation to have the right display)

'''text
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
└── GMV_scripts/ (should contain all .py files)
    ├── GMV.py
    ├── GMV_utils.py
    └── GMV_complt_func.py
'''

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

    - yyyy-mm-ddThh-mm-ss : time of the event
    - channel as DPZ, DPE, DPN, DP1 or DP2

ex : 2025-09-18T12-34-08.7M.C055.00.DPE.D.mseed

if not, see read_data_inventory in GMV_utils.py

** **IMPORTANT :** all xml files should be named according to the following structure :

7M.station_name.xml

ex : 7M.C003.xml

if not, see read_data_inventory in GMV_utils.py

*** information about event also may be entered by hand in the function readevent in GMV_utils.py, if enter_info_by_hand is set to True


### GMV.py

Parameters that can be changed depending on the event :

- event_name

- plot_local - True/False depending on the event is local or not

- plot_3c - True/False, if False, only the vertical motion will be shown

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

- save_option - Save format

- save_dp - Saved figure resolution (Default: 120)

- vmin - colorbar min, default: -0.1
- vmax - colorbar max, default: 0.1


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

- map_maciv - creates a map of the French Massif Central, used to work with GMV_plot_MACIV_pygmt (*never came to fruition*)


- middle_station - finds the closest station to the middle of the map (Note : read only mseed file with station's name ending by "DPZ.D.mseed")