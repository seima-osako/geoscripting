from branca.element import Template, MacroElement
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


def show_map(sample_tiff):
    with rasterio.open(sample_tiff) as src:
        data = src.read(1)
        profile = src.profile
        bounds = src.bounds

    pixel_area_km2 = 30 * 30 / 1_000_000

    def calculate_areas(arr, pixel_area_km2):
        area1 = np.count_nonzero(arr == 1) * pixel_area_km2
        area2 = np.count_nonzero(arr == 2) * pixel_area_km2
        area3 = np.count_nonzero(arr == 3) * pixel_area_km2

        return round(area1, 2), round(area2, 2), round(area3, 2)

    threshold1 = 10
    threshold2 = 30

    if threshold1 >= threshold2:
        st.sidebar.error("Warning: It shoule be Suitable < Sub-suitable < Unsuitable")
    else:
        classified = np.zeros_like(data, dtype=np.uint8)
        classified[data < threshold1] = 1  # Suitable
        classified[(data >= threshold1) & (data < threshold2)] = 2  # Sub-suitable
        classified[data >= threshold2] = 3  # Unsuitable

        area1, area2, area3 = calculate_areas(classified, pixel_area_km2)

        col_map, col_charts = st.columns([2, 1])
        with col_map:
            color_mapping = {
                1: [0, 255, 0, 255],  # Green: Suitable
                2: [255, 255, 0, 255],  # Yellow: Sub-suitable
                3: [255, 0, 0, 255],  # Red: Unsuitable
            }

            colored_classified = np.zeros(
                (classified.shape[0], classified.shape[1], 4), dtype=np.uint8
            )

            for class_value, color in color_mapping.items():
                colored_classified[classified == class_value] = color

            m = folium.Map(
                location=[
                    (bounds.bottom + bounds.top) / 2,
                    (bounds.left + bounds.right) / 2,
                ],
                zoom_start=12,
            )

            # ref. https://python-visualization.github.io/folium/latest/user_guide/raster_layers/image_overlay.html
            folium.raster_layers.ImageOverlay(
                name="Classified",
                image=colored_classified,
                bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
                opacity=0.6,
                interactive=True,
                cross_origin=False,
                zindex=1,
            ).add_to(m)

            # ref. https://www.geeksforgeeks.org/create-a-legend-on-a-folium-map-a-comprehensive-guide/
            legend_html = """
            {% macro html() %}
            <div style="
                position: fixed; 
                bottom: 50px; left: 50px; width: 150px; height: 120px; 
                z-index:9999; font-size:14px;
                background-color:white;
                opacity: 0.8;
                padding: 10px;
                border:2px solid grey;
            ">
                &nbsp;<b>Legend</b><br>
                &nbsp;<i style="background:green;width:10px;height:10px;display:inline-block;"></i>&nbsp;Suitable<br>
                &nbsp;<i style="background:yellow;width:10px;height:10px;display:inline-block;"></i>&nbsp;Sub-suitable<br>
                &nbsp;<i style="background:red;width:10px;height:10px;display:inline-block;"></i>&nbsp;Unsuitable
            </div>
            {% endmacro %}
            """

            legend = MacroElement()
            legend._template = Template(legend_html)
            m.get_root().add_child(legend)

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

            map_data = st_folium(
                m,
                height=800,
                returned_objects=["all_drawings"],
                use_container_width=True,
            )

        with col_charts:
            st.write("**Overall**")
            fig_overall = go.Figure(
                data=[
                    go.Pie(
                        labels=["Suitable", "Sub-suitable", "Unsuitable"],
                        values=[area1, area2, area3],
                        hole=0.3,
                        marker=dict(colors=["green", "yellow", "red"]),
                        hoverinfo="label+percent",
                        textinfo="value",
                        textfont_size=15,
                    )
                ]
            )
            fig_overall.update_layout(height=350)
            st.plotly_chart(fig_overall, use_container_width=True)

            st.write("**AOI**")
            fig_selected = None

            if st.button("Extract"):
                if map_data and map_data["all_drawings"]:
                    geojson = map_data["all_drawings"][-1]
                    roi_geom = shape(geojson["geometry"])

                    # Save extracted file temporarily
                    extracted_tif = tempfile.NamedTemporaryFile(
                        delete=False, suffix=".tif"
                    )
                    with rasterio.open(extracted_tif.name, "w", **profile) as dst:
                        dst.write(classified, 1)

                    with rasterio.open(extracted_tif.name) as src:
                        out_image, out_transform = rasterio.mask.mask(
                            src, [roi_geom], crop=True
                        )
                        extracted_data = out_image[0]

                        area1_roi, area2_roi, area3_roi = calculate_areas(
                            extracted_data, pixel_area_km2
                        )

                        fig_selected = go.Figure(
                            data=[
                                go.Pie(
                                    labels=["Suitable", "Sub-suitable", "Unsuitable"],
                                    values=[area1_roi, area2_roi, area3_roi],
                                    hole=0.3,
                                    marker=dict(colors=["green", "yellow", "red"]),
                                    hoverinfo="label+percent",
                                    textinfo="value",
                                    textfont_size=15,
                                )
                            ]
                        )
                        fig_selected.update_layout(height=350)
                        st.plotly_chart(fig_selected, use_container_width=True)
                else:
                    st.warning("Draw an AOI")
