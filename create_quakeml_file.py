from obspy import read, Stream, UTCDateTime, read_inventory
from obspy.clients.fdsn import Client

"""
Code to create an ml file for the event. Required for the animation, or enter informations manually.

How to use this code ?

1) enter the event time, the magnitude and the file name you want as an output as parameters.
Check the line 29 (file = catalog[1].write(file_name, format="QUAKEML") is commented to avoid the creation of a wrong quakeml file.

2) Choose a client ("USGS", "EPOSFR", etc - more examples in obspy's documentation) and find the event you are looking for.
Several tries might be necessay to find the right client where the event's information is stored. 

3) Once you find your event, write its index in catalog in line 28 (file = catalog[index].write(file_name, format="QUAKEML")) and uncomment the line before running the program.

"""

event_time="2025-09-18T12:34:08.937068"
magnitude=3.58
file_name="catalog_saintes.ml"

client = Client("EPOSFR")
t = UTCDateTime(event_time) # time of the event
catalog = client.get_events(starttime=t-100, endtime=t+3*3600, minmagnitude=magnitude-1)

print(catalog)

# file = catalog[1].write(file_name, format="QUAKEML")