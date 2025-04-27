import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from geopandas.tools import geocode
from geopy.geocoders import Nominatim

uploaded_file = st.file_uploader("Choose a file", accept_multiple_files=False)


if uploaded_file is not None:
    try:
        Data = pd.read_excel(uploaded_file,sheet_name=13,header=4)
        Data = Data.drop([0, 1])
        Data.columns = Data.columns.map(str)
        Data.columns = Data.columns.str.strip()

        year_cols = [col for col in Data.columns if col.isdigit()]

        for col in year_cols:
            Data[col] = pd.to_numeric(Data[col], errors='coerce')


        Data['2009'] = Data['2009'].fillna(Data['2009'].mean())


        Data = Data.dropna()

        tab1,tab2,tab3,tab4 = st.tabs(["All time","Per year","Histogram","Geoplot"])

        with tab1:


            st.title("Boxplot for All Years Combined")

            fig, ax = plt.subplots(figsize=(14, 6))

            Data_box_all_years = Data[year_cols]


            ax.boxplot(Data_box_all_years.values, labels=year_cols, patch_artist=True)

            ax.set_xlabel('Year')
            ax.set_ylabel('Frequency')
            ax.set_title('Distribution of Frequencies for All Years (All Local Authorities)')
            ax.grid(axis='y', linestyle='--', alpha=0.7)

            st.pyplot(fig)


            st.title("Full Dataset Display")
            st.dataframe(Data)




        with tab2:
            year_selected = st.selectbox("Select Year", year_cols)


            st.title(f"Boxplot for Year {year_selected}")

            fig, ax = plt.subplots(figsize=(14, 6))

            Data_box_selected = Data[[year_selected]]  

            ax.boxplot(Data_box_selected.values, patch_artist=True)

            ax.set_xlabel('Year')
            ax.set_ylabel('Frequency')
            ax.set_title(f'Distribution of Frequencies for Year {year_selected} (All Local Authorities)')
            ax.grid(axis='y', linestyle='--', alpha=0.7)

            st.pyplot(fig)





        with tab3:

            local_authority_selected = st.selectbox("Select Local Authority", Data['Local Authority'].unique())


            filtered_data = Data[Data['Local Authority'] == local_authority_selected]


            st.title(f"Histogram for {local_authority_selected}: Frequency over Years")

            fig, ax = plt.subplots(figsize=(12, 6))
            ax.bar(year_cols, filtered_data[year_cols].values.flatten(), color='skyblue')
            ax.set_xlabel("Year")
            ax.set_ylabel("Frequency")
            ax.set_title(f"Traffic Frequency per Year for {local_authority_selected}")
            plt.xticks(rotation=45)
            st.pyplot(fig)

        c_point_list = []
        
        for i, row in Data.iterrows():
            c_point = geocode(row['Local Authority'])

            if not c_point.empty:
                lt = c_point.geometry.y.values[0]
                ln = c_point.geometry.x.values[0]
                c_point_list.append(
                    {
                        'Local Authority': row['Local Authority'],
                        'latitude': lt,
                        'longitude': ln
                    }
                )
            else:
                c_point_list.append(
                    {
                        'Local Authority': row['Local Authority'],
                        'Latitude': None,
                        'Longitude': None
                    }
                )
        

        with tab4:
            st.header("Plot of points on map representing traffic flows")
            st.map(c_point_list,zoom=1)
        
   




    except Exception as e:
        st.error(f"An error occurred: {e}")    
else:
    st.info("File not uploaded, upload file for analysis!")



