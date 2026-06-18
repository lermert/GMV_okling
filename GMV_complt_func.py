from obspy import read, Stream, UTCDateTime
from obspy.clients.fdsn import Client
import os



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

    

if __name__ == "__main__":

    quakeml_file("2025-10-10T20-29-20", 7.2, file_name="catalog.ml")
#    st = extract(3)
#    st.plot()


    