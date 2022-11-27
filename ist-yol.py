import requests
import pandas as pd
from datetime import date
import streamlit as st

def update():
    today = date.today()
    today = today.strftime("%d-%m-%Y")
    
    res = requests.get("https://api.ibb.gov.tr/teas/api/open_data")
    j = res.json()
    data = []
    
    for i in range(len(pd.DataFrame(j))):    
        d = pd.DataFrame(pd.DataFrame(j).features[i]).properties
        data.append(d)
        
    tum_veriler = pd.DataFrame(data)
    gunluk_veriler = tum_veriler[tum_veriler.tarih == today]
    
    return tum_veriler, gunluk_veriler

st.header('Verileri Güncelle')
if st.button('Güncelle'):
    tum_veriler, gunluk_veriler = update()
    
st.write(gunluk_veriler)