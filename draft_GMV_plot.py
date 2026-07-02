import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from matplotlib.gridspec import GridSpec
import matplotlib.image as mpimg
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.cbook import get_sample_data
from pathlib import Path


parent_file = Path(__file__).resolve().parent.parent


vmin = -0.1   # colorbar min, default: -0.1
vmax =  0.1   # colorbar max, default: 0.1

map_region = [1.8, 4.2, 44.8, 46.5] # [lon min, lon max, lat min, lat max] (light_map_background.png)


proj = ccrs.LambertConformal(central_longitude =(map_region[0]+map_region[1])/2,
                             central_latitude =(map_region[2]+map_region[3])/2, 
                             standard_parallels = (43, 49))


gs=GridSpec(5,1, height_ratios=[4,0.05,0.55,0.55,0.55])
gs.update(hspace=0.1)
ax1 = plt.subplot(gs[0], projection=proj)
axs = plt.subplot(gs[1])
axs.set_visible(False)
ax2 = plt.subplot(gs[2])
ax3 = plt.subplot(gs[3])
ax4 = plt.subplot(gs[4])


images = parent_file / "images"
logo_loc = images / "LogoMaciv.png" # path to logo
map_loc = images / "light_map_background.png" # path to map background


img = mpimg.imread(map_loc)

ax1.set_extent(map_region, crs=ccrs.PlateCarree())
ax1.set_axis_off() # removes the frame of the subplot


ax1.imshow(img, origin='upper', extent=map_region, transform=ccrs.PlateCarree())



stations_lon =  [2.54802351, 2.64122125, 2.73222877, 2.82263965, 2.91193677, 3.0026679, 2.94393786, 3.09750315, 3.1825248,  3.02332463]
stations_lat =  [45.86899977, 45.86582321, 45.86790255, 45.92357984, 45.92314744, 45.9203824, 45.97520064, 45.94969792, 45.91863033, 45.99256603]



alpmap = ax1.scatter(stations_lon, stations_lat, c=stations_lon, edgecolors='k',
                     marker='o', s=45, cmap='bwr', vmin=vmin, vmax=vmax, zorder=3,
                     transform=ccrs.PlateCarree())

# creates a new axis for the colorbar
cax = inset_axes(ax1, width="5%", height="90%", loc='center left', bbox_to_anchor=(1.04, 0, 1, 1), 
                 bbox_transform=ax1.transAxes, borderpad=0) # bbox_to_anchor = [left, bottom, width, height]

ticks = [vmin*0.95, 0, vmax*0.95]
cbar = plt.colorbar(alpmap, cax=cax, ticks=ticks, pad=0.04, location = 'right')
cbar.ax.set_yticklabels(["Down","0","Up"], fontsize=12)
cbar.ax.tick_params(size=0)

with get_sample_data(logo_loc) as file_img:
    arr_img = plt.imread(file_img, format='png')

# Add logo on plot
imagebox = OffsetImage(arr_img, zoom=0.10)
imagebox.image.axes = ax1
ab = AnnotationBbox(imagebox, (1, 1),
                            xybox=(-150., 130.),
                            xycoords='data',
                            boxcoords="offset points",
                            pad=0.5, frameon=False)
        
ax1.add_artist(ab)


plt.show()