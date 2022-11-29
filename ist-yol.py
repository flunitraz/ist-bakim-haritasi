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
       
    
    tum_veriler.loc[tum_veriler["gece"] == "EVET" , "gece"] = "Gece"
    tum_veriler.loc[tum_veriler["gece"] == "HAYIR" , "gece"] = "Gündüz"
    
    gunluk_veriler = tum_veriler[tum_veriler.tarih == today]
    
    if(len(gunluk_veriler)==0):
        gunluk_veriler = tum_veriler[tum_veriler.tarih == yesterday]

    return tum_veriler, gunluk_veriler

def st_df(dataframe,d):
    df = dataframe[["ilce","isin_adi","tarih","gece"]]
    df.columns=["İlçe","İşin Adı","Tarih","Vakit"]
    
    if(d!="gunluk"):
        tarih = d.strftime("%d-%m-%Y")
        df = df[df.Tarih==tarih]
    df = df.set_index("Tarih")
    return df
    
    
    
tum_veriler, gunluk_veriler = guncelle()



ICON_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/Road_works_ahead_PW03_2_01.png/242px-Road_works_ahead_PW03_2_01.png"

icon_data = {
    "url": ICON_URL,
    "width": 242,
    "height": 242,
    "anchorY": 242,
}

gunluk_veriler["icon_data"] = None
for i in gunluk_veriler.index:
    gunluk_veriler["icon_data"][i] = icon_data


map_s={"Koyu Mod":"dark","Yol Haritası":"road","Uydu Görüntüsü":"satellite"}

tab1, tab2, tab3= st.tabs(["Son Çalışmalar", "Haritada Göster","Tüm Verileri İncele"])

with tab1:      
    st.dataframe(data=st_df(gunluk_veriler,"gunluk"), width=None, height=None, use_container_width=True)
    st.text(str(gunluk_veriler.tarih[0]) + " tarihine ait toplam " + str(len(gunluk_veriler)) +" adet yol çalışması verisi bulunmaktadır.")

with tab2:
   col1, col2 = st.columns(2)
   with col1:
       st.text("Harita Modu Seç")
   with col2: 
       s = st.selectbox("",("Koyu Mod","Yol Haritası","Uydu Görüntüsü"),label_visibility="collapsed")
   
   
   st.pydeck_chart(pdk.Deck(
       
       map_provider="mapbox",
       map_style=map_s[s],
       initial_view_state=pdk.ViewState(
           latitude=41.1,
           longitude=28.9,
           zoom=8,
           pitch=0,
           bearing=0,
       ),
       layers=[
           pdk.Layer(
               'IconLayer',
               data=gunluk_veriler,
               get_position='[lon, lat]',
               get_icon="icon_data",
               get_size=4,
               size_scale=12,
               pickable=True,
           ),
       ],
       tooltip={"text": "{isin_adi}\n{gece}"}
   ))
   
   st.text("Yukarıdaki haritada " + str(gunluk_veriler.tarih[0]) + " tarihine ait veriler gösterilmektedir.")
   
   

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.text("Tarih Seç")
    with col2:
        d = st.date_input("",label_visibility="collapsed",
                          min_value = date(2022, 10, 1),
                          max_value = date.today())
        
    if(len(st_df(tum_veriler,d))==0):
        st.text(str(d) + " tarihine ait veri bulunamadı.")
    else:
        stdf = st.dataframe(data=st_df(tum_veriler,d), width=None, height=None, use_container_width=True)
        st.text(str(d) + " tarihine ait toplam " + str(len(st_df(tum_veriler,d)))+ " adet yol çalışması verisi bulunmaktadır.")
