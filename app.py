# App to visualize the SuitabilityMap
import streamlit as st
import streamlit_mermaid as stmd
from st_on_hover_tabs import on_hover_tabs

from utils import BASEMAPS
from utils import show_map

st.set_page_config(layout="wide")

st.header("🌲Suitability Map")
st.markdown("<style>" + open("./style.css").read() + "</style>", unsafe_allow_html=True)


with st.sidebar:
    tabs = on_hover_tabs(
        tabName=["Home", "Map", "Dataset"],
        iconName=["home", "map", "description"],
        default_choice=0,
    )
if tabs == "Home":
    st.markdown(
        """
        ### ℹ️ Quick info
        - **Title:** Suitability Mapping for new agroforestry plots of cacoa and coffee in Thailand

        - **Team name and members:**
        Spectacular_polite_caped_buffalo

            _Amina Shehzadi, Seima Osako, Gaia Bolder and Jari Bos_

        - **Challenge number:** 2

        """
    )
    st.info(
        """
        ### 📊 About the project
        ![Alt text](https://lwr.org/sites/default/files/styles/hero_image_country/public/DSC03745.JPG.jpeg?itok=rSImDUzV)
        This project was one of the available projects during the course Geoscripting and involved developing a **suitability mapping** model to identify new areas for **cacao and coffee agroforestry in Thailand**. 
        
        In this project **land use, soil texture, slope, precipitation, road and stream data** were used(see Data sources). 
        Our workflow consist of several steps (see **Figure 1**). For each the road and stream vector data, raster data were created containing for each cell in the Area of Interest(AoI) the distance to the nearest road or stream. 
        
        All raster data were standardised to the 10m resolution of the Land Use dataset. Based on found literatures, suitability scores for both cacao and coffee were established. 
        For each criteria layer, raster values were transformed according to these chosen suitability scores.
        Next, seperate suitability maps for cacao and coffee were created by summing up the suitability values of each criteria layer. 
        
        We should mention that this project focused on geoscripting, therefore **we did not apply pair-wise comparison and assigning weights**. 
        At last, suitability map for cacao and coffee together was made by combining the individual suitability maps. 
        """
    )
    code = """
    flowchart TD
        %% Datasets
        subgraph Datasets["Data sets"]
            style Datasets fill:#D2691E
            NASADEM["NASADEM 30m"]
            SoilTYP["Soil texture (USDA system) at 100m"]
            Precipitation["GPM (IMERG) v6"]
            ESAWorldCover["ESA WorldCover 10m v100"]
            Watersheds["Thailand stream data"]
            RoadNetwork["GRIP4"]
        end
        
        %% Layers
        subgraph Layers[ ]
            style Layers fill:#228B22
            Slope["Slope (degrees)"]
            SoilTexture["Soil Texture"]
            PrecipitationLayer["Precipitation (mm/yr)"]
            LandUse["Land Use"]
            ProximityWater["Proximity to water/streams (m)"]
            ProximityRoads["Proximity to roads (m)"]
        end
        
        %% Layer Grouping Arrows
        NASADEM --> Slope
        SoilTYP --> SoilTexture
        Precipitation --> PrecipitationLayer
        ESAWorldCover --> LandUse
        Watersheds --> ProximityWater
        RoadNetwork --> ProximityRoads

        %% Analysis
        Scores["Establish Suitability Scores"]

        Slope --> Scores
        SoilTexture --> Scores
        PrecipitationLayer --> Scores
        LandUse --> Scores
        ProximityWater --> Scores
        ProximityRoads --> Scores

        NWO["Non-weighted overlay"]
        Scores--> NWO

        LSM{"Land Suitability Map (LSM)"}
        style LSM fill:#4682B4
        NWO--> LSM

        ArcMap["Visual comparison with ArcMap analysis"]
        LSM--> ArcMap
    """
    stmd.st_mermaid(code, height="500px")
    st.html(
        """
        <div align="center">
        <b>Figure 1</b> Project flowchart
        </div>
        """
    )
    st.markdown(
        """
        ### 📃References
        - Eduardo Chavez. Sanitary pruning as part of ongoing rehabilitation at a cacao farm in Guayas, Ecuador. ESPOL. https://lwr.org/blog/2021/rehabilitation-and-renovation-cocoa-agroforestry-systems.
        - Sawasawa, H. L. A. (2003). Crop yield estimation: Integrating RS, GIS, and management factors. In International Institute for Geo-information Science and Earth Observation, International Institute for Geo-information Science and Earth Observation [Thesis].) [https://webapps.itc.utwente.nl/librarywww/papers_2003/msc/nrm/sawasawa.pdf]
        - López, R. S., Fernández, D. G., López, J. O. S., Briceño, N. B. R., Oliva, M., Murga, R. E. T., Trigoso, D. I., Castillo, E. B., & Gurbillón, M. Á. B. (2020). Land Suitability for Coffee (Coffea arabica) Growing in Amazonas, Peru: Integrated Use of AHP, GIS and RS. ISPRS International Journal of Geo-Information, 9(11), 673. https://doi.org/10.3390/ijgi9110673
        - sei-Gyabaah, A. P., Antwi, M., Addo, S., & Osei, P. (2023). Land suitability analysis for cocoa (Theobroma cacao) production in the Sunyani municipality, Bono region, Ghana. Smart Agricultural Technology, 5, 100262. https://doi.org/10.1016/j.atech.2023.100262
        - Singh, K., Fuentes, I., Fidelis, C., Yinil, D., Sanderson, T., Snoeck, D., Minasny, B., & Field, D. J. (2021). Cocoa suitability mapping using multi-criteria decision making: An agile step towards soil security. Soil Security, 5, 100019. https://doi.org/10.1016/j.soisec.2021.100019
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
    with st.expander("**How to use the map**"):
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
    suitability_map = st.radio(
        "Suitability Map for",
        ["Coffee", "Cacao", "Combined"],
        index=2,
        horizontal=True,
    )
    with st.expander("**Settings**"):
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

        bs = st.radio(
            "🗺Basemap:",
            (
                "Google-Satellite-Hybrid",
                "Google-Maps",
                "Google-Terrain",
                "Esri-Satellite",
            ),
        )
        opacity = st.slider(
            "Transparency",
            min_value=0.0,
            max_value=1.0,
            value=0.6,
            step=0.1,
        )
    if suitability_map == "Coffee":
        tiff_path = "data/coffee_suitability.tif"
        show_map(tiff_path, threshold1, threshold2, bs, opacity)
    elif suitability_map == "Cacao":
        tiff_path = "data/cacao_suitability.tif"
        show_map(tiff_path, threshold1, threshold2, bs, opacity)
    else:
        tiff_path = "data/suitability.tif"
        show_map(tiff_path, threshold1, threshold2, bs, opacity)
