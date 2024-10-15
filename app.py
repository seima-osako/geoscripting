# App to visualize the SuitabilityMap
import streamlit as st
from st_on_hover_tabs import on_hover_tabs

from utils import show_map

st.set_page_config(layout="wide")

st.header("Demo")
st.markdown("<style>" + open("./style.css").read() + "</style>", unsafe_allow_html=True)


with st.sidebar:
    tabs = on_hover_tabs(
        tabName=["Dataset", "Map"],
        iconName=["description", "map"],
        default_choice=0,
    )

if tabs == "Dataset":
    datasets_list = """
    | Layers |	Data-Links	| Authors	| Date	| Resolution | 
    | ------ | ---------- | ------- | ----- | ---------- |
    | DEM    |  [NASADEM](https://developers.google.com/earth-engine/datasets/catalog/NASA_NASADEM_HGT_001)| NASA | 2000-02-22 | 30m | 
    | Landuse | [ESA WorldCover 10m v100](https://developers.google.com/earth-engine/datasets/catalog/ESA_WorldCover_v100) | ESA | 2020-2021 | 10m |
    | Soil    | [SOIL TYP](https://developers.google.com/earth-engine/datasets/catalog/OpenLandMap_SOL_SOL_TEXTURE-CLASS_USDA-TT_M_v02)| DOI | 1950-2017 | 250m |
    | Roads | [Road network](https://gee-community-catalog.org/projects/grip/?h=ro) | GRIP global roads database | 2021-04-03 | 8km |
    | Precipitation | [Precipitation](https://developers.google.com/earth-engine/datasets/catalog/NASA_GPM_L3_IMERG_MONTHLY_V06?hl=en) | NASA & JAXA  | 2000-06-01 to 2024-05-01 | 11132 meters  |
    | Water Bodies | [Watersheds](https://data.humdata.org/dataset/thailand-water-bodies-water-courses?) | HDX | 2018-08-16 |
    """
    st.markdown(datasets_list)

elif tabs == "Map":
    suitability_map = st.radio(
        "Suitability Map for",
        ["Coffee", "Cocoa", "Combined"],
        index=0,
        horizontal=True,
    )

    threshold1 = st.number_input(
        "Threshold between Sub-suitable and Unsuitable",
        value=20,
    )
    threshold2 = st.number_input(
        "Threshold between Suitable and Sub-suitable", value=25
    )

    if suitability_map == "Coffee":
        sample_tiff = "data/coffee_suitability.tif"
        show_map(sample_tiff, threshold1, threshold2)
    elif suitability_map == "Cocoa":
        sample_tiff = "data/cacao_suitability.tif"
        show_map(sample_tiff, threshold1, threshold2)
    else:
        sample_tiff = "data/suitability.tif"
        show_map(sample_tiff, threshold1, threshold2)
