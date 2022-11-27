import requests
import pandas as pd
from datetime import date,timedelta
import streamlit as st
import pydeck as pdk

def guncelle():
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    today = today.strftime("%d-%m-%Y")
    yesterday = yesterday.strftime("%d-%m-%Y")
    
    res = requests.get("https://api.ibb.gov.tr/teas/api/open_data")
    j = res.json()
    data = []
    
    for i in range(len(pd.DataFrame(j))):    
        d = pd.DataFrame(pd.DataFrame(j).features[i]).properties
        data.append(d)
        
    tum_veriler = pd.DataFrame(data)
    gunluk_veriler = tum_veriler[tum_veriler.tarih == today]
    
    if(len(gunluk_veriler)==0):
        gunluk_veriler = tum_veriler[tum_veriler.tarih == yesterday]

    return tum_veriler, gunluk_veriler

st.header('Verileri Güncelle')
if st.button('Güncelle'):
    tum_veriler, gunluk_veriler = guncelle()

def yazdir(dataframe):
    df = dataframe[["ilce","isin_adi","tarih"]]
    df.columns=["İlçe","İşin Adı","Tarih"]
    return df
    
    
tum_veriler, gunluk_veriler = guncelle()
st.write(yazdir(gunluk_veriler))

st.map(gunluk_veriler[["lat","lon","tarih"]])


st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=24.76,
        longitude=-24.4,
        zoom=11,
        pitch=50,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=gunluk_veriler,
            get_position='[lon, lat]',
            get_color='[200, 30, 0, 160]',
            get_radius=200,
        ),
    ],
))
