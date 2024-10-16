import folium
from folium.plugins import Draw
import numpy as np
import plotly.graph_objects as go
import rasterio
import rasterio.mask
import streamlit as st
from streamlit_folium import st_folium
from shapely.geometry import shape
import tempfile


# Function to display the map and analyze suitability based on threshold values
def show_map(tiff_path, threshold1, threshold2):

    # Open the GeoTIFF file and read the data
    with rasterio.open(tiff_path) as src:
        data = src.read(1)
        data = np.where(data == 0, np.nan, data)
        profile = src.profile  # Get metadata of the GeoTIFF
        bounds = src.bounds  # Get spatial boundaries of the raster

    # Calculate pixel area in square kilometers (each pixel is approximately 10x10 meters)
    pixel_area_km2 = 10 * 10 / 1_000_000

    # Helper function to calculate area for each classification
    def calculate_areas(arr, pixel_area_km2):
        area1 = np.count_nonzero(arr == 1) * pixel_area_km2  # Unsuitable area
        area2 = np.count_nonzero(arr == 2) * pixel_area_km2  # Sub-suitable area
        area3 = np.count_nonzero(arr == 3) * pixel_area_km2  # Suitable area

        return round(area1, 2), round(area2, 2), round(area3, 2)

    # Ensure that thresholds are in the correct order
    if threshold1 >= threshold2:
        st.error("Warning: It should be Unsuitable < Sub-suitable < Suitable")
    else:
        # Classify the data based on the provided thresholds
        classified = np.zeros_like(data, dtype=np.uint8)
        classified[data < threshold1] = 1  # Unsuitable class
        classified[(data >= threshold1) & (data < threshold2)] = 2  # Sub-suitable class
        classified[data >= threshold2] = 3  # Suitable class

        # Calculate areas for each classification
        area1, area2, area3 = calculate_areas(classified, pixel_area_km2)

        # Layout: Split into map and chart columns
        col_map, col_charts = st.columns([2, 1])
        with col_map:

            # Define colors for each suitability class
            color_mapping = {
                1: [255, 0, 0, 255],  # Red for Unsuitable
                2: [255, 255, 0, 255],  # Yellow for Sub-suitable
                3: [0, 255, 0, 255],  # Green for Suitable
            }

            # Create a colored version of the classified data for overlay
            colored_classified = np.zeros(
                (classified.shape[0], classified.shape[1], 4), dtype=np.uint8
            )

            # Assign colors to the classified pixels
            for class_value, color in color_mapping.items():
                colored_classified[classified == class_value] = color

            # Create the map centered on the bounds of the raster
            m = folium.Map(
                location=[
                    (bounds.bottom + bounds.top) / 2,
                    (bounds.left + bounds.right) / 2,
                ],
                zoom_start=12,
            )

            # Add the classified raster as an overlay on the map
            # Reference: https://python-visualization.github.io/folium/latest/user_guide/raster_layers/image_overlay.html
            folium.raster_layers.ImageOverlay(
                name="Classified",
                image=colored_classified,
                bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
                opacity=0.6,
                interactive=True,
                cross_origin=False,
                zindex=1,
            ).add_to(m)

            # Add drawing tools to the map for selecting regions
            draw = Draw(
                draw_options={
                    "polyline": False,
                    "polygon": True,
                    "circle": False,
                    "rectangle": True,
                    "marker": False,
                    "circlemarker": False,
                },
                edit_options={"edit": False},
            )
            draw.add_to(m)

            # Display the map in the Streamlit app
            map_data = st_folium(
                m,
                height=800,
                returned_objects=["all_drawings"],
                use_container_width=True,
            )
        with col_charts:
            # Display a pie chart showing the overall suitability distribution
            st.write("**Overall Suitability Distribution**")
            fig_overall = go.Figure(
                data=[
                    go.Pie(
                        labels=["Unsuitable", "Sub-suitable", "Suitable"],
                        values=[area1, area2, area3],
                        hole=0.3,
                        marker=dict(colors=["red", "yellow", "lawngreen"]),
                        hoverinfo="label+percent",
                        textinfo="text",
                        texttemplate="%{value} km²",
                        textfont_size=14,
                    )
                ]
            )
            fig_overall.update_layout(height=350)
            st.plotly_chart(fig_overall, use_container_width=True)

            # Area of Interest (AOI) extraction section
            st.write("**AOI**")
            fig_selected = None

            # Button to extract selected area
            if st.button("Extract"):
                if map_data and map_data["all_drawings"]:
                    geojson = map_data["all_drawings"][
                        -1
                    ]  # Get the drawn shape (GeoJSON)
                    roi_geom = shape(
                        geojson["geometry"]
                    )  # Convert GeoJSON to Shapely geometry

                    # Save extracted classified data to a temporary file
                    extracted_tif = tempfile.NamedTemporaryFile(
                        delete=False, suffix=".tif"
                    )
                    with rasterio.open(extracted_tif.name, "w", **profile) as dst:
                        dst.write(classified, 1)

                    # Mask the raster with the selected geometry
                    with rasterio.open(extracted_tif.name) as src:
                        out_image, out_transform = rasterio.mask.mask(
                            src, [roi_geom], crop=True
                        )
                        extracted_data = out_image[0]  # Get the masked raster data

                        # Calculate areas for the selected region
                        area1_roi, area2_roi, area3_roi = calculate_areas(
                            extracted_data, pixel_area_km2
                        )

                        # Display pie chart for the selected region
                        fig_selected = go.Figure(
                            data=[
                                go.Pie(
                                    labels=["Unsuitable", "Sub-suitable", "Suitable"],
                                    values=[area1_roi, area2_roi, area3_roi],
                                    hole=0.3,
                                    marker=dict(colors=["red", "yellow", "lawngreen"]),
                                    hoverinfo="label+percent",
                                    textinfo="text",
                                    texttemplate="%{value} km²",
                                    textfont_size=14,
                                )
                            ]
                        )
                        fig_selected.update_layout(height=350)
                        st.plotly_chart(fig_selected, use_container_width=True)
                else:
                    st.warning("Draw an AOI")  # Warning if no shape is drawn
