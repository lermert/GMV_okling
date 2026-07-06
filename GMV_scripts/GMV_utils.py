#!/usr/bin/env python3

__author__ = "Angel Ling, revisited by Hazurya in 06-07 2026"

import obspy
import pickle
import numpy as np
from os import listdir
from obspy.geodetics.base import gps2dist_azimuth  # distance in m, azi and bazi in degree
from obspy.geodetics import kilometers2degrees     # distance in degree
from obspy.geodetics.flinnengdahl import FlinnEngdahl
from obspy.signal.rotate import rotate_ne_rt
from obspy.taup import TauPyModel
from operator import itemgetter


def maxabs(x):
    return max(abs(x))

# Function to calculate the antipode
def antipode(lat, lon):
    lat *= -1
    if lon > 0:
        lon -= 180
    elif lon <= 0:
        lon += 180
    return lat, lon


def readevent(event_name, evt_info_directory, enter_info_by_hand = False):
    """
    Read QUAKEML or pkl downloaded via obspyDMT
    
    :param event_name: 
    :param evt_info_directory: path to the quakeml file or pkl file
    :param enter_info_by_hand: if info is entered manually (in that case, enter information directly in the function)
    :return: event dictionary
    """
    print("Reading event "+event_name+"...")
    print("Reading event catalog "+event_name+"...")
    event_dic = {}
    if not enter_info_by_hand:
        try: # QUAKEML
            cat = obspy.read_events(evt_info_directory, format="QUAKEML") # (H)
            ev  = cat[0]
            origin    = ev.preferred_origin()
            lat_event = origin.latitude
            lon_event = origin.longitude
            dep_event = origin.depth/1000.
            ev_otime  = origin.time
            time_event_sec = ev_otime.timestamp
            year   = ev_otime.year
            month  = ev_otime.month
            day    = ev_otime.day
            hour   = ev_otime.hour
            minute = ev_otime.minute
            second = float(ev_otime.second) + ev_otime.microsecond / 1E6
            
            if ev.preferred_magnitude().magnitude_type in ["mw", "mww"]:
                    mag_type  = ev.preferred_magnitude().magnitude_type
                    mag_event = ev.preferred_magnitude().mag
            else:
                for _i in ev.magnitudes:
                    if _i.magnitude_type in ["Mw", "Mww"]:
                        mag_type  = _i.magnitude_type
                        mag_event = _i.mag
                    else:
                        mag_type  = _i.magnitude_type
                        mag_event = _i.mag
        except FileNotFoundError: # Event pkl
            ev_pkl = pickle.load(open(evt_info_directory, "rb")) # (H)
            lat_event = ev_pkl.get('latitude')
            lon_event = ev_pkl.get('longitude')
            dep_event = ev_pkl.get('depth')
            ev_otime  = ev_pkl.get("datetime")
            time_event_sec = ev_otime.timestamp
            year   = ev_otime.year
            month  = ev_otime.month
            day    = ev_otime.day
            hour   = ev_otime.hour
            minute = ev_otime.minute
            second = float(ev_otime.second) + ev_otime.microsecond / 1E6
            
            mag_type  = ev_pkl.get("magnitude_type")
            mag_event = ev_pkl.get("magnitude")
    
    # Enter event info by hand
    elif enter_info_by_hand:
        lat_event = 17.257
        lon_event = -61.327
        dep_event = 10.0
        ev_otime  = obspy.UTCDateTime("2026-05-16T14:50:06.600500Z")#obspy.UTCDateTime("2020-10-25 19:35:43")
        time_event_sec = ev_otime.timestamp
        year   = ev_otime.year
        month  = ev_otime.month
        day    = ev_otime.day
        hour   = ev_otime.hour
        minute = ev_otime.minute
        second = float(ev_otime.second) + ev_otime.microsecond / 1E6
            
        mag_type  = "M" #"ML"
        mag_event = 5.8 #4.4
    
    fe = FlinnEngdahl()
    event_dic['event_name'] = event_name
    event_dic['region']     = fe.get_region(lon_event,lat_event)
    event_dic['lat']        = lat_event
    event_dic['lon']        = lon_event
    event_dic['depth']      = dep_event
    event_dic["ev_otime"]   = ev_otime
    event_dic['time_sec']   = time_event_sec
    event_dic['year']       = year
    event_dic['month']      = month
    event_dic['day']        = day
    event_dic['hour']       = hour
    event_dic['minute']     = minute
    event_dic['second']     = second
    event_dic['mag_type']   = mag_type
    event_dic['mag']        = mag_event
    
    return event_dic

# ==================================
# %% Read and process streams and inventories

def keep_trace(st, keep):
    newst  = obspy.Stream()
    for i, tr in enumerate(st):
        if i in keep:
            newst += tr
    return newst

def filter_streams(st, f1, f2, f=None, ftype="bandpass"):
    """
    Filter streams
    
    :param st: stream
    :param f1: lower frequency
    :param f2: higher frequency
    :param f: frequency for lowpass/highpass, default: None
    :param ftype: filter type, default: "bandpass"
    :return: filtered stream
    """
    st_filtered = st.copy()
    st_filtered.detrend("demean")
    st_filtered.detrend('linear')
    st_filtered.taper(0.01, 'cosine') # init 0.05 (H)
    if ftype == "bandpass":
        st_filtered.filter(ftype, freqmin=f1, freqmax=f2, corners=4, zerophase=True)
    else:
        st.filter(ftype, freq=f, corners=4, zerophase=True)
    st_filtered.detrend('linear') # detrend after filtering
    
    return st_filtered

def read_data_inventory(prodata_directory, resp_directory, event_dic, tstart=0, tend=600, read_obs=False, plot_3c=True):
    """
    Read raw data and station inventory
    
    :param prodata_directory: data directory
    :param resp_directory: inventory directory
    :param event_dic: event dictionary
    :param read_obs: option to read OBS data
    :param plot_3c: option to plot in 3 component
    :return: dictionary with station data and inventory
    """
    print ('Reading data and inventory...')
    
    st1 = obspy.Stream() # Z channels
    st2 = obspy.Stream() # N channels
    st3 = obspy.Stream() # E channels 
    lat_sta  = np.array([])
    lon_sta  = np.array([])
    elv_sta  = np.array([])
    dist_sta = np.array([])
    azi_sta  = np.array([])
    bazi_sta = np.array([])
    name_sta = np.array([])
    net_sta  = np.array([])
    
    lat_event  = event_dic["lat"]
    lon_event  = event_dic["lon"]
    region     = event_dic["region"]
    event_time = event_dic["time_sec"] 
    stime      = obspy.UTCDateTime(event_time + tstart) 
    etime      = obspy.UTCDateTime(event_time + tend)
    data_dict_list = []
    
    obs = 0 # obs counter
    Z12_count  = 0 # Z12 station counter 
    
    print ('Processing data of '+event_dic['mag_type'].capitalize()+"%.1f "%event_dic['mag']+region+' earthquake...')
    print ('Reading trace from '+str(tstart)+' to '+str(tend)+'s from the origin time...')
    
    for file in sorted(listdir(prodata_directory)):
        if file.endswith('DPZ.D.mseed'): # (H)
            fsp = file.split(".")
            try:
                # DPZ (H)
                tr11    = obspy.read(prodata_directory / file, starttime=stime, endtime=etime) # read the trace
                inv_sta = obspy.read_inventory(resp_directory / f"7M.{tr11[0].stats.station}.xml") # (H)
                # Stations with data missing more than 10% of their samples are discarded.
                data_count = (tend-tstart)*tr11[0].stats.sampling_rate - ((tend-tstart)*tr11[0].stats.sampling_rate*0.1) 
                if tr11[0].stats.npts < data_count:
                    continue              
            except Exception as e: # If file not present, skip this station
                # print(e)
                continue
            
            # Read station location
            lat = inv_sta[0][0].latitude
            lon = inv_sta[0][0].longitude
            elv = inv_sta[0][0].elevation /1000. # in km
            dist, azi, bazi = gps2dist_azimuth(lat_event, lon_event, lat, lon)
            dist_deg        = kilometers2degrees(dist/1000.)
                
            tr11[0].stats.distance       = dist_deg
            tr11[0].stats.backazimuth    = bazi
            tr11[0].stats["coordinates"] = {}
            tr11[0].stats["coordinates"]["latitude"]  = lat
            tr11[0].stats["coordinates"]["longitude"] = lon
            tr11[0].stats["coordinates"]["elevation"] = elv
            
            try: # Read DPN (H)
                tr22 = obspy.read(prodata_directory / str(fsp[0]+"."+fsp[1]+"."+fsp[2]+".00.DPN.D.mseed"), starttime=stime, endtime=etime) # (H)
                print("tr22 : ", tr22)              
                if tr22[0].stats.npts < data_count:
                    continue 
                tr22[0].stats.distance       = dist_deg
                tr22[0].stats.backazimuth    = bazi
                tr22[0].stats["coordinates"] = {}
                tr22[0].stats["coordinates"]["latitude"]  = lat
                tr22[0].stats["coordinates"]["longitude"] = lon
                tr22[0].stats["coordinates"]["elevation"] = elv               
            except Exception as e: # If file not present, skip this station
                # print(e)
                try: # Read DP1 (H)
                    tr22 = obspy.read(prodata_directory / str(fsp[0]+"."+fsp[1]+"."+fsp[2]+".00.DP1.D.mseed"), starttime=stime, endtime=etime) # (H)
                    if tr22[0].stats.npts < data_count:
                        continue 
                except Exception as e:
                    if plot_3c:
                        continue
                    else:
                        # If there's no DPN channel (H)
                        tr22 = obspy.Trace(np.zeros(len(tr11[0].data)))
                        tr22.stats.network  = tr11[0].stats.network
                        tr22.stats.station  = tr11[0].stats.station
                        tr22.stats.location = tr11[0].stats.location 
                        tr22.stats.delta    = tr11[0].stats.delta
                        tr22.stats.starttime= tr11[0].stats.starttime
                        tr22.stats.channel  = "DPN" # (H)
                        tr22.stats.distance    = dist_deg
                        tr22.stats.backazimuth = bazi
                        tr22.stats["coordinates"] = {}
                        tr22.stats["coordinates"]["latitude"]  = lat
                        tr22.stats["coordinates"]["longitude"] = lon
                        tr22.stats["coordinates"]["elevation"] = elv
                        tr22 = obspy.Stream(traces=[tr22])
                        
            try: # Read DPE
                tr33 = obspy.read(prodata_directory / str(fsp[0]+"."+fsp[1]+"."+fsp[2]+".00.DPE.D.mseed"), starttime=stime, endtime=etime) # (H)
                if tr33[0].stats.npts < data_count:
                    continue                 
                tr33[0].stats.distance    = dist_deg
                tr33[0].stats.backazimuth = bazi
                tr33[0].stats["coordinates"] = {}
                tr33[0].stats["coordinates"]["latitude"]  = lat
                tr33[0].stats["coordinates"]["longitude"] = lon
                tr33[0].stats["coordinates"]["elevation"] = elv            
            except Exception as e:
                try: # Read DP2 (H)
                    tr33 = obspy.read(prodata_directory / str(fsp[0]+"."+fsp[1]+"."+fsp[2]+".00.DP2.D.mseed"), starttime=stime, endtime=etime) # (H)
                    if tr33[0].stats.npts < data_count:
                        continue 
                except Exception as e: # If file not present, skip this station
                    # print(e)
                    if plot_3c:
                        continue
                    else:
                        # If there's no DPE channel (H)
                        tr33 = obspy.Trace(np.zeros(len(tr11[0].data)))
                        tr33.stats.network  = tr11[0].stats.network
                        tr33.stats.station  = tr11[0].stats.station
                        tr33.stats.location = tr11[0].stats.location 
                        tr33.stats.delta    = tr11[0].stats.delta
                        tr33.stats.starttime= tr11[0].stats.starttime
                        tr33.stats.channel     = "DPE" # (H)
                        tr33.stats.distance    = dist_deg
                        tr33.stats.backazimuth = bazi
                        tr33.stats["coordinates"] = {}
                        tr33.stats["coordinates"]["latitude"]  = lat
                        tr33.stats["coordinates"]["longitude"] = lon
                        tr33.stats["coordinates"]["elevation"] = elv
                        tr33 = obspy.Stream(traces=[tr33])
                                    
            if tr22[0].stats.channel == "DPN" and tr33[0].stats.channel == "DPE": # (H)
                tr1 = tr11
                tr2 = tr22
                tr3 = tr33    
            elif tr22[0].stats.channel == "DP1" and tr33[0].stats.channel == "DP2": # (H)
                trZ12 = tr11+tr22+tr33
                try:
                    invZNE = obspy.read_inventory(resp_directory+'STXML.'+fsp[0]+"."+fsp[1]+"."+fsp[2]+"*")
                    trZNE  = trZ12.copy()._rotate_to_zne(invZNE, components=('Z12'))   # rotate to ZNE
                except Exception:
                    continue
                for tr in trZNE:
                    if tr.stats.channel.endswith('Z'):
                        tr1 = tr.copy()
                        tr1.stats.distance       = dist_deg
                        tr1.stats.backazimuth    = bazi
                        tr1.stats["coordinates"] = {}
                        tr1.stats["coordinates"]["latitude"]  = lat
                        tr1.stats["coordinates"]["longitude"] = lon
                        tr1.stats["coordinates"]["elevation"] = elv
                    elif tr.stats.channel.endswith('N'):
                        tr2 = tr.copy()
                        tr2.stats.distance       = dist_deg
                        tr2.stats.backazimuth    = bazi
                        tr2.stats["coordinates"] = {}
                        tr2.stats["coordinates"]["latitude"]  = lat
                        tr2.stats["coordinates"]["longitude"] = lon
                        tr2.stats["coordinates"]["elevation"] = elv
                    elif tr.stats.channel.endswith('E'):
                        tr3 = tr.copy()
                        tr3.stats.distance       = dist_deg
                        tr3.stats.backazimuth    = bazi
                        tr3.stats["coordinates"] = {}
                        tr3.stats["coordinates"]["latitude"]  = lat
                        tr3.stats["coordinates"]["longitude"] = lon
                        tr3.stats["coordinates"]["elevation"] = elv
                Z12_count += 1 
            else:
                continue
                
        # Read all OBS channels
        elif file.endswith('CHZ'):
            if not read_obs: # If False, don't read OBS stations
                continue 
            
            fsp = file.split(".")
            try:
                file_ch = fsp[0]+"."+fsp[1]+"."+fsp[2]+".CH*"
                ch      = obspy.read(prodata_directory+file_ch, starttime=stime, endtime=etime) # read as a stream
                print(ch)
                inv_sta = obspy.read_inventory(resp_directory+'STXML.'+file_ch)   # read all channel inventory
                ch_zne  = ch.copy()._rotate_to_zne(inv_sta, components=('Z12'))   # rotate to ZNE
                
                # Read station location
                lat = inv_sta[0][0].latitude
                lon = inv_sta[0][0].longitude
                elv = inv_sta[0][0].elevation /1000. # in km
                dist, azi, bazi = gps2dist_azimuth(lat_event, lon_event, lat, lon)
                dist_deg        = kilometers2degrees(dist/1000.) # in km
                
                # Assign rotated channels back to separate trace
                for tr in ch_zne:
                    if tr.stats.channel.endswith('Z'):
                        tr1 = tr.copy()
                        tr1.stats.channel  = "CHZ"
                        tr1.stats["coordinates"] = {}
                        tr1.stats["coordinates"]["latitude"]  = lat
                        tr1.stats["coordinates"]["longitude"] = lon
                        tr1.stats["coordinates"]["elevation"] = elv
                    elif tr.stats.channel.endswith('N'):
                        tr2 = tr.copy()
                        tr2.stats.channel  = "CHN"
                        tr2.stats["coordinates"] = {}
                        tr2.stats["coordinates"]["latitude"]  = lat
                        tr2.stats["coordinates"]["longitude"] = lon
                        tr2.stats["coordinates"]["elevation"] = elv
                    elif tr.stats.channel.endswith('E'):
                        tr3 = tr.copy()
                        tr3.stats.channel  = "CHE"
                        tr3.stats["coordinates"] = {}
                        tr3.stats["coordinates"]["latitude"]  = lat
                        tr3.stats["coordinates"]["longitude"] = lon
                        tr3.stats["coordinates"]["elevation"] = elv
                        
                obs += 1 # Count obs stations
                    
            except Exception: # If file not present, skip this station
                continue
        
        else:
            continue

            
        # Array list
        arraydic = {}
        arraydic["net_sta"]  = fsp[0]
        arraydic["name_sta"] = fsp[2] # (H)
        arraydic["lat_sta"]  = lat
        arraydic["lon_sta"]  = lon
        arraydic["elv_sta"]  = elv
        arraydic["dist_sta"] = dist_deg
        arraydic["bazi_sta"] = bazi
        arraydic["azi_sta"]  = azi
        arraydic["tr"]       = tr1
        arraydic["tr_N"]     = tr2
        arraydic["tr_E"]     = tr3
        data_dict_list.append(arraydic)
            
    # Show number of OBS
    if obs != 0:
        print ('Read ' + str(obs)+ ' OBS stations.')
    if Z12_count != 0:
        print ('Read ' + str(Z12_count)+ ' Z12 stations.')
    # Sort the array list by distance
    print ('Sorting the list of dictionaries according to distance in degree...')
    data_dict_list.sort(key=itemgetter('dist_sta'))
    
    for i in range(len(data_dict_list)):
        # Store data in arrays
        st1 += data_dict_list[i]["tr"]
        st2 += data_dict_list[i]["tr_N"]
        st3 += data_dict_list[i]["tr_E"]
        lat_sta  = np.append(lat_sta,  data_dict_list[i]["lat_sta"])
        lon_sta  = np.append(lon_sta,  data_dict_list[i]["lon_sta"])
        elv_sta  = np.append(elv_sta,  data_dict_list[i]["elv_sta"])
        dist_sta = np.append(dist_sta, data_dict_list[i]["dist_sta"])
        bazi_sta = np.append(bazi_sta, data_dict_list[i]["bazi_sta"])
        azi_sta  = np.append(azi_sta,  data_dict_list[i]["azi_sta"])
        net_sta  = np.append(net_sta,  data_dict_list[i]["net_sta"])
        name_sta = np.append(name_sta, data_dict_list[i]["name_sta"])

    # Storing raw data
    print ('Storing raw data...')
    data_inv_dic = {}
    # inv
    data_inv_dic["net_sta"]  = net_sta
    data_inv_dic["name_sta"] = name_sta
    data_inv_dic["lat_sta"]  = lat_sta
    data_inv_dic["lon_sta"]  = lon_sta
    data_inv_dic["elv_sta"]  = elv_sta
    data_inv_dic["dist_sta"] = dist_sta
    data_inv_dic["bazi_sta"] = bazi_sta
    data_inv_dic["azi_sta"]  = azi_sta
    # streams
    data_inv_dic["st"]   = st1
    data_inv_dic["st_N"] = st2
    data_inv_dic["st_E"] = st3
    
    return data_inv_dic

def normalize(data_inv_dic, event_dic, f1, f2, start, end, ftype="bandpass", f=None, decimate_fc=2, threshold=None, plot_Xsec=False, plot_ZeroX=False): 
    """
    Filter and normalize streams for one single event
    
    :param data_inv_dic: data and inventory dictionary
    :param event_dic: event dictionary
    :param f1: lower frequency
    :param f2: higher frequency
    :param start: start time of the stream
    :param end: end time of the stream
    :param plot_Xsec: option for plotting cross-sections
    :return: dictionary of processed data and dictionary of stream info
    """
    gmv1 = np.array([]) # Z
    gmv2 = np.array([]) # N
    gmv3 = np.array([]) # E
    gmv4 = np.array([]) # R
    gmv5 = np.array([]) # T
    tr1_std = np.array([])
    tr2_std = np.array([])
    tr3_std = np.array([])
    
    st1 = data_inv_dic["st"]
    st2 = data_inv_dic["st_N"]
    st3 = data_inv_dic["st_E"]
    lat_sta  = data_inv_dic["lat_sta"]
    lon_sta  = data_inv_dic["lon_sta"]
    name_sta = data_inv_dic["name_sta"]
    dist_sta = data_inv_dic["dist_sta"]
    bazi_sta = data_inv_dic["bazi_sta"]
    azi_sta  = data_inv_dic["azi_sta"]
    region   = event_dic['region']
    time_event_sec   = event_dic['time_sec']
    mag = event_dic['mag']
    
    # Starting and ending time after OT
    if  type(start) is obspy.core.utcdatetime.UTCDateTime and type(end) is obspy.core.utcdatetime.UTCDateTime:
        starttime = start
        endtime   = end
    else:
        starttime = obspy.UTCDateTime(time_event_sec + start) 
        endtime   = obspy.UTCDateTime(time_event_sec + end)
    
    # Filter and downsample streams
    print ('Filtering between %.2f s and %.2f s...' % (1/f2, 1/f1))
    st_all_raw = st1+st2+st3

    st_all_f = filter_streams(st_all_raw, f1, f2, f=f, ftype=ftype)

    
    print ('Trimming traces from '+str(start)+'s to '+str(end)+'s...')
    # Trim the filtered traces
    try:
        st_all_f.interpolate(sampling_rate=st_all_f[0].stats.sampling_rate, starttime=starttime)
        print('Traces are interpoated.')
    except Exception as e:
        print(e)
        
    st_all = st_all_f.trim(starttime, endtime, pad=True, fill_value=0)
    # Downsample data by an integer factor
    if decimate_fc:
        print("Traces will be downsampled from "+str(st_all[0].stats.sampling_rate)+"Hz to "+str(st_all[0].stats.sampling_rate/decimate_fc)+"Hz")
        st_all.decimate(decimate_fc) 
    else:
        print("Traces will NOT be downsampled.")
        st_all = st_all
    
    print(st_all)
    st   = st_all.select(channel="??Z")
    st_N = st_all.select(channel="??N")    
    st_E = st_all.select(channel="??E")

    for ttr in st:
        print(ttr.stats.sampling_rate, end="Hz, ")
    
    timestep    = st[0].stats.delta         # Sample distance in seconds (timestep)
    nt          = st[0].stats.npts          # Total number of samples
    sample_rate = st[0].stats.sampling_rate # Sampling rate in Hz
    time_st     = st[0].times()             # stream time
    
    # normalize each trace by max, abs value and store in matrix
    print ('Normalizing traces by the max, abs value...')
    for i, (tr1, tr2, tr3, bazi) in enumerate(zip(st, st_N, st_E, bazi_sta)):
        # Rotate DPN/DPE to Radial/Transverse before normalizing (H)
        if tr1.stats.station != tr2.stats.station or tr1.stats.station != tr3.stats.station or tr2.stats.station != tr3.stats.station:
            print(tr1)
            print("Not the same station")
        try:
            tr4,tr5 = rotate_ne_rt(tr2.copy().data, tr3.copy().data, bazi) # rotate N and E component to R and T
        except Exception as e:
            print(e)
            print(tr2)
            print(tr3)
            continue
#        print(tr4.shape, tr5.shape) commented by (H)
        if plot_Xsec:
            tr1_new = tr1.data/max(maxabs(tr1.data),maxabs(tr2.data),maxabs(tr3.data))
            tr2_new = tr2.data/max(maxabs(tr2.data),maxabs(tr3.data))
            tr3_new = tr3.data/max(maxabs(tr2.data),maxabs(tr3.data))        
            tr4_new = tr4/max(maxabs(tr4),maxabs(tr5))
            tr5_new = tr5/max(maxabs(tr4),maxabs(tr5))
        else:
            tr1_new = tr1.data/maxabs(tr1.data)
            tr2_new = tr2.data/max(maxabs(tr2.data),maxabs(tr3.data))
            tr3_new = tr3.data/max(maxabs(tr2.data),maxabs(tr3.data))
            tr4_new = tr4/maxabs(tr4)
            tr5_new = tr5/maxabs(tr5)
        
        tr1_std = np.append(tr1_std, tr1_new.std())
        tr2_std = np.append(tr2_std, (tr2.data/maxabs(tr2.data)).std())
        tr3_std = np.append(tr3_std, (tr3.data/maxabs(tr3.data)).std())
        
        gmv1 = np.append(gmv1, tr1_new)
        gmv2 = np.append(gmv2, tr2_new)
        gmv3 = np.append(gmv3, tr3_new)
        gmv4 = np.append(gmv4, tr4_new)
        gmv5 = np.append(gmv5, tr5_new)
    
    # Replace nans with zeros
    gmv1 = np.reshape(gmv1, (len(st),len(tr1_new.data)))
    gmv1[np.isnan(gmv1)] = 0
    gmv2 = np.reshape(gmv2, (len(st),len(tr1_new.data)))
    gmv2[np.isnan(gmv2)] = 0
    gmv3 = np.reshape(gmv3, (len(st),len(tr1_new.data)))
    gmv3[np.isnan(gmv3)] = 0
    gmv4 = np.reshape(gmv4, (len(st),len(tr1_new.data)))
    gmv4[np.isnan(gmv4)] = 0
    gmv5 = np.reshape(gmv5, (len(st),len(tr1_new.data)))
    gmv5[np.isnan(gmv5)] = 0
    
    # Remove noisy stations
    print ('Removing noisy stations...')
    
    # Remove traces with STD above a threshold # default: 0.3
    if threshold:
        threshold = threshold # set by hand
    else:
        if mag >= 7.0:
            threshold = 0.25 # default: 0.25
        else:
            threshold = 0.3  # default: 0.3
    goodstations = ((tr1_std <= threshold) & (tr2_std <= threshold) & (tr3_std <= threshold)) # Store good stations

    print(len(tr1_std) - len(goodstations), "station(s) removed")
    
    # Store good stations
    normalized_dic = {}
    normalized_dic["name_sta"] = name_sta[goodstations]
    normalized_dic["lat_sta"]  = lat_sta[goodstations]
    normalized_dic["lon_sta"]  = lon_sta[goodstations]
    normalized_dic["dist_sta"] = dist_sta[goodstations]
    normalized_dic["bazi_sta"] = bazi_sta[goodstations]
    normalized_dic["azi_sta"]  = azi_sta[goodstations]       
    # Store good streams
    normalized_dic["GMV_Z"]   = gmv1[goodstations]
    normalized_dic["GMV_N"]   = gmv2[goodstations]
    normalized_dic["GMV_E"]   = gmv3[goodstations]
    normalized_dic["GMV_R"]   = gmv4[goodstations]
    normalized_dic["GMV_T"]   = gmv5[goodstations]
    if plot_ZeroX: # Zero crossings
        print("Zero crossing data is saved.")
        gmv_ZeroX = gmv1[goodstations]
        gmv_ZeroX[abs(gmv_ZeroX)<=0.01] = 1 # only +/- 1%
        gmv_ZeroX[gmv_ZeroX!=1]         = 0 # turn off the rest
        normalized_dic["GMV_ZeroX"] = gmv_ZeroX
    
    print ('Data processing for one single event DONE!')
    print ('The total number of stations of '+region+' earthquake: '+str(len(name_sta[goodstations])))
    
    return normalized_dic, dict(start=start, end=end, timestep=timestep, nt=nt, sample_rate=sample_rate, region=region, time_st=time_st)

def station_phases(GMV, station, event_dic, model, phases):
    """
    Get single station info and arrivals
    
    :param GMV: processed data dictionary
    :param station: station name
    :param event_dic: event dictionary
    :param model: earth model
    :param phases: phases to plot on seismograms and ray path plot
    :return: dictionary of station info and arrivals
    """
    # Select a station by name
    name_sta  = GMV["name_sta"].tolist()
    dist_sta  = GMV["dist_sta"]
    lat_sta   = GMV["lat_sta"]
    lon_sta   = GMV["lon_sta"]
    bazi_sta  = GMV["bazi_sta"]
    dep_event = event_dic['depth']
    print("Reading station "+station+"...")
    try:
        sta_index = name_sta.index(station) # station index
    except ValueError:
        print("Station not found. Selecting a random station...")
        station = name_sta[int(len(name_sta)/2)] # Select a station by name
        sta_index = name_sta.index(station) # station index
    print("Getting "+station+" arrival time...")
    
    # Phases and their travel times
    model_ev  = TauPyModel(model=model) 
    arr = model_ev.get_ray_paths(source_depth_in_km=dep_event, distance_in_degree=dist_sta[sta_index],phase_list=phases)
    
    print("Station "+station+" read!")
    return dict(arr=arr, 
                sta_index=sta_index, 
                sta_name=station, 
                sta_dist=dist_sta[sta_index],
                sta_lat=lat_sta[sta_index],
                sta_lon=lon_sta[sta_index],
                sta_bazi=bazi_sta[sta_index])

def phase_marker(arr, ax, channel, start, end, timelabel="s", move=False, plot_local=False, move_label=["Sg","PcP","PKP","PKiKP","SKS"], ignore=['PPP','SKKKS','SKSP','PPPS','SSP','PKiKP']):
    """
    Plot phase marker of the selected station on seismograms
    
    :param arr: list of arrivals
    :param ax: axes to plot in. 
    :param channel: channel, "Z", "N", "E", "R", "T"
    :param start: starting time of stream
    :param end: ending time of stream
    :param move: label adjustment
    :param plot_local: label adjustment if plot local
    :param ignore: these phases will not be plotted on seismograms but on ray path plot
    """
    props = dict(boxstyle='round', facecolor='white', alpha=0.5)
    j = 1 # Rayleigh wave
    k = 1 # Love wave
    if move:
        n = 0.5
    else:
        n = 1
    repeat = []
    for i in range(len(arr)):
        phase_label = arr[i].name
        if phase_label in ignore: # Do not plot these phases
           continue
        if channel in ["Z","R","E","N"]:
            if phase_label == "4kmps": # Rayleigh wave
                phase_label = "R"+str(j)
                j+=1
            elif phase_label in ["4.4kmps","4.5kmps"]: # Skip Love wave
                continue
        elif channel in ["T"]:
            if phase_label in ["4.4kmps","4.5kmps"]: # Love wave
                 phase_label = "G"+str(k)
                 k+=1
            elif phase_label == "4kmps" or phase_label.startswith("P"): # Skip all P phases and Rayleigh wave
                continue
            # elif phase_label == "SKKS":
            #     continue
        else:
            print("Please specify the channel: Z, E, N, R or T")
            break
        phase_time = arr[i].time
        
        if timelabel == "hr":
            phase_time = phase_time/(60*60)
        elif timelabel == "min":
            phase_time = phase_time/60
        else:
            phase_time = phase_time
        if phase_time >= end or phase_time <= start:
            continue
        
        ax.axvline(x=phase_time, color="b", linewidth=0.8)
        
        # phase text label adjustment

        if timelabel == "hr":
            x_adjust = 0.005
        elif timelabel == "min":
            x_adjust = 0.2
        else:
            if plot_local:
                x_adjust = 3
            else:
                x_adjust = 12
            
        if phase_label in repeat or phase_label in move_label:
            ax.text(x=phase_time+x_adjust, y=-0.9*n, s=phase_label, color="b", fontsize=8, bbox=props) # plot label on the bottom
        else:
            ax.text(x=phase_time+x_adjust, y= 0.75*n, s=phase_label, color="b", fontsize=8, bbox=props)
        repeat.append(phase_label)