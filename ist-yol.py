import requests
import pandas as pd
from datetime import date,timedelta
import streamlit as st
import pydeck as pdk
from geopy.geocoders import Nominatim

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
    
    
def get_directions_response(lat1, long1, lat2, long2, mode='drive'):
    url = "https://route-and-directions.p.rapidapi.com/v1/routing"
    querystring = {"waypoints": f"{str(lat1)},{str(long1)}|{str(lat2)},{str(long2)}", "mode": "drive"}
    headers = {
        "X-RapidAPI-Key": "889d5281acmsh9a8b0e8a6bdfce3p188328jsna791960c7d91",
        "X-RapidAPI-Host": "route-and-directions.p.rapidapi.com"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    return response


def rota_olustur(x,y):
   
    geolocator = Nominatim(user_agent="MyApp")    
    locationx = geolocator.geocode(x + " istanbul türkiye")
    locationy = geolocator.geocode(y + " istanbul türkiye")
    
    response = get_directions_response(locationx.latitude, locationx.longitude, locationy.latitude, locationy.longitude)    
    j = response.json()
    j = j["features"][0]["geometry"]["coordinates"]
    
    pathdf = pd.DataFrame()
    pathdf["koor"] = j
    pathdf["color"] = [(255,0,0)]
    return(pathdf)

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


st.set_page_config(
    page_title="İstanbul Bakım Haritası",
    layout="wide",
    initial_sidebar_state="expanded"
)


with st.sidebar:
    st.title("Rota Oluştur")
    x=st.text_input("Nereden",value="istanbul")
    y=st.text_input("Nereye",value="istanbul")
    pathdf=rota_olustur(x,y)
   


tab1, tab2, tab3= st.tabs(["Haritada Göster","Son Çalışmalar","Tüm Verileri İncele"])

with tab1:
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
               type="PathLayer",
               data=pathdf,
               get_color="color",
               width_scale=10,
               width_min_pixels=2,
               get_path="koor",
               get_width=5,             
               ),
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
   
   
with tab2:      
    st.dataframe(data=st_df(gunluk_veriler,"gunluk"), width=None, height=None, use_container_width=True)
    st.text(str(gunluk_veriler.tarih[0]) + " tarihine ait toplam " + str(len(gunluk_veriler)) +" adet yol çalışması verisi bulunmaktadır.")


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
        
