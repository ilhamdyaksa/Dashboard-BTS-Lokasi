import streamlit as st
import pandas as pd
from geopy.distance import geodesic
import folium
import streamlit_folium as sf

st.set_page_config(
    page_title="Dashboard BTS Bakti",
    page_icon="⚡",
    layout="wide"  # coba aktifkan ini
)
st.title("🔍 Cari Lokasi BTS Bakti")
st.markdown("Dashboard untuk mencari lokasi BTS terdekat")

# ... (kode lainnya)

df = pd.read_csv('sites.csv')
df = df.dropna(subset=['latitude', 'longitude'])

option = st.selectbox("Pilih Metode Pencarian", ["Longitude/Latitude", "Pilih Berdasarkan Area"])
if option == "Longitude/Latitude":
    lat = st.number_input("Latitude", format="%.6f")
    lon = st.number_input("Longitude", format="%.6f")
    if st.button("Cari"):
        df['jarak'] = df.apply(lambda row: geodesic((lat, lon), (row['latitude'], row['longitude'])).km, axis=1)
        site_terdekat = df[df['jarak'] <= 5] # Radius 5 Km
        # Kesimpulan
        st.write("**Kesimpulan:**")
        st.write(f"1. Pada lokasi ({lat}, {lon}), ditemukan site terdekat dalam radius 5 Km:")
        st.write(f" - BTS 4G: {len(site_terdekat[site_terdekat['Program'].str.contains('4G', case=False, na=False)])} site")
        st.write(f" - BTS USO: {len(site_terdekat[site_terdekat['Program'].str.contains('USO', case=False, na=False)])} site")
        st.write(f"2. Berdasarkan lokasi tersebut, ditemukan problem:")
        problem_list = ['Vandalisme', 'POWER', 'VSAT', 'BTS Site', 'Landslide', 'MW']
        for problem in problem_list:
            count = len(site_terdekat[site_terdekat['Problem Availability'].astype(str).str.contains(problem, case=False, na=False)])
            st.write(f" - Issue {problem}: {count} site")
        count_site_availability = len(site_terdekat[~site_terdekat['Problem Availability'].astype(str).str.contains('|'.join(problem_list), case=False, na=False)])
        st.write(f" - Site Availability Achieve: {count_site_availability} site")
        st.write(f"3. Berdasarkan lokasi tersebut, ditemukan problem overlapping:")
        overlap_list = ["No overlapping Issue", "K1 : Tidak Overlap", "K2 : Overlap Sebagian", "K3 : Full Overlap"]
        for overlap in overlap_list:
            count = len(site_terdekat[site_terdekat['K2-K3 Kategori'].astype(str).str.contains(overlap, case=False, na=False)])
            st.write(f" - {overlap}: {count} site")
        # Tampilkan map
        m = folium.Map(location=[lat, lon], zoom_start=12)
        folium.Marker([lat, lon], icon=folium.Icon(color='red'), popup='Lokasi Anda').add_to(m)
        for index, row in site_terdekat.iterrows():
            if '4G' in str(row['Program']):
                warna = 'blue'
            elif 'USO' in str(row['Program']):
                warna = 'green'
            else:
                warna = 'gray'
            if "No overlapping Issue" in str(row['K2-K3 Kategori']):
                warna_overlap = 'lightblue'
            elif "K1 : Tidak Overlap" in str(row['K2-K3 Kategori']):
                warna_overlap = 'yellow'
            elif "K2 : Overlap Sebagian" in str(row['K2-K3 Kategori']):
                warna_overlap = 'orange'
            elif "K3 : Full Overlap" in str(row['K2-K3 Kategori']):
                warna_overlap = 'red'
            else:
                warna_overlap = 'gray'
            folium.Marker([row['latitude'], row['longitude']], icon=folium.Icon(color=warna, icon_color=warna_overlap), popup=row['Site Name']).add_to(m)
        sf.folium_static(m, width=700, height=500)
        st.write("Site Terdekat dalam Radius 5 Km:")
        st.write(site_terdekat)
elif option == "Pilih Berdasarkan Area":
    kabupaten_list = ['Select All'] + list(df['Kabupaten'].unique())
    kabupaten = st.selectbox("Pilih Kabupaten", kabupaten_list)
    if kabupaten == 'Select All':
        desa_list = ['Select All'] + list(df['Desa'].unique())
    else:
        desa_list = ['Select All'] + list(df[df['Kabupaten'] == kabupaten]['Desa'].unique())
    desa = st.selectbox("Pilih Desa", desa_list)
    if st.button("Cari"):
        if kabupaten == 'Select All' and desa == 'Select All':
            site_terdekat = df
            area = "Semua Area"
        elif kabupaten == 'Select All':
            site_terdekat = df[df['Desa'] == desa]
            area = desa
        elif desa == 'Select All':
            site_terdekat = df[df['Kabupaten'] == kabupaten]
            area = kabupaten
        else:
            site_terdekat = df[(df['Kabupaten'] == kabupaten) & (df['Desa'] == desa)]
            area = f"{desa}, {kabupaten}"
        # Kesimpulan
        st.write("**Kesimpulan:**")
        st.write(f"1. Pada area {area}, ditemukan:")
        st.write(f" - BTS 4G: {len(site_terdekat[site_terdekat['Program'].str.contains('4G', case=False, na=False)])} site")
        st.write(f" - BTS USO: {len(site_terdekat[site_terdekat['Program'].str.contains('USO', case=False, na=False)])} site")
        st.write(f"2. Berdasarkan lokasi tersebut, ditemukan problem:")
        problem_list = ['Vandalisme', 'POWER', 'VSAT', 'BTS Site', 'Landslide', 'MW']
        for problem in problem_list:
            count = len(site_terdekat[site_terdekat['Problem Availability'].astype(str).str.contains(problem, case=False, na=False)])
            st.write(f" - Issue {problem}: {count} site")
        count_site_availability = len(site_terdekat[~site_terdekat['Problem Availability'].astype(str).str.contains('|'.join(problem_list), case=False, na=False)])
        st.write(f" - Site Availability Achieve: {count_site_availability} site")
        st.write(f"3. Berdasarkan lokasi tersebut, ditemukan problem overlapping:")
        overlap_list = ["No overlapping Issue", "K1 : Tidak Overlap", "K2 : Overlap Sebagian", "K3 : Full Overlap"]
        for overlap in overlap_list:
            count = len(site_terdekat[site_terdekat['K2-K3 Kategori'].astype(str).str.contains(overlap, case=False, na=False)])
            st.write(f" - {overlap}: {count} site")
        # Tampilkan map
        if not site_terdekat.empty:
            lat = site_terdekat.iloc[0]['latitude']
            lon = site_terdekat.iloc[0]['longitude']
            m = folium.Map(location=[lat, lon], zoom_start=12)
            for index, row in site_terdekat.iterrows():
                if '4G' in str(row['Program']):
                    warna = 'blue'
                elif 'USO' in str(row['Program']):
                    warna = 'green'
                else:
                    warna = 'gray'
                if "No overlapping Issue" in str(row['K2-K3 Kategori']):
                    warna_overlap = 'lightblue'
                elif "K1 : Tidak Overlap" in str(row['K2-K3 Kategori']):
                    warna_overlap = 'yellow'
                elif "K2 : Overlap Sebagian" in str(row['K2-K3 Kategori']):
                    warna_overlap = 'orange'
                elif "K3 : Full Overlap" in str(row['K2-K3 Kategori']):
                    warna_overlap = 'red'
                else:
                    warna_overlap = 'gray'
                folium.Marker([row['latitude'], row['longitude']], icon=folium.Icon(color=warna, icon_color=warna_overlap), popup=row['Site Name']).add_to(m)
            sf.folium_static(m, width=700, height=500)
            st.write("Site di", area)
            st.write(site_terdekat)
        else:
            st.write("Tidak ada data")