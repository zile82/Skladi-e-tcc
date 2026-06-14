import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from PIL import Image, ImageOps

st.set_page_config(page_title="Skladiste Cloud", layout="wide")

st.title("📦 Skladiste Mobile-Ready")

# Povezivanje s Google Sheets
url = "https://docs.google.com/spreadsheets/d/1AtSdX-pOFb-IaT1ACI7X7XkI4UjaMXDGvbZPMU-zxbg/edit?usp=drivesdk"
conn = st.connection("gsheets", type=GSheetsConnection)

# Učitaj podatke
df = conn.read(spreadsheet=url, ttl=0)
df = df.dropna(how="all")

# --- SIDEBAR ZA UNOS ---
st.sidebar.header("Skeniranje / Unos")
with st.sidebar.form("moja forma"):
    ean = st.sidebar.text_input("Šifra artikla (ean)")
    naziv = st.sidebar.text_input("Naziv")
    lokacija = st.sidebar.selectbox("Lokacija", ["Hala 1", "Hala 2", "Hala 3", "Hala 4", "Hala 5", "Regal A", "Regal B"])
    kolicina = st.sidebar.number_input("Količina", min_value=0, step=1)
    datum_vhoda = st.date_input("Datum_vhoda", value=None)
    
    submitted = 
st.form_submit_button("Ažuriraj stanje")
if submitted:    
    if ean :
        df_fresh = conn.read(spreadsheet=url, ttl=0)
        # priprema datuma
        datum_str = datum_vhoda.strftime("%d. %m. %Y") if datum_vhoda else ""

    if trazeni_ean in ean_kolona.values:
        maska = (ean_kolona == trazeni_ean) 
        df_fresh.loc[maska,], ['naziv', 'kolicina, 'lokacija', 'datum_vhoda']] = ['naziv', 'kolicina, 'lokacija', 'datum_str']

st.sidebar.success("Ažurirano!")                                                                                                                                                           st.sidebar.success("Ažurirano!")
    else:
                    # novi red - dodajemo datum_str pod kljuc datu_vhoda
         new_row = pd.DataFrame([{
                        "ean": ean, "naziv": naziv, "lokacija": lokacija, "kolicina": kolicina, "datum_vhoda": datum_str}])
                    df_fresh = pd.concat([df_fresh, new_row], ignore_index=True)
st.sidebar.succes("Dodano!")
                conn.update(spreadsheet=url, data=df=fresh)
                st.rerun()
            if st.sidebar.button("Ažuriraj stanje"):
    # Provjeri postoji li ean
    if ean in df['ean'].values:
        df.loc[df['ean'] == ean, ['naziv', 'lokacija', 'kolicina', 'datum_vhoda' ]] = [naziv, lokacija, kolicina, datum_vhoda]
    else:
        new_row = pd.DataFrame([{"ean": ean, "naziv": naziv, "lokacija": lokacija, "kolicina": kolicina, "datum_vhoda": datum_vhoda}])
        df_fresh = pd.concat([df_fresh, new_row], ignore_index=True)
    
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
    # Ovde smo stavili 'ean' i 'artikel' jer smo saznali da se tako zovu u tvom fajlu
    if 'ean' in df.columns and 'artikel' in df.columns:
        filtered = df[
            df['ean'].astype(str).str.contains(search, case=False, na=False) | 
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
            # 1. Uzmi skenirani kod i očisti ga
            scanned_code = str(barcode.data.decode("utf-8")).strip()
            st.success(f"✅ Skenirano: {scanned_code}")

            # 2. Pripremi kolonu iz tablice za usporedbu
            # (Provjeri zove li se kolona 'ean' ili 'skl' u Excelu i ovdje upiši točno tako)
            naziv_kolone_u_excelu = 'ean' 
            
            # Pretvaramo cijelu kolonu u tekst, mičemo .0 i prazna mjesta
            df_temp_sku = df[naziv_kolone_u_excelu].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()

            # 3. Potraži artikal
            pronadjeno = df[df_temp_ean == scanned_code]

            if not pronadjeno.empty:
                artikal = pronadjeno.iloc[0]
                st.balloons() # Mali efekt za uspjeh
                st.info(f"📦 PRONAĐENO: {artikal['naziv']} | Lokacija: {artikal['lokacija']}")
                
                # Automatski popuni polje za sidebar
                st.session_state.skenirani_ean = scanned_code
            else:
                st.error(f"❌ Artikal {scanned_code} ne postoji u tablici.")
                st.warning("Provjeri jesu li podaci u Google tablici spremljeni (File -> Save).")
            
            
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
            
            # AUTOMATSKA PRETRAGA - koristi tvoj 'ean' stubac
            result = df[df['ean'].astype(str) == barcode_data]
            
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
