import streamlit as st
import requests
import xml.etree.ElementTree as ET
from shapely.geometry import Polygon
import leafmap.foliumap as leafmap
import pandas as pd

st.set_page_config(page_title="BMKG XML Viewer", layout="wide")

st.title("🌩️ BMKG XML Auto Viewer (No GeoPandas Version)")

url = st.text_input(
    "Masukkan URL XML BMKG",
    "https://raw.githubusercontent.com/infoBMKG/data-cap/main/nowcast-cap-en.xml"
)

if st.button("Load XML"):
    try:
        # Download XML
        response = requests.get(url)
        xml_text = response.text
        root = ET.fromstring(xml_text)

        # CAP namespace
        ns = "{urn:oasis:names:tc:emergency:cap:1.2}"

        polygons = []
        rows = []

        for info in root.findall(f".//{ns}info"):
            event = info.find(f"{ns}event").text

            for area in info.findall(f"{ns}area"):
                area_name = area.find(f"{ns}areaDesc").text

                polygon_text = area.find(f"{ns}polygon")
                if polygon_text is None:
                    continue

                coords = []
                for pair in polygon_text.text.split(" "):
                    lat, lon = map(float, pair.split(","))
                    coords.append((lat, lon))

                # simpan polygon
                polygons.append(coords)

                rows.append({
                    "event": event,
                    "area": area_name,
                    "polygon_points": coords
                })

        # DataFrame preview
        df = pd.DataFrame(rows)
        st.subheader("📄 Data Hasil Parsing")
        st.dataframe(df)

        # Tampilkan peta
        st.subheader("🗺️ Peta BMKG")
        m = leafmap.Map(center=[-2.5, 118], zoom=5)

        for coords in polygons:
            lat_list = [c[0] for c in coords]
            lon_list = [c[1] for c in coords]
            poly = list(zip(lat_list, lon_list))
            m.add_polygon(poly)

        m.to_streamlit(height=600)

    except Exception as e:
        st.error(f"Gagal memproses: {e}")
