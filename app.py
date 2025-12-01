import streamlit as st
import requests
import xml.etree.ElementTree as ET
import leafmap.foliumap as leafmap
import pandas as pd

st.set_page_config(page_title="BMKG XML Viewer", layout="wide")

st.title("⛈️ BMKG XML Auto Viewer (Light Version — No GeoPandas, No Shapely)")

# Input URL XML BMKG
url = st.text_input(
    "Masukkan URL XML BMKG",
    "https://raw.githubusercontent.com/infoBMKG/data-cap/main/nowcast-cap-en.xml"
)

if st.button("Load XML"):
    try:
        # --- 1. Download file XML ---
        response = requests.get(url)
        xml_text = response.text

        # --- 2. Parse XML ---
        root = ET.fromstring(xml_text)
        ns = "{urn:oasis:names:tc:emergency:cap:1.2}"

        data = []
        polygons = []

        for info in root.findall(f".//{ns}info"):
            event = info.find(f"{ns}event").text

            for area in info.findall(f"{ns}area"):
                area_desc = area.find(f"{ns}areaDesc").text
                polygon_text = area.find(f"{ns}polygon")

                if polygon_text is None:
                    continue

                # Convert koordinat ke list (lat, lon)
                coords = []
                for p in polygon_text.text.split(" "):
                    lat, lon = map(float, p.split(","))
                    coords.append([lat, lon])

                polygons.append(coords)

                data.append({
                    "event": event,
                    "area": area_desc,
                    "points": coords
                })

        # --- 3. Tampilkan tabel ---
        df = pd.DataFrame(data)
        st.subheader("📄 Data Terdeteksi")
        st.dataframe(df)

        # --- 4. Tampilkan peta ---
        st.subheader("🗺️ Peta BMKG XML")

        m = leafmap.Map(center=[-2.5, 118], zoom=5)

        # Tambahkan polygon ke peta
        for poly in polygons:
            # Leaflet butuh format [[lat, lon], ...]
            m.add_polygon(poly, color="red")

        m.to_streamlit(height=600)

    except Exception as e:
        st.error(f"Error: {e}")
