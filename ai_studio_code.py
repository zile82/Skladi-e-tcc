import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Skladiste Cloud", layout="wide")

st.title("📦 Skladiste Mobile-Ready")

# Povezivanje s Google Sheets
url = "https://docs.google.com/spreadsheets/d/1AtSdX-pOFb-IaT1ACI7X7XkI4UjaMXDGvbZPMU-zxbg/edit?usp=drivesdk"
conn = st.connection("gsheets", type=GSheetsConnection)

# Učitaj podatke
df = conn.read(spreadsheet=url, usecols=[0, 1, 2, 3])
df = df.dropna(how="all")

# --- SIDEBAR ZA UNOS ---
st.sidebar.header("Skeniranje / Unos")
sku = st.sidebar.text_input("Šifra artikla (SKU)")
naziv = st.sidebar.text_input("Naziv")
lokacija = st.sidebar.selectbox("Lokacija", ["Hala 1", "Hala 2", "Regal A", "Regal B"])
kolicina = st.sidebar.number_input("Količina", min_value=0, step=1)

if st.sidebar.button("Ažuriraj stanje"):
    # Provjeri postoji li SKU
    if sku in df['sku'].values:
        df.loc[df['sku'] == sku, ['naziv', 'lokacija', 'kolicina']] = [naziv, lokacija, kolicina]
    else:
        new_row = pd.DataFrame([{"sku": sku, "naziv": naziv, "lokacija": lokacija, "kolicina": kolicina}])
        df = pd.concat([df, new_row], ignore_index=True)
    
    # Spremi natrag u Google Sheets
    conn.update(spreadsheet=url, data=df)
    st.sidebar.success("Podaci spremljeni!")
    st.rerun()

# --- PRIKAZ ---
st.subheader("Trenutno stanje")
st.dataframe(df, use_container_width=True)
df.columns = [x.strip().lower() for x in df.columns]
# 2. Polje za pretragu - sada koristimo tvoja prava imena kolona
search = st.text_input("🔍 Brza pretraga (unesi artikal ili kod):")

if search:
    # Ovde smo stavili 'skl' i 'artikel' jer smo saznali da se tako zovu u tvom fajlu
    if 'skl' in df.columns and 'artikel' in df.columns:
        filtered = df[
            df['skl'].astype(str).str.contains(search, case=False, na=False) | 
            df['artikel'].astype(str).str.contains(search, case=False, na=False)
        ]
        st.write(f"Pronađeno rezultata: {len(filtered)}")
        st.write(filtered)
    else:
        st.error("Greška: Kolone nisu pronađene. Proveri fajl.")
