import pygmt
import geopandas as gpd
from pathlib import Path

""""
Creates the map of the French Massif Central using pygmt.
"""

parent_file = Path(__file__).resolve().parent.parent


# Path to the KML file
McFkml_file = parent_file / "map_files" / "Massif_Central_contour.kml"
# Read the KML file using GeoPandas
McF = gpd.read_file(McFkml_file).to_crs(epsg=4326)
McF = McF.simplify(tolerance=0.01, preserve_topology=True)

kml_file = parent_file / "map_files" / "Regions_volcaniques.kml"
volc = gpd.read_file(kml_file).to_crs(epsg=4326)

Fault_file = parent_file / "map_files" / "Neotectonic map (Grellet et al., 1993).kml"
Fault1 = gpd.read_file(Fault_file).to_crs(epsg=4326)
Fault1 = Fault1.simplify(tolerance=0.01, preserve_topology=True)

Fault_file = parent_file / "map_files" / "Potentially active Faults.kml"
Fault2 = gpd.read_file(Fault_file).to_crs(epsg=4326)
Fault2 = Fault2.simplify(tolerance=0.01, preserve_topology=True)


# Define the regions of interest
regionNodes2 = [1.8, 4.2, 44.8, 46.5]


# Create a PyGMT figure for McF sismicity - in color
fig = pygmt.Figure()

#define etopo data file
topo_data = '@earth_relief_15s' #15 arc second global relief (SRTM15+V2.1 @ 1.0 km)

pygmt.makecpt(cmap='gmt/gray', series='-3500/3000/50',continuous=True, output='elevation.cpt')


# Add topography (relief map)
print("add topo")
fig.basemap(region=regionNodes2, projection="Q12c", frame="0")
fig.grdimage(grid=topo_data, region=regionNodes2, shading=True, cmap="elevation.cpt") 

# Add coastline
print("add coastline")
fig.coast(shorelines="1/0.5p,black", resolution="i", area_thresh=10,
                   borders=["1/0.5p,black", "2/0.5p,red", "3/0.5p,blue"])

# plot volcanoes
print("volcanoes")
fig.plot(data=volc, fill="#8f8571", pen="0p",transparency=60, label="volcanic regions")


# fig.savefig('FMC_bakcground.png')

fig.show()