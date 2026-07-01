from obspy import read, Stream, UTCDateTime, read_inventory
from obspy.clients.fdsn import Client
import os
import numpy as np 
import pygmt
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from GMV_utils import phase_marker
from matplotlib.ticker import MultipleLocator # (H)
from pygmt.datasets import load_earth_relief # (H)
import os # (H)
import cv2 # (H)
from PIL import Image # (H)
import cartopy.crs as ccrs
import matplotlib.image as mpimg
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from os import listdir
from obspy.geodetics import gps2dist_azimuth




def extract_to_mutliple_mseed(data_directory, event_time, saving_directory):
    """creates one mseed file per trace from one mseed file

    :param data_directory: path to the folder containing the mseed file
    :param event_time: yyyy-mm-ddThh-mm-ss ex: 2025-09-18T12-34-08
    :param saving_directory: path to the folder where mseed files will be saved
    """

    st = read(data_directory)
    print(f"files will be saved in {saving_directory}")
    for trace in st:
        name = f"{event_time}.7M.{trace.stats.station}.00.{trace.stats.channel}.D.mseed"
        trace.write(saving_directory + "/" + name)
        print(name, "saved")




def extract_to_one_mseed(k, data_directory):
    "extracts k stations from one mseed files and creates an mseed file with those traces (if data are in several mseed files, one per trace)"
    files = os.listdir(data_directory)
    st = Stream()

    if k > len(files)//3 :
        print(f"There are only {len(files)//3} stations in file.")
        for i in range(3*len(files)):
            st += read(data_directory + files[i])
    else:
        for i in range(3*k):
            st += read(data_directory + files[i])
    print(st)
    st.write(f"2025-10-10T20-29-20_{len(st)//3}_stations.mseed", format='MSEED')
    return st

# use a png as a map
def GMV_plot_MACIV(GMV, event_dic, stream_info, thechosenone, 
             vmin, vmax, arr_img, movie_directory, map_loc, map_region,
             timeframes=None, timelabel="s", scale = 0.2,
             plot_save=True, save_option="png", save_dpi=120,
             plot_local=False, plot_3c=True, plot_rotate=True):
    
    """
    Plot single timestep of GMV and reference seismograms 
    
    :param GMV: processed data dictionary
    :param event_dic: event dictionary
    :param stream_info: stream info dictionary
    :param thechosenone: the reference station info dictionary
    :param vmin: colorbar min
    :param vmax: colorbar max
    :param arr_img: logo
    :param movie_directory: movie directory path
    :param map_loc: map directory path # (H)
    :param map_region: delimited region by the map # (H)
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

    # defines the projection for furure plotting (H)
    proj = ccrs.LambertConformal(central_longitude =(map_region[0]+map_region[1])/2,
                                central_latitude =(map_region[2]+map_region[3])/2,
                                standard_parallels = (43, 49) ) #(H)
    # reads the map image (H)
    img = mpimg.imread(map_loc) # (H)

    
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
        
    print("Plots will be saved in " + str(movie_directory))
        
    step = 0 # used only when plot_local is True
    for it in timeframes: # from start time to end time 
        if (start+it*timestep) % 500 == 0:
            print("Plotting %07.1f s..."%(start+it*timestep))
        # Just the simple map and seismograms
        # Setting up the plot
        fig = plt.figure(figsize=(10, 8.5)) 
        gs=GridSpec(5,1, height_ratios=[4,0.05,0.55,0.55,0.55])
        gs.update(hspace=0.1)
        ax1 = plt.subplot(gs[0], projection=proj) # adds the projection type of the subplot # (H)
        ax1.set_axis_off() # removes the frame of the subplot (H)
        axs = plt.subplot(gs[1])
        axs.set_visible(False)
        ax2 = plt.subplot(gs[2])
        ax3 = plt.subplot(gs[3])
        ax4 = plt.subplot(gs[4])

        # prepares the place for the map in the subplot (H)
        ax1.set_extent(map_region, crs=ccrs.PlateCarree())
        
        # places the map in the subplot (H)
        ax1.imshow(img, origin='upper', extent=map_region, transform=ccrs.PlateCarree())

        
        # Plot the stations
        # Plot 3C motion
        if plot_3c:
            scale = scale
            x_sta, y_sta = lon_sta_new+(GMV["GMV_E"][:,it]*scale), lat_sta_new+(GMV["GMV_N"][:,it]*scale)

            alpmap = ax1.scatter(x_sta, y_sta, c=GMV["GMV_Z"][:,it], edgecolors='k', marker='o', s=45, cmap='bwr', vmin=vmin, vmax=vmax, zorder=3, transform=ccrs.PlateCarree())
        
        # Plot vertical motion only
        else:
            x_sta, y_sta = lon_sta_new, lat_sta_new
            alpmap = ax1.scatter(x_sta, y_sta, c=GMV["GMV_Z"][:,it], edgecolors='k', marker='o', s=45, cmap='bwr', vmin=vmin, vmax=vmax, zorder=3, transform=ccrs.PlateCarree())
        # Plot reference station (Plotting it again to avoid being covered by other dots)
        alpmap_n1= ax1.scatter(x_sta[thechosenone["sta_index"]], y_sta[thechosenone["sta_index"]], c=GMV["GMV_Z"][thechosenone["sta_index"],it], edgecolors='k', marker='o', s=45, cmap='bwr', vmin=vmin, vmax=vmax, zorder=4, transform=ccrs.PlateCarree())
        alpmap_n = ax1.plot(x_sta[thechosenone["sta_index"]], y_sta[thechosenone["sta_index"]], fillstyle='none', markeredgecolor="lime", markeredgewidth=3, marker="o", markersize=8, zorder=5, transform=ccrs.PlateCarree())
        
        if plot_local: # Plot local epicenter
            x_eq, y_eq = event_dic["lon"], event_dic["lat"]
            alpmap_eq = ax3.plot(x_eq, y_eq, c="yellow", markeredgecolor="k", markeredgewidth=1.5, marker="*", markersize=15, zorder=4, ax=ax1)
        
        # creates a new axis for the colorbar (H)
        cax = inset_axes(ax1, width="5%", height="90%", loc='center left', bbox_to_anchor=(1.04, 0, 1, 1), bbox_transform=ax1.transAxes, borderpad=0) # bbox_to_anchor = [left, bottom, width, height]

        # colorbar (H)
        ticks = [vmin*0.95, 0, vmax*0.95]
        cbar = plt.colorbar(alpmap, cax=cax, ticks=ticks, pad=0.04, location = 'right')
        cbar.ax.set_yticklabels(["Down","0","Up"], fontsize=12)
        cbar.ax.tick_params(size=0)
        
        ax1.set_title("%04d"% event_dic["year"]+'/'+"%02d"% event_dic["month"] +'/'+"%02d"% event_dic["day"]+' '+
                      "%02d"% event_dic["hour"] +':'+"%02d"% event_dic["minute"] +':'+"%02d"% event_dic["second"]+
                      ' '+event_dic["mag_type"].capitalize()+' '+"%.1f"% event_dic["mag"]+' '+ event_dic["region"]+'\n'+ # (H) string.capwords retirée)
                      '  Lat '+"%.2f"% event_dic["lat"] +' Lon '+"%.2f" % event_dic["lon"]+', Depth '+ "%.1f"% event_dic["depth"]+'km'+
                      ', Distance '+ "%.1f"% np.median(GMV["dist_sta"])+'\N{DEGREE SIGN}, '+str(len(name_sta_new))+' STA', fontsize=14)
    
        # Add logo on plot
        imagebox = OffsetImage(arr_img, zoom=0.15)
        imagebox.image.axes = ax1
        ab = AnnotationBbox(imagebox, (1, 1),
                            xybox=(-250., 235.),
                            xycoords='data',
                            boxcoords="offset points",
                            pad=0.5, frameon=False)
        
        ax1.add_artist(ab)
        
        # Plot reference seismograms
        # DPZ # initially HHZ (H)
        ax2.plot( (time_st+start)/d_time, GMV["GMV_Z"][thechosenone["sta_index"]], color="k", linewidth=0.8, label=thechosenone["sta_name"]+".Z") # linewidth=1.5 (H)
        ax2.axvline(x=(start+it*timestep)/d_time, color="r", linewidth=1.2) # Time marker
        # Plot phase marker for channel Z
        phase_marker(thechosenone["arr"], ax2, "Z", start/d_time, end/d_time, timelabel=timelabel, plot_local=plot_local)
        
        ax2.grid(which='major') # initially ax2.grid(b=True, which='major') but raised an error (H)
        ax2.set_xlim([start/d_time,end/d_time])
        ax2.set_ylim([-1.1,1.1]) 
        ax2.set_xticks(seismo_labels)
        ax2.set_xticklabels([])
        ax2.legend(loc='lower right', fontsize=8, bbox_to_anchor=(0.99, -0.07))
        
        # DPN/R
        if plot_rotate:
            ax3.plot((time_st+start)/d_time, GMV["GMV_R"][thechosenone["sta_index"]], color="k", linewidth=0.8, label=thechosenone["sta_name"]+".R") # linewidth=1.5 (H)
#            phase_marker(thechosenone["arr"], ax3, "R", start/d_time, end/d_time, timelabel=timelabel, plot_local=plot_local)
        else:    
            ax3.plot((time_st+start)/d_time, GMV["GMV_N"][thechosenone["sta_index"]], color="k", linewidth=0.8, label=thechosenone["sta_name"]+".N") # linewidth=1.5 (H)
            phase_marker(thechosenone["arr"], ax3, "N", start/d_time, end/d_time, timelabel=timelabel, plot_local=plot_local)
        ax3.axvline(x=(start+it*timestep)/d_time, color="r", linewidth=1.2) # Time marker
        
        ax3.grid(which='major')  # initially ax3.grid(b=True, which='major') but raised an error (H)
        ax3.set_xlim([start/d_time,end/d_time])
        ax3.set_ylim([-1.1,1.1]) 
        ax3.set_xticks(seismo_labels)
        ax3.set_xticklabels([])
        ax3.set_ylabel('Normalized Displacement', fontsize=11)
        ax3.legend(loc='lower right', fontsize=8, bbox_to_anchor=(0.99, -0.07))
        
        # DPE/T
        if plot_rotate:
            ax4.plot((time_st+start)/d_time, GMV["GMV_T"][thechosenone["sta_index"]], color="k", linewidth=0.8, label=thechosenone["sta_name"]+".T")
            phase_marker(thechosenone["arr"], ax4, "T", start/d_time, end/d_time, timelabel=timelabel, plot_local=plot_local)
        else:
            ax4.plot((time_st+start)/d_time, GMV["GMV_E"][thechosenone["sta_index"]], color="k", linewidth=0.8, label=thechosenone["sta_name"]+".E")
            phase_marker(thechosenone["arr"], ax4, "E", start/d_time, end/d_time, timelabel=timelabel, plot_local=plot_local)
        ax4.axvline(x=(start+it*timestep)/d_time, color="r", linewidth=1.2) # Time marker
        
        ax4.grid(which='major') # ax4.grid(b=True, which='major') (H)
        ax4.tick_params(axis="x",labelsize=12)
        if timelabel == "hr":
            ax4.set_xlabel('Time after origin [hr]', fontsize=14)
            ax4.xaxis.set_minor_locator(MultipleLocator(0.1))
        elif timelabel == "min":
            ax4.set_xlabel('Time after origin [min]', fontsize=14)
        else:
            ax4.set_xlabel('Time after origin [s]', fontsize=14)
        ax4.set_xlim([start/d_time,end/d_time])
        ax4.set_ylim([-1.1,1.1]) 
        ax4.set_xticks(seismo_labels)
        ax4.set_xticklabels(seismo_labels) 
        ax4.legend(loc='lower right', fontsize=8, bbox_to_anchor=(0.99, -0.07)) 
        
        plt.tight_layout(h_pad=1)
        
        if plot_save:
            if plot_local:
                step += 1
            else:
                step = start+it*timestep 
            if plot_3c:
                plt.savefig(movie_directory / str(event_dic['event_name'] +"_3C_"+ "%07.1f"%(step)+"s."+save_option), dpi=save_dpi)
            else:
                plt.savefig(movie_directory / str(event_dic['event_name'] +"_"+ "%07.1f"%(step)+"s."+save_option), dpi=save_dpi)
                
            plt.clf()
            plt.close()
            
        else:
            plt.show()
            
    if plot_save:
        print("Plots are saved. End of plotting.")
    else:
        print("Plots are not saved. End of plotting.")

def GMV_plot_MACIV_pygmt(GMV, event_dic, stream_info, thechosenone,
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
        
        map.colorbar( position="JMR+w8c/0.5c+o0.7c/0c", frame="+lZ component")        

        if plot_save:
            if plot_local:
                step += 1
            else:
                step = start+it*timestep 
            if plot_3c:
                map.savefig(fname = movie_directory+ event_dic['event_name'] +"_3C_"+ "%07.1f"%(step)+"s."+save_option, dpi=save_dpi)
                print("it : ", it)
            else:
                map.savefig(movie_directory+ event_dic['event_name'] +"_"+ "%07.1f"%(step)+"s."+save_option, dpi=save_dpi)
        
            del map # delete the figure to avoid overloading memory          
            
    if plot_save:
        print("Plots are saved. End of plotting.")
    else:
        print("Plots are not saved. End of plotting.")

def generate_video(image_folder, video_name, fps = 15):
    """Generates a video (.avi format)"""


    images = [img for img in os.listdir(image_folder) if img.endswith((".jpg", ".jpeg", ".png"))]
    print("Images:", images)

    # Set frame from the first image
    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, layers = frame.shape

    # Video writer to create .avi file
    video = cv2.VideoWriter(video_name + ".avi", cv2.VideoWriter_fourcc(*'DIVX'), fps, (width, height))

    # Appending images to video
    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))

    # Release the video file
    video.release()
    cv2.destroyAllWindows()
    print("Video generated successfully!")

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
    fig.grdimage(grid=topo_grid, region=regionNodes2, shading=True, cmap="gmt/gray", )

    # Add coastline
    fig.coast(shorelines="1/0.5p,black", resolution="i", area_thresh=10,
                   borders=["1/0.5p,black", "2/0.5p,red", "3/0.5p,blue"])

    # plot volcanoes
    fig.plot(data=volc, fill="#8f8571", pen="0p",transparency=60, label="volcanic regions")

    return fig

def middle_station(map_region, prodata_directory, resp_directory):
    """Find the closest station to the middle of the map"""

    name = []
    lat = []
    lon = []
    mid_dist = []

    mid_lon = (map_region[0]+map_region[1])/2
    mid_lat = (map_region[2]+map_region[3])/2

    for file in listdir(prodata_directory):
        if file.endswith('DPZ.D.mseed'):
            tr = read(prodata_directory+file)
            inv_sta = read_inventory(resp_directory + f"7M.{tr[0].stats.station}.xml")

            name.append(tr[0].stats.station)
            lat.append(inv_sta[0][0].latitude)
            lon.append(inv_sta[0][0].longitude)

    for la, lo in zip(lat, lon):
        mid_dist.append(gps2dist_azimuth(la, lo, mid_lat, mid_lon)[0])

    index_min = mid_dist.index(min(mid_dist))

    return name[index_min]