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
# 2. Polje za pretragu
search = st.text_input("🔍 Brza pretraga:")

if search:
    # 3. Provera da li kolone postoje
    if 'sku' in df.columns and 'naziv' in df.columns:
        filtered = df[
            df['sku'].astype(str).str.contains(search, case=False, na=False) | 
            df['naziv'].astype(str).str.contains(search, case=False, na=False)
        ]
        st.write(filtered)
    else:
        # Ako se kolone ne zovu tako, Streamlit će ti ispisati šta vidi
        st.error("Greška: Kolone 'sku' i 'naziv' nisu pronađene!")
        st.write("Kolone koje su stvarno u fajlu su:", df.columns.tolist())
