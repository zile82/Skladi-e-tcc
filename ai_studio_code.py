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
import streamlit as st
from pyzbar.pyzbar import decode
from PIL import Image
import numpy as np

st.divider() # Linija za razdvajanje
st.subheader("📷 Skeniraj bar-kod kamerom")
st.divider()
st.subheader("📷 Skeniraj bar-kod (EAN-13)")

img_file_buffer = st.camera_input("Postavi bar-kod ispred kamere i slikaj")

if img_file_buffer is not None:
    # Učitaj sliku
    img = Image.open(img_file_buffer)
    
    # --- OBRADA SLIKE ZA BOLJE ČITANJE ---
    # 1. Pretvori u sivu boju
    gray_img = ImageOps.grayscale(img)
    # 2. Pojačaj kontrast (da bele linije budu belje, a crne crnje)
    enhanced_img = ImageOps.autocontrast(gray_img)
    
    # Pokušaj dekodiranje na obrađenoj slici
    barcodes = decode(enhanced_img)
    
    # Ako ne nađe, pokušaj na originalnoj (za svaki slučaj)
    if not barcodes:
        barcodes = decode(img)
    
    if barcodes:
        for barcode in barcodes:
            barcode_data = barcode.data.decode("utf-8")
            # Čišćenje nula sa početka ako ih Excel skrati
            clean_code = barcode_data.lstrip('0')
            
            st.success(f"✅ Prepoznat kod: {barcode_data}")
            
            # Pretraga u bazi (proveravamo i original i očišćen kod)
            result = df[
                (df['skl'].astype(str) == barcode_data) | 
                (df['skl'].astype(str) == clean_code)
            ]
            
            if not result.empty:
                st.info(f"📦 Artikal: {result['artikel'].values[0]}")
                st.metric("Količina", str(result['količina'].values[0]))
                st.metric("Lokacija", str(result['lokacija'].values[0]))
                st.dataframe(result)
            else:
                st.warning(f"Nema artikla sa kodom {barcode_data} u Excelu.")
    else:
        st.error("❌ Bar-kod nije prepoznat na slici.")
        st.info("Savet: Drži telefon mirno na oko 20cm udaljenosti. Bar-kod treba da bude horizontalan i dobro osvetljen.")
    barcodes = decode(img)
    
    if barcodes:
        for barcode in barcodes:
            # Uzimanje broja iz bar-koda
            barcode_data = barcode.data.decode("utf-8")
            st.success(f"Skeniran kod: {barcode_data}")
            
            # AUTOMATSKA PRETRAGA - koristi tvoj 'skl' stubac
            result = df[df['skl'].astype(str) == barcode_data]
            
            if not result.empty:
                st.write("### Podaci o artiklu:")
                # Prikaz podataka u lepim karticama
                c1, c2, c3 = st.columns(3)
                c1.metric("Artikal", str(result['artikel'].values[0]))
                c2.metric("Količina", str(result['količina'].values[0]))
                c3.metric("Lokacija", str(result['lokacija'].values[0]))
                
                st.dataframe(result) # Prikaz cele tabele za taj artikal
            else:
                st.warning(f"Artikal sa kodom {barcode_data} nije pronađen u bazi.")
    else:
        st.info("Pokušavam da prepoznam bar-kod... Pomeri kameru malo bliže ili dalje.")
