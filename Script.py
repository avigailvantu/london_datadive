import json
import urllib2
import pandas as pd
import numpy as np
from dateutil import parser
import dateutil

# Relevant link
url = 'http://api.erg.kcl.ac.uk/AirQuality/Information/MonitoringSites/GroupName=London/Json'
req = urllib2.urlopen(url)
info = json.loads(req.read())

sites = {}
for i in info['Sites']['Site']:
    m = i['@SiteCode']
    sites[m] = (i['@Latitude'],i['@Longitude'],i['@SiteName'])
data_sites = pd.DataFrame(sites).T
data_sites = data_sites.reset_index()
data_sites.columns = ['Station','Latitude','Longitude','StationName']

inproximity = ['Westminster - Oxford Street',
'Westminster - Marylebone Road FDMS',
'Westminster - Marylebone Road',
'Camden - Shaftesbury Avenue',
'Westminster - Strand (Northbank BID)',
'Camden - Holborn (inmidtown)',
'Camden - Bloomsbury',
'Camden - Euston Road']

ofinterest = []
for i,l in enumerate(data_sites['StationName']):
    if l in inproximity:
        ofinterest.append(data_sites['Station'][i])

pollution = {}
for i in ofinterest:
    url = 'http://api.erg.kcl.ac.uk/AirQuality/Data/SiteSpecies/SiteCode=%s/SpeciesCode=NO2/StartDate=25Nov2006/EndDate=09Dec2006/Json'%(i)
    req = urllib2.urlopen(url)
    info_species = json.loads(req.read())
    x = pd.DataFrame(info_species['RawAQData']['Data'])
    x['@Value'] = x['@Value'].apply(lambda x: x.encode('utf-8'))
    x['@Value'] = np.where(x['@Value']=='',np.nan,x['@Value'])
    x['@Value'] = x['@Value'].astype(float)
    x['Date'] = x['@MeasurementDateGMT'].apply(lambda x: dateutil.parser.parse(x.encode('utf-8')).date())
    pollution[i] = pd.DataFrame({'Mean':x.groupby('Date',axis=0)['@Value'].mean(),
                            'Std':x.groupby('Date',axis=0)['@Value'].std()}).reset_index()
