import streamlit as st
import requests
import xml.etree.ElementTree as ET
import geopandas as gpd
from shapely.geometry import Polygon, Point
import leafmap.foliumap as leafmap
import io

st.set_page_config(page_title="BMKG XML Viewer", layout="wide")

st.title("🌩️ BMKG XML Auto Viewer (CAP Format)")

# ===============================
# FORM INPUT URL XML BMKG
# ===============================
url = st.text_input("Masukkan URL XML BMKG", 
                    "https://raw.githubusercontent.com/infoBMKG/data-cap/main/nowcast-cap-en.xml")

if st.button("Load XML"):
    try:
        # ===============================
        # DOWNLOAD XML FILE
        # ===============================
        response = requests.get(url)
        xml_text = response.text

        # Parse XML
        root = ET.fromstring(xml_text)

        # ===============================
        # PARSE POLYGON + ATRIBUT
        # ===============================
        polygons = []
        names = []
        events = []
        areas = []

        for info in root.findall(".//{urn:oasis:names:tc:emergency:cap:1.2}info"):
            event = info.find("{urn:oasis:names:tc:emergency:cap:1.2}event").text

            for area in info.findall("{urn:oasis:names:tc:emergency:cap:1.2}area"):
                area_name = area.find("{urn:oasis:names:tc:emergency:cap:1.2}areaDesc").text

                polygon_text = area.find("{urn:oasis:names:tc:emergency:cap:1.2}polygon")
                if polygon_text is not None:
                    coords = []
                    for pair in polygon_text.text.split(" "):
                        lat, lon = map(float, pair.split(","))
                        coords.append((lon, lat))
                    
                    poly = Polygon(coords)

                    polygons.append(poly)
                    names.append(area_name)
                    events.append(event)
                    areas.append(area_name)

        # ===============================
        # CONVERT KE GEODATAFRAME
        # ===============================
        gdf = gpd.GeoDataFrame({
            "event": events,
            "area": areas,
            "location": names,
        }, geometry=polygons, crs="EPSG:4326")

        st.success("XML berhasil diproses!")

        # Tampilkan tabel
        st.subheader("📄 Data Terdeteksi")
        st.dataframe(gdf)

        # ===============================
        # TAMPILKAN PETA
        # ===============================
        st.subheader("🗺️ Peta Hasil Parsing")
        m = leafmap.Map(center=[-2.5, 118], zoom=5)
        m.add_gdf(gdf, layer_name="BMKG XML")
        m.to_streamlit(height=600)

    except Exception as e:
        st.error(f"❌ Error: {e}")
