import folium
from folium.plugins import Draw
from geopy import distance, Nominatim
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium
import requests
import numpy as np

st.set_page_config(layout="wide")
st.subheader("Shelter Search App")

# セッションステートの初期化
if "center_location" not in st.session_state:
    st.session_state.center_location = [35.681236, 139.767125]

if "user_markers" not in st.session_state:
    st.session_state.user_markers = []

if "route_coordinates" not in st.session_state:
    st.session_state.route_coordinates = {}

if "shelters" not in st.session_state:
    st.session_state.shelters = pd.DataFrame()


def update_shelter_markers(m):
    """
    避難所データを読み込み、中心位置から近いトップ5の避難所をマップにマーカーとして追加します。
    """
    # 避難所データの読み込みと距離計算
    df_shelter = pd.read_csv("shelter.csv")
    df_shelter["distance"] = df_shelter.apply(
        lambda row: distance.distance(
            st.session_state.center_location, [row["lat"], row["lon"]]
        ).km,
        axis=1,
    )

    # 距離が近いトップ5の避難所を取得
    top_5_shelters = df_shelter.nsmallest(5, "distance")
    st.session_state.shelters = top_5_shelters

    # トップ5の避難所を地図にマーカーとして追加
    for index, row in top_5_shelters.iterrows():
        shelter_location = [row["lat"], row["lon"]]
        folium.Marker(
            location=shelter_location,
            popup=f'Name: {row["name"]}\nAddress: {row["address"]}',
            icon=folium.Icon(color="red", icon="info-sign"),
        ).add_to(m)


def get_route(source, dest):
    """
    OSRM APIを使用して出発点と目的地の間のルートを取得し、[lat, lon] のリストを返します。
    """
    # OSRM APIは "lon,lat" の順で座標を指定
    start = "{},{}".format(source[1], source[0])
    end = "{},{}".format(dest[1], dest[0])
    url = f"http://router.project-osrm.org/route/v1/driving/{start};{end}?overview=full&geometries=geojson"

    try:
        r = requests.get(url)
        if r.status_code == 200:
            routejson = r.json()
            if routejson["routes"]:
                route_coords = routejson["routes"][0]["geometry"]["coordinates"]
                # Foliumは "lat, lon" の順を期待しているため変換
                route_latlon = [[coord[1], coord[0]] for coord in route_coords]
                return route_latlon
            else:
                return None
        else:
            st.sidebar.error(f"Route Retrieval Error: {r.status_code}")
            return None
    except Exception as e:
        st.sidebar.error(f"An error occurred while retrieving the route: {e}")
        return None


def fetch_routes():
    """
    中心地点からトップ5避難所へのルートを取得し、セッションステートに保存します。
    """
    if st.session_state.shelters.empty:
        st.sidebar.warning(
            "The shelter data has not been loaded yet. Please search for an address."
        )
        return

    st.session_state.route_coordinates = {}
    colors = ["blue", "green", "purple", "orange", "darkred"]

    for idx, row in st.session_state.shelters.iterrows():
        shelter_name = row["name"]
        shelter_location = [row["lat"], row["lon"]]
        route = get_route(st.session_state.center_location, shelter_location)
        if route:
            st.session_state.route_coordinates[shelter_name] = {
                "coordinates": route,
                "color": colors[idx % len(colors)],
            }
        else:
            st.sidebar.warning(f"Unable to retrieve the route to {shelter_name}.")


# サイドバーにアドレス検索機能とルート検索ボタンを追加
with st.sidebar:
    st.subheader("Address Search")
    address = st.text_input("Please enter the address to search:")
    search_button = st.button("Search")

    if search_button and address:
        geolocator = Nominatim(user_agent="geo_search")
        try:
            location = geolocator.geocode(address)
            if location:
                st.session_state.center_location = [
                    location.latitude,
                    location.longitude,
                ]
                st.sidebar.success(
                    f"Search Results: ({location.latitude}, {location.longitude})"
                )
                # ルート情報をクリア
                st.session_state.route_coordinates = {}
            else:
                st.sidebar.error("The specified address could not be found.")
        except Exception as e:
            st.sidebar.error(f"An error occurred: {e}")

    st.subheader("Route to Shelter")
    route_button = st.button("Search Route")

    if route_button:
        with st.spinner("Searching for route..."):
            fetch_routes()
        st.sidebar.success("Route search completed.")

# 地図の作成
m = folium.Map(location=st.session_state.center_location, zoom_start=14)

# 描画ツールの追加
draw = Draw(
    draw_options={
        "polyline": False,
        "rectangle": False,
        "polygon": False,
        "circle": False,
        "marker": True,
        "circlemarker": False,
    }
)
draw.add_to(m)

# ラスターレイヤーの追加
folium.raster_layers.TileLayer(
    tiles="https://disaportaldata.gsi.go.jp/raster/05_jisuberikeikaikuiki/{z}/{x}/{y}.png",
    fmt="image/png",
    attr="landslide",
    tms=False,
    overlay=True,
    control=True,
    opacity=0.7,
).add_to(m)

# 既存のユーザーマーカーを地図に追加
for marker in st.session_state.user_markers:
    folium.Marker(
        location=marker,
        icon=folium.Icon(color="blue", icon="info-sign"),
    ).add_to(m)

# 避難所マーカーの更新
update_shelter_markers(m)

# ルートの描画
for shelter_name, route_info in st.session_state.route_coordinates.items():
    route = route_info["coordinates"]
    color = route_info["color"]
    folium.PolyLine(
        locations=route,
        color=color,
        weight=5,
        opacity=0.8,
        popup=f"Route to {shelter_name}",
    ).add_to(m)
    # 出発点にマーカー（中心地点）
    folium.Marker(
        location=st.session_state.center_location,
        popup="出発点",
        icon=folium.Icon(color="green", icon="play"),
    ).add_to(m)
    # 目的地にマーカー（避難所）
    # folium.Marker(
    #    location=route[-1],
    #    popup=f"目的地: {shelter_name}",
    #    icon=folium.Icon(color="red", icon="info-sign"),
    # ).add_to(m)

# 地図の表示と描画オブジェクトの取得
output = st_folium(m, width=None, height=500, returned_objects=["all_drawings"])

# 新しいマーカーが追加された場合の処理
if output and output["all_drawings"]:
    # 最新の描画を取得
    last_drawing = output["all_drawings"][-1]
    geometry = last_drawing.get("geometry", {})
    if geometry.get("type") == "Point":
        coordinates = geometry.get("coordinates", [])
        if coordinates:
            # [lon, lat] から [lat, lon] に変換
            new_center = [coordinates[1], coordinates[0]]
            st.session_state.center_location = new_center
            # 新しいマーカーをユーザーマーカーに追加
            st.session_state.user_markers.append(new_center)
            # ルート情報をクリア
            st.session_state.route_coordinates = {}
            st.rerun()
