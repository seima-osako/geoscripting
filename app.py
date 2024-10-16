# App to visualize the SuitabilityMap
import streamlit as st
from st_on_hover_tabs import on_hover_tabs

from utils import show_map

st.set_page_config(layout="wide")

st.header("Suitability Map")
st.markdown("<style>" + open("./style.css").read() + "</style>", unsafe_allow_html=True)


with st.sidebar:
    tabs = on_hover_tabs(
        tabName=["Help", "Map", "Dataset"],
        iconName=["help", "map", "description"],
        default_choice=0,
    )
if tabs == "Help":
    st.subheader("How to Use")
    st.info(
        """
        **View Suitability Map**
        1. Select the suitability map for "Coffee", "Cacao", or "Combined".
        2. Adjust the thresholds using the sliders in the sidebar to classify areas as Unsuitable, Sub-suitable, or Suitable.

        **Select Area of Interest (AOI)**
        1. Use the drawing tools on the map to define an AOI.
        2. Click the "Extract" button to view detailed statistics for the selected AOI.

        """
    )

elif tabs == "Dataset":
    st.subheader("Table 1. Geospatial data used")
    datasets_list = """
    | Layers |	Data-Links	| Authors	| Date	| Resolution | 
    | ------ | ---------- | ------- | ----- | ---------- |
    | Slope|[NASADEM 30m](https://developers.google.com/earth-engine/datasets/catalog/NASA_NASADEM_HGT_001)| NASA | 2000-02-11 till 2000-02-222 | 30m | 
    | Landuse | [ESA WorldCover 10m v100](https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v100) | ESA | 2020-2021 | 10m |
    | Soil Texture   | [Soil texture (USDA system) at 100m](https://developers.google.com/earth-engine/datasets/catalog/OpenLandMap_SOL_SOL_TEXTURE-CLASS_USDA-TT_M_v02)| DOI | 1950-2017 | 250m |
    | Precipitation | [GPM (IMERG) v6](https://developers.google.com/earth-engine/datasets/catalog/NASA_GPM_L3_IMERG_MONTHLY_V06?hl=en) | NASA & JAXA  | 2000-06-01 to 2024-05-01 | 11132 meters  |
    | Roads | [Road network](https://gee-community-catalog.org/projects/grip/?h=ro) | GRIP global roads database | 2021-04-03 | n/a |
    | Streams | [Streams in Thailand](http://www.savgis.org/donnees-sig-2/thailand.html) | Unknown | Unknown | n/a |
    """
    st.markdown(datasets_list)

    st.subheader("Table 2. Suitability Ranking")
    with open("SuitabilityRanking.md", "r", encoding="utf-8") as file:
        markdown_content = file.read()
        st.markdown(markdown_content)
elif tabs == "Map":
    suitability_map = st.radio(
        "Suitability Map for",
        ["Coffee", "Cacao", "Combined"],
        index=2,
        horizontal=True,
    )
    with st.expander("ℹ️ Threshold Settings"):
        st.markdown(
            """
            Adjust the thresholds to classify areas as Unsuitable, Sub-suitable, or Suitable.
            - **Threshold 1:** Defines the boundary between Unsuitable and Sub-suitable areas.
            - **Threshold 2:** Defines the boundary between Sub-suitable and Suitable areas.
            """
        )
        threshold1 = st.slider(
            "Threshold1 between Unsuitable and Sub-suitable",
            min_value=2,
            max_value=60,
            value=40,
            step=1,
        )

        threshold2 = st.slider(
            "Threshold2 between Sub-suitable and Suitable",
            min_value=2,
            max_value=60,
            value=50,
            step=1,
        )

    if suitability_map == "Coffee":
        tiff_path = "data/coffee_suitability.tif"
        show_map(tiff_path, threshold1, threshold2)
    elif suitability_map == "Cacao":
        tiff_path = "data/cacao_suitability.tif"
        show_map(tiff_path, threshold1, threshold2)
    else:
        tiff_path = "data/suitability.tif"
        show_map(tiff_path, threshold1, threshold2)
