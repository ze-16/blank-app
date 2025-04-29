import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from geopandas.tools import geocode
from geopy.geocoders import Nominatim
import pydeck as pdk

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

        #c_point_list = []

        if not Data['Local Authority'].str.contains('United Kingdom').any():
            Data['Local Authority'] = Data['Local Authority'] + ", United Kingdom"
        #Without this code, geopandas starts searching all over the world map
        #Therefore sometimes it accidentally plot uk locations elsewhere e.g in the USA
        
        for i, row in Data.iterrows():
            c_point = geocode(row['Local Authority'],  
                              user_agent = 'xyz', 
                              timeout = 10 
                              )

            if not c_point.empty:
                lt = c_point.geometry.y.values[0]
                ln = c_point.geometry.x.values[0]


                Data.at[i,'latitude'] = lt
                Data.at[i,'longitude'] = ln 
            else:
                Data.at[i,'latitude'] = np.nan
                Data.at[i,'longitude'] = np.nan

        

        with tab4:
            st.header("Plot of points on map representing traffic flows")

            Data['average_traffic'] = Data[year_cols].mean(axis=1)
            #Using the average traffic flow instead of the previously implemented per year traffic flow
            #Due to the fact that every time a new year was selected in selectbox, streamlit had to do the whole calculation again
            #Therefore to avoid performance issues, I decided to use an average instead

            traffic_min = Data['average_traffic'].min()
            traffic_max = Data['average_traffic'].max()

            def get_color(value):

                norm_value = (value - traffic_min) / (traffic_max - traffic_min)

                red = int(norm_value * 255)
                green = int((1 - norm_value) * 255)
                return [red, green, 0]


            Data['color'] = Data['average_traffic'].apply(get_color)

            lyr = pdk.Layer(
                "ScatterplotLayer",
                data=Data,
                get_position = '[longitude, latitude]',
                get_color='color',
                get_radius=600,
                pickable=True,
                auto_highlight=True,

            )

            vstate = pdk.ViewState(
                latitude=Data['latitude'].mean(),
                longitude=Data['longitude'].mean(),
                zoom=5,
                pitch=0,


            )

            r = pdk.Deck(layers=[lyr], initial_view_state=vstate,tooltip={"text": "{Local Authority}\nTraffic: {average_traffic}"})
            st.pydeck_chart(r)
            st.write("Points on map are averages of points in the dataset per Local authority across the years.")
            st.write("This is due to considerations for performance and time saving, " \
            "as inputing a new year based on choice meant re-running the code and " \
            "geopandas taking time to find the coordinates again.")
        
   




    except Exception as e:
        st.error(f"An error occurred: {e}")    
else:
    st.info("File not uploaded, upload file for analysis!")



