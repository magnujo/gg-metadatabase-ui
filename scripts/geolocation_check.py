import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import folium
from shapely.geometry import Point

def match_coord_to_country(input_data, geodata, lat_col_name, lon_col_name, iso3_col_name, geodata_geometry_col_name="geometry", geodata_iso_col_name="ISO_A3"):
    # ---- Spatial Join with Countries ----
    geometry = [Point(xy) for xy in zip(input_data[lon_col_name], input_data[lat_col_name])]
    input_gdf = gpd.GeoDataFrame(input_data, geometry=geometry, crs="EPSG:4326")
    joined = gpd.sjoin(input_gdf, geodata[[geodata_geometry_col_name, geodata_iso_col_name]], how="left", predicate='intersects')
    input_data["Detected_Country"] = None
    input_data.loc[joined.index, "Detected_Country"] = joined[geodata_iso_col_name].values
    
    # ---- Country Match Classification ----
    def classify_match(row):
        if pd.isna(row[iso3_col_name]) or pd.isna(row["Detected_Country"]):
            return "Unknown"
        return "Correct" if row[iso3_col_name].lower() == row["Detected_Country"].lower() else "Wrong"
    input_data["Country_Match"] = input_data.apply(classify_match, axis=1)
    # ---- Static Map ----
    map_data = input_data[input_data[lat_col_name].between(-90, 90) & input_data[lon_col_name].between(-180, 180)].copy()
    geometry = [Point(xy) for xy in zip(map_data[lon_col_name], map_data[lat_col_name])]
    map_gdf = gpd.GeoDataFrame(map_data, geometry=geometry, crs="EPSG:4326")
    fig, ax = plt.subplots(figsize=(12, 8))
    geodata.plot(ax=ax, color='white', edgecolor='gray')
    colors = map_gdf["Country_Match"].map({"Correct": "black", "Wrong": "red"}).fillna("gray")
    map_gdf.plot(ax=ax, color=colors, markersize=10)
    plt.title("Country Match: Correct vs Wrong")
    plt.show()
    # ---- Interactive Map ----
    m = folium.Map(zoom_start=2)
    colors = {"Correct": "black", "Wrong": "red", "Unknown": "blue"}
    for _, row in map_gdf.iterrows():
        folium.CircleMarker(
            location=(row[lat_col_name], row[lon_col_name]),
            radius=4,
            color=colors.get(row["Country_Match"], "gray"),
            fill=True,
            fill_opacity=0.7,
            popup=folium.Popup(f"""
            <b>Site:</b> {row.get('Site', '')}<br>
            <b>Country:</b> {row.get('Country', '')}<br>
            <b>Detected:</b> {row.get('Detected_Country', '')}<br>
            <b>Status:</b> {row.get('Country_Match', '')}
            """, max_width=250)
        ).add_to(m)
    legend_html = """
    <div style="position: fixed; bottom: 50px; left: 50px; width: 150px; background: white; border:1px solid grey; padding: 10px;">
    <b>Country Match</b><br>
    <i style="color:black">●</i> Correct<br>
    <i style="color:red">●</i> Wrong<br>
    <i style="color:blue">●</i> Unknown
    </div>"""
    m.get_root().html.add_child(folium.Element(legend_html))

    return input_data, m