# -*- coding: utf-8 -*-
"""
Web scraper for SMHI - Swedish Meterological and Hydrological Institute - data 

In the 0.2 version of this code, the script gathers data on solar radiation in
Gothenburg between set months, hard coded. To be developed.

CC 4.0 Anders Nord, Ingenjörsarbete För Klimatet
 https://ingenjorsarbeteforklimatet.se

"""

# Ladda in lite paket för att hantera dataimport och analys
import requests
import pandas as pd
import datetime as dt

# Funktion som sparar data från smhi i filen "data.csv", vilken sedan kan läsas in t ex m h a pandas csv-läsare
# Info från SMHI finns här: https://www.smhi.se/data/utforskaren-oppna-data/
def smhi_read(parameter,station_no):
    url="https://opendata-download-metobs.smhi.se/api/version/1.0/parameter/{}/station/{}/period/corrected-archive/data.csv".format(parameter,station_no)
    session = requests.Session()
    response = session.get(url)
    with open('.\src_files\data.csv', 'wb') as f:
        f.write(response.content)
    return

 # Lufttemperatur mätt en gång var tredje timme finns i parameter 1.
# Global irradians i medelvärde per timme finns i parameter 11.

# Göteborg temperatur är stationsnummer 71420.
# Göteborg sol är stationsnummer 71415.

# starta en session, anropa api på smhi med den på hemsidan nedladdade frågan och läs in
# temperatur- respektive irradiansdata via fil i source files-mappen.

# (nuvarande implementering fulhårdkodar start på data i "header" nedan, orkar inte parsea ordentligt nu)

smhi_read(1,71420)
ambient_temperature=pd.read_csv('.\src_files\data.csv', sep=";", header=11,usecols=[0,1,2])
ambient_temperature["datetime"]=ambient_temperature["Datum"] + ' ' + ambient_temperature["Tid (UTC)"]
ambient_temperature["datetime"]=pd.to_datetime(ambient_temperature["datetime"])

smhi_read(11,71415)
solar_radiation=pd.read_csv('.\src_files\data.csv', sep=";", header=7,usecols=[0,1,2])
solar_radiation["datetime"]=solar_radiation["Datum"] + ' ' + solar_radiation["Tid (UTC)"]
solar_radiation["datetime"]=pd.to_datetime(solar_radiation["datetime"])

#Välj en femårsperiod för modelleringen - här 2008-01-01 till 2013-01-01 (baserat på datatillgänglighet)
start_time="2008-4-15 00:00:00"

end_time="2008-4-17 12:00:00" #Temp för provning - kör bara några månader

#end_time="2013-1-1 00:00:00"



# Gör lite plottar och så för att visa att vi har fått tag i vad vi önskar
import matplotlib.pyplot as plt

aT=ambient_temperature[(ambient_temperature["datetime"] > start_time) & (ambient_temperature["datetime"] < end_time)]
sR=solar_radiation[(solar_radiation["datetime"] > start_time) & (solar_radiation["datetime"] < end_time)]

#Rita grafer för datan som hämtats från SMHI
plt.plot(aT["datetime"],aT["Lufttemperatur"])
plt.title('Temperaturdata från SMHI')
plt.xlabel('Tid')
plt.ylabel('T [$^{\circ}C$]')
plt.show()

plt.plot(sR["datetime"],sR["Global Irradians (svenska stationer)"])
plt.title('Global Irradians (svenska stationer)')
plt.xlabel('Tid')
plt.ylabel('$R_s$ [$W/m^2$]')
plt.show()
 