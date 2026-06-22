from obspy import read, Stream, UTCDateTime
from obspy.clients.fdsn import Client
import os
import numpy as np 
import pygmt
from datetime import date
import geopandas as gpd
import fiona
import pandas as pd
import re
from glob import glob
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colorbar import ColorbarBase
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from GMV_plotting import phase_marker
from matplotlib.ticker import MultipleLocator
from pygmt.datasets import load_earth_relief # (H)








def extract(k):
    "extracts k stations from the mseed files and create an mseed file with those traces (if data are in several mseed files, one per trace)"
    files = os.listdir("2025-10-10T20-29-20")
    st = Stream()
    for i in range(3*k):
        st += read("2025-10-10T20-29-20/" + files[i])
    print(st)
    st.write(f"2025-10-10T20-29-20_{k}_stations.mseed", format='MSEED')
    return st


def quakeml_file(event_time=str, magnitude=float, client = "USGS", file_name="catalog.ml"):
    """
    Fetch data via client to create a quakeml file for the event.
    Supposes it'll find only one event fitting information.
    
    :param event_time: time of the event
    :param magnitude: magnitude of the event
    :param client: client used for the request by obspy, default: "USGS"
    :param file_name: name of the out file, default: "catalog.ml"
    :return: quakeml file with data of the event
    """

    client = Client("USGS")
    t = UTCDateTime(event_time) # time of the drake passage event
    catalog = client.get_events(starttime=t-100, endtime=t+3*3600, minmagnitude=magnitude-1)
    file = catalog[0].write(file_name, format="QUAKEML")
    print(f"file '{file_name}' for the event \n {catalog[0]} \n created")

    return catalog[0].write(file_name, format="QUAKEML")


def map_maciv_obsolete(path_map_files=str):
    """
    Creates a map of the Macif central with pygmt

    :param path_map_files: path to the folder containing kml files to create the map
    :return: map as a pygmt object
    """

    # Path to the KML file
    McFkml_file = path_map_files + "/Massif_Central_contour.kml"
    # Read the KML file using GeoPandas
    McF = gpd.read_file(McFkml_file).to_crs(epsg=4326)
    McF = McF.simplify(tolerance=0.01, preserve_topology=True)
    
    kml_file = path_map_files + "/Regions_volcaniques.kml"
    volc = gpd.read_file(kml_file).to_crs(epsg=4326)

    Fault_file = path_map_files + "/Neotectonic map (Grellet et al., 1993).kml"
    Fault1 = gpd.read_file(Fault_file).to_crs(epsg=4326)
    Fault1 = Fault1.simplify(tolerance=0.01, preserve_topology=True)

    Fault_file = path_map_files + "/Potentially active Faults.kml"
    Fault2 = gpd.read_file(Fault_file).to_crs(epsg=4326)
    Fault2 = Fault2.simplify(tolerance=0.01, preserve_topology=True)

    # Define the regions of interest
    regionNodes2 = [1.8, 4.2, 44.8, 46.5]

    # Create a PyGMT figure for McF sismicity - in color
    fig = pygmt.Figure()

    #define etopo data file
    #topo_data = '@earth_relief_01s_g' #HighResolution
    topo_data_high = '@earth_relief_01s_g' # zoom sur région nodes
    topo_data = '@earth_relief_15s' #15 arc second global relief (SRTM15+V2.1 @ 1.0 km)

    # Add topography (relief map)
    fig.basemap(region=regionNodes2, projection="M5i", frame=True)
    fig.grdimage(grid=topo_data, region=regionNodes2, shading=True, cmap="terra")

    # Add coastline
    fig.coast(shorelines="1/0.5p,black", resolution="i", area_thresh=10,
                   borders=["1/0.5p,black", "2/0.5p,red", "3/0.5p,blue"])

    # plot volcanoes
    fig.plot(data=volc, fill="goldenrod", pen="0p",transparency=60, label="volcanic regions")

    return fig

def map_maciv(McF, volc, Fault1, Fault2, topo_grid):
    """
    Creates a map of the Macif central with pygmt

    :return: map as a pygmt object
    """

    # Read the KML file using GeoPandas
    McF = McF.simplify(tolerance=0.01, preserve_topology=True)
    Fault1 = Fault1.simplify(tolerance=0.01, preserve_topology=True)
    Fault2 = Fault2.simplify(tolerance=0.01, preserve_topology=True)

    # Define the regions of interest
    regionNodes2 = [1.8, 4.2, 44.8, 46.5]

    # Create a PyGMT figure for McF sismicity - in color
    fig = pygmt.Figure()

    # Add topography (relief map)
    fig.basemap(region=regionNodes2, projection="M5i", frame=True)
    fig.grdimage(grid=topo_grid, region=regionNodes2, shading=True, cmap="gmt/gray")

    # Add coastline
    fig.coast(shorelines="1/0.5p,black", resolution="i", area_thresh=10,
                   borders=["1/0.5p,black", "2/0.5p,red", "3/0.5p,blue"])

    # plot volcanoes
    fig.plot(data=volc, fill="#8f8571", pen="0p",transparency=60, label="volcanic regions")

    return fig

def GMV_plot_MACIV(GMV, event_dic, stream_info, thechosenone,
             vmin, vmax, arr_img, map_files,
             movie_directory, timeframes=None, timelabel="s",
             plot_save=True, save_option="png", save_dpi=120,
             plot_local=False, plot_3c=True, plot_rotate=True):
    
    """
    Plot single timestep of GMV and reference seismograms 
    
    :param GMV: processed data dictionary
    :param event_dic: event dictionary
    :param stream_info: stream info dictionary
    :param thechosenone: the reference station info dictionary
    :param start_movie: starting time of the movie (in s) # removed , by laura
    :param end_movie: ending time of the movie (in s)
    :param interval: movie interval (index)
    :param vmin: colorbar min
    :param vmax: colorbar max
    :param arr_img: AlpArray logo
    :param movie_directory: movie directory path
    :param plot_save: If True, save figure
    :param plot_local: If True, plot local event
    :param plot_3c: If True, plot in 3 component on GMV
    :param plot_rotate: If True, seismograms plotted in RT instead of NE
    """
    
    # Variables
    start    = stream_info["start"]
    end      = stream_info["end"]
    timestep = stream_info["timestep"]
    time_st  = stream_info["time_st"]
    lat_sta_new  = GMV["lat_sta"]
    lon_sta_new  = GMV["lon_sta"]
    name_sta_new = GMV["name_sta"]

    # reading the files for the map

    McF = gpd.read_file(map_files + "/Massif_Central_contour.kml").to_crs(epsg=4326)
    volc = gpd.read_file(map_files + "/Regions_volcaniques.kml").to_crs(epsg=4326)
    Fault1 = gpd.read_file(map_files + "/Neotectonic map (Grellet et al., 1993).kml").to_crs(epsg=4326)
    Fault2 = gpd.read_file(map_files + "/Potentially active Faults.kml").to_crs(epsg=4326)

    # Loading topography grid into memory (H)
    regionNodes2 = [1.8, 4.2, 44.8, 46.5]
    topo_grid = load_earth_relief(resolution="15s", region=regionNodes2)

    
    if timelabel == "hr":
        d_time        = 60*60
        seismo_labels = np.arange(round(start/d_time *2 +0.5)/2, round(end/d_time *2 +0.5)/2, 0.5)
        print("Seismograms will be plotted in HOURS.")
    elif timelabel == "min":
        d_time        = 60
        seismo_labels = np.arange(round(round(start/d_time*2 +1)/2, -1), round(round(end/d_time*2 +1)/2,-1), 15)
        print("Seismograms will be plotted in MINUTES.")
    else:
        d_time = 1
        if plot_local:
            seismo_labels = np.arange(int(start), int(end)+1, 100)
        else:
            seismo_labels = np.arange(round(start+1, -3), round(end, -3)+1, 1000)
        print("Seismograms will be plotted in SECONDS.")
    
    if timeframes is None:
        raise ValueError("you must specify time frames to plot")

    print("The following time frames in seconds will be plotted:")
    print(*timeframes)
    timeframes = ((np.array(timeframes)-start)/timestep).astype(int)
        
    if plot_3c:
        print("Ready to plot 3C figures!")
    else:
        print("Ready to plot (vertical component only)!")  
        
    print("Plots will be saved in " + movie_directory)

        
    step = 0 # used only when plot_local is True
    ############################################################ BEGINNING OF THE LOOP
    for it in timeframes: # from start time to end time 
        if (start+it*timestep) % 500 == 0:
            print("Plotting %07.1f s..."%(start+it*timestep))
        # Just the simple map and seismograms
        # Setting up the plot

        map = map_maciv(McF=McF, volc=volc, Fault1=Fault1, Fault2=Fault2, topo_grid=topo_grid) # creating the map (H)

        pygmt.makecpt(cmap="SCM/vik", series=[vmin, vmax]) # colormap (H)

   
        # Plot the stations
        # Plot 3C motion
        if plot_3c:
            if plot_local:
                scale = 0.65
            else:
                scale = 1
            x_sta, y_sta = lon_sta_new+(GMV["GMV_E"][:,it]*scale), lat_sta_new+(GMV["GMV_N"][:,it]*scale)
            alpmap = map.plot(x=x_sta, y= y_sta, style= "c0.3c", fill=GMV["GMV_Z"][:,it], cmap=True, pen="black")


        # Plot vertical motion only
        else:
            x_sta, y_sta = lon_sta_new, lat_sta_new
            alpmap = map.plot(x=x_sta,y= y_sta,  style= "c0.3c", fill=GMV["GMV_Z"][:,it], cmap=True, pen="black") # not tested (H)
        # Plot reference station (Plotting it again to avoid being covered by other dots)
        alpmap_n1= map.plot(x=x_sta[thechosenone["sta_index"]], y=y_sta[thechosenone["sta_index"]], style = "c0.3c", fill='red', cmap=True, pen="0.3p,red")
        
        
        if plot_local: # Plot local epicenter
            x_eq, y_eq = event_dic["lon"], event_dic["lat"]
            alpmap_eq = map.plot(x_eq, y_eq, c="yellow", style= "c0.3c")
        
        map.colorbar(frame="xaf+lZ component")

#        map.show()
        

        if plot_save:
            if plot_local:
                step += 1
            else:
                step = start+it*timestep 
            if plot_3c:
                map.savefig(fname = movie_directory+ event_dic['event_name'] +"_3C_"+ "%07.1f"%(step)+"s."+save_option, dpi=save_dpi, show=True)
                print("it : ", it)
            else:
                map.savefig(movie_directory+ event_dic['event_name'] +"_"+ "%07.1f"%(step)+"s."+save_option, dpi=save_dpi)
        
            del map # delete the figure to avoid overloading memory


                
            
    if plot_save:
        print("Plots are saved. End of plotting.")
    else:
        print("Plots are not saved. End of plotting.")








"""
if __name__ == "__main__":

#    carte = map_maciv("/Users/sommi/Desktop/stage_ISTerre/animations/GMV_okling/map_files")
#    carte.show()

#    quakeml_file("2025-10-10T20-29-20", 7.2, file_name="catalog.ml")
#    st = extract(3)
#    st.plot()"""