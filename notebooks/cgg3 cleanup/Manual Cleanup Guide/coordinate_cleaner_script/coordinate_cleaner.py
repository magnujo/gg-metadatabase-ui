from textwrap import dedent
import argparse
import pandas as pd
import re
import numpy as np
from sqlalchemy import create_engine
import geopandas as gpd
import matplotlib.pyplot as plt
import folium
from shapely.geometry import Point
import uuid
import os


world = gpd.read_file(os.path.join("ne_110m_admin_0_countries", "ne_110m_admin_0_countries.shp"))

def run(input_path, sheet_name, lat_col_name, lon_col_name, country_col_name, excel_output_path, map_output_path):
    try:
        cgg_df = pd.read_excel(input_path, sheet_name=sheet_name, dtype=str)
    except PermissionError as e:
        print(f"Permission error: {e}. Please close the Excel file before running this script.")
        return

    unique_string = str(uuid.uuid4())
    suf = f"_{unique_string}"

    cgg_df = cgg_df.add_suffix(suf) 

    country_col_name = f"{country_col_name}{suf}"
    lat_col_name = f"{lat_col_name}{suf}"
    lon_col_name = f"{lon_col_name}{suf}"

    # General cleaning
    cgg_df = cgg_df.map(lambda x: x.strip() if isinstance(x, str) else x)
    cgg_df = cgg_df.map(lambda x: re.sub(r'[\r\n\t]', '. ', x) if isinstance(x, str) else x)
    cgg_df = cgg_df.map(lambda x: re.sub(r' +', ' ', x) if isinstance(x, str) else x)
    none_like_values = ['None', 'none', 'NONE', 'null', 'NULL', 'Null', 'N/A', 'n/a', 'NA', 'na', 'n.a.', 'N.A.', 'n.a', 'N.A', 'nan', 'NaN', 'NaN.', 'nan.', 'nAN', 'nAn', 'nAN.', 'nAn.']
    cgg_df = cgg_df.replace(none_like_values, np.nan)
    cgg_df = cgg_df.replace(r'^\s*$', np.nan, regex=True)
    cgg_df = cgg_df.dropna(how='all', axis='columns')

    # lat lon cleaning
    cgg_df['cleaned_lon'] = (cgg_df[lon_col_name]
                            .map(lambda x: re.sub(r'\s+', ' ', x), na_action='ignore')  # Removes any consecutive whitespaces
                            .map(lambda x: x.replace(',', '.'), na_action='ignore') # Standardize decimal point
                            .map(lambda x: x.replace(u'\xa0', u' '), na_action='ignore')  # Fix  weird unicode error
                            ) 

    cgg_df['cleaned_lat'] = (cgg_df[lat_col_name]
                            .map(lambda x: re.sub(r'\s+', ' ', x), na_action='ignore')  # Removes any consecutive whitespaces
                            .map(lambda x: x.replace(',', '.'), na_action='ignore') # Standardize decimal point
                            .map(lambda x: x.replace(u'\xa0', u' '), na_action='ignore')  # Fix  weird unicode error
                            )   

    # Standardize symbols
    cgg_df['cleaned_lon'] = (cgg_df.cleaned_lon
    .map(lambda x: re.sub(r"''|”|’’|‘‘|´´|″", '"', x), na_action='ignore')  # Replaces bad second chars with "
    .map(lambda x: re.sub(r"′|’|´|‘|`", "'", x), na_action='ignore')  # Replaces bad minute chars with '
    .map(lambda x: re.sub(r"(deg)|º|˚|o", "°", x), na_action='ignore')  # Replaces bad degree chars with °
    )

    cgg_df['cleaned_lat'] = (cgg_df.cleaned_lat
    .map(lambda x: re.sub(r"''|”|’’|‘‘|´´|″", '"', x), na_action='ignore')  # Replaces bad second chars with "
    .map(lambda x: re.sub(r"′|’|´|‘", "'", x), na_action='ignore')  # Replaces bad minute chars with '
    .map(lambda x: re.sub(r"(deg)|º|˚|o", "°", x), na_action='ignore')  # Replaces bad degree chars with °
    )

    # Standardize direction symbols
    cgg_df.cleaned_lon = cgg_df.cleaned_lon.map(lambda x: re.sub(r"[Øø]", 'E', x), na_action='ignore')
    cgg_df.cleaned_lon = cgg_df.cleaned_lon.map(lambda x: re.sub(r"[Vv]", 'W', x), na_action='ignore')

    cgg_df.cleaned_lat = cgg_df.cleaned_lat.map(lambda x: re.sub(r"[Øø]", 'E', x), na_action='ignore')
    cgg_df.cleaned_lat = cgg_df.cleaned_lat.map(lambda x: re.sub(r"[Vv]", 'W', x), na_action='ignore')

    def manual_coordinate_conversion(cgg_df):
        cgg_df['lon_direction'] = (cgg_df.cleaned_lon
                                .map(lambda x: re.sub(r"[^A-Za-zÆØÅæøå\-+]", '', x), na_action='ignore')
                                .replace(np.nan, '')              
                                )
        #  Removes the direction from the cleaned_lon column, as now it is no longer needed
        cgg_df.cleaned_lon = (cgg_df.cleaned_lon
                            .map(lambda x: re.sub(r"[A-Za-zÆØÅæøå\-+]", '', x), na_action='ignore')
                            .str.strip())

        cgg_df['lat_direction'] = (cgg_df.cleaned_lat
                                .map(lambda x: re.sub(r"[^A-Za-zÆØÅæøå\-+]", '', x), na_action='ignore')
                                .replace(np.nan, '')  # This will make it easier later, when adding the direction back to the coordinate
                                )

        #  Removes the direction from the cleaned_lat column, as now it is no longer needed
        cgg_df.cleaned_lat = (cgg_df.cleaned_lat
                            .map(lambda x: re.sub(r"[A-Za-zÆØÅæøå\-+]", '', x), na_action='ignore')
                            .str.strip())

        def check_format_lon(s: str):
            dd_regex_lon = r'''^\d{1,3}(\.\d+)?(°| °)?$'''
            dm_regex_lon = r'''^\d{1,3}( |° |°)\d{1,2}(\.\d+)?('| ')?$'''
            dms_regex_lon = r'''^\d{1,3}( |° |°)\d{1,2}( |' |')\d{1,2}(\.\d+)?("| ")?$'''
            if re.match(dd_regex_lon, s):
                return 'DD'
            elif re.match(dm_regex_lon, s):
                return 'DM'
            elif re.match(dms_regex_lon, s):
                return 'DMS'
            else:
                return 'invalid format'
            
        def check_format_lat(s: str):
            dd_regex = r'''^\d{1,2}(\.\d+)?(°| °)?$'''
            dm_regex = r'''^\d{1,2}( |° |°)\d{1,2}(\.\d+)?('| ')?$'''
            dms_regex = r'''^\d{1,2}( |° |°)\d{1,2}( |' |')\d{1,2}(\.\d+)?("| ")?$'''
            if re.match(dd_regex, s):
                return 'DD'
            elif re.match(dm_regex, s):
                return 'DM'
            elif re.match(dms_regex, s):
                return 'DMS'
            else:
                return 'invalid format'

        cgg_df['lon_format'] = cgg_df.cleaned_lon.map(check_format_lon, na_action='ignore')
        cgg_df['lat_format'] = cgg_df.cleaned_lat.map(check_format_lat, na_action='ignore')
        cgg_df.cleaned_lon = cgg_df.cleaned_lon.map(lambda x: re.sub(r"\D+$", '', x), na_action='ignore')  
        cgg_df.cleaned_lat = cgg_df.cleaned_lat.map(lambda x: re.sub(r"\D+$", '', x), na_action='ignore')
        cgg_df['cleaned_lon_split'] = cgg_df.cleaned_lon.str.split(pat=r"[ °']+", regex=True)
        cgg_df['cleaned_lat_split'] = cgg_df.cleaned_lat.str.split(pat=r"[ °']+", regex=True)

        def check_leading_zeroes(x):
            if isinstance(x, list):
                for ele in x:   
                    if re.match(r'^0+\d', ele):
                        return True
                    else:
                        return False
            
            return np.nan
        cgg_df['lon_has_leading_zeroes'] = cgg_df['cleaned_lon_split'].apply(check_leading_zeroes)
        cgg_df['lat_has_leading_zeroes'] = cgg_df['cleaned_lat_split'].apply(check_leading_zeroes)


        def convert_direction_lon(row):
            direction = str(row.lon_direction)
            if direction == 'nan':
                return np.nan
            direction = re.sub(r'[EeØø]', '+', direction)
            direction = re.sub(r'[WwVv]', '-', direction)
            direction = direction.strip()
            if bool(re.match(r'^(\-|\+)$', direction)) or direction == '':
                return direction
            else:
                
                return 'invalid direction'

        def convert_direction_lat(row):
            direction = str(row.lat_direction)
            if direction == 'nan':
                return np.nan
            direction = re.sub(r'[Nn]', '+', direction)
            direction = re.sub(r'[Ss]', '-', direction)
            direction = direction.strip()
            if bool(re.match(r'^(\-|\+)$', direction)) or direction == '':
                return direction
            else:
                
                return 'invalid direction'

        cgg_df['converted_lon_direction'] = cgg_df.apply(convert_direction_lon, axis=1)
        cgg_df['converted_lat_direction'] = cgg_df.apply(convert_direction_lat, axis=1)

        def add_direction(row):
            direction = str(row.converted_lon_direction)
            coord = row.converted_lon
            if not direction == 'invalid direction':
                return float(str(direction) + str(coord))
            else:
                return np.nan

        def convert_dd(lst):
            assert len(lst) == 1
            return float(lst[0])

        def convert_dm(lst):
            assert len(lst) == 2
            degrees, minutes = float(lst[0]), float(lst[1])
            
            return degrees + (minutes/60)

        def convert_dms(lst):
            assert len(lst) == 3
            degrees, minutes, seconds = float(lst[0]), float(lst[1]), float(lst[2])
            
            return degrees + (minutes/60) + (seconds/3600)

        def convert_to_dd(row):
        
            lon_format = row.lon_format 
            split_lst = row.cleaned_lon_split
            
            if lon_format == 'DD':
                result = convert_dd(split_lst)
            elif lon_format == 'DM':
                result = convert_dm(split_lst)
            elif lon_format == 'DMS':
                result = convert_dms(split_lst)
            else:
                return np.nan
            return result
            
        cgg_df['converted_lon'] = cgg_df.apply(convert_to_dd, axis=1)
        cgg_df['converted_lon'] = cgg_df.apply(add_direction, axis=1)



        assert cgg_df.converted_lon.dropna().astype(str).apply(lambda x: bool(re.fullmatch(r'^\-?\d{1,3}\.\d*$', x))).all()

        def add_direction(row):
            direction = str(row.converted_lat_direction)
            coord = row.converted_lat
            if not direction == 'invalid direction':
                return float(str(direction) + str(coord))
            else:
                return np.nan

        def convert_dd(lst):
            assert len(lst) == 1
            return float(lst[0])

        def convert_dm(lst):
            assert len(lst) == 2
            degrees, minutes = float(lst[0]), float(lst[1])
            
            return degrees + (minutes/60)

        def convert_dms(lst):
            assert len(lst) == 3
            degrees, minutes, seconds = float(lst[0]), float(lst[1]), float(lst[2])
            
            return degrees + (minutes/60) + (seconds/3600)

        def convert_to_dd(row):
            lat_format = row.lat_format 
            split_lst = row.cleaned_lat_split
            if lat_format == 'DD':
                return convert_dd(split_lst)
            elif lat_format == 'DM':
                return convert_dm(split_lst)
            elif lat_format == 'DMS':
                return convert_dms(split_lst)
            else:
                return np.nan
            
        cgg_df['converted_lat'] = cgg_df.apply(convert_to_dd, axis=1)
        cgg_df['converted_lat'] = cgg_df.apply(add_direction, axis=1)

        assert cgg_df.converted_lat.dropna().astype(str).apply(lambda x: bool(re.fullmatch(r'^\-?\d{1,2}\.\d*$', x))).all()

        return cgg_df

    cgg_df_conv_3 = manual_coordinate_conversion(cgg_df)
    cgg_df_conv_3["coord_has_NA"] = cgg_df_conv_3["converted_lat"].isna() | cgg_df_conv_3["converted_lon"].isna()
    cgg_df_conv_3["latitude_decimal"] = cgg_df_conv_3["converted_lat"]
    cgg_df_conv_3["longitude_decimal"] = cgg_df_conv_3["converted_lon"]

    cgg_df[country_col_name] = cgg_df[country_col_name].str.strip()

    cgg_df['Country_cleaned'] = (
    cgg_df[country_col_name]
    .replace('Anartic', 'Antarctica')
    .replace('Columbia', 'Colombia')
    .replace('Great Britain', 'United Kingdom')
    .replace('North Atlantic', 'Atlantic Ocean')
    .replace('North Pole', 'Arctic Ocean')
    .replace('Island', 'Iceland')
    .replace('Outer Mongolia', 'Mongolia')
    .replace('The Netherlands', 'Netherlands')
    .replace('UK', 'United Kingdom')
    .replace('US', 'USA')
    .replace('|Denamrk', 'Denmark')
    )

    ENGINE = create_engine(
    f"postgresql://postgres:Wtcantfw36c!@dandypdb01fl:5432/smdb")
    allowed_countries = pd.read_sql('select * from uploaded_data.allowed_country_regions', con=ENGINE, dtype=str)

    mask = cgg_df.Country_cleaned.str.lower().isin(allowed_countries['name'].str.lower())
    cgg_df.Country_cleaned = cgg_df[mask].Country_cleaned
    mask = (cgg_df.Country_cleaned.isna()) & (~cgg_df[country_col_name].isna())
    cgg_df['Country_bad'] = mask

    def match_coord_to_country(cgg_df, coord_has_na_col_name, converted_lat_col_name, converted_lon_col_name):
        # ---- Spatial Join with Countries ----
        CGG_valid = cgg_df[~cgg_df[coord_has_na_col_name]].copy()
        geometry = [Point(xy) for xy in zip(CGG_valid[converted_lon_col_name], CGG_valid[converted_lat_col_name])]
        CGG_gdf = gpd.GeoDataFrame(CGG_valid, geometry=geometry, crs="EPSG:4326")
        joined = gpd.sjoin(CGG_gdf, world[["geometry", "ADMIN"]], how="left", predicate='intersects')
        cgg_df["Detected_Country"] = None
        cgg_df.loc[joined.index, "Detected_Country"] = joined["ADMIN"].values
        
        # renaming bad detected country names
        renamer = {
            'United States of America': 'USA', 
            'Republic of Serbia': 'Serbia',
            'Czechia': 'Czech Republic',
            'United Republic of Tanzania': 'Tanzania'
        }
        cgg_df['Detected_Country'] = cgg_df['Detected_Country'].replace(renamer)

        
        # ---- Country Match Classification ----
        def classify_match(row):
            if pd.isna(row["Country_cleaned"]) or pd.isna(row["Detected_Country"]):
                return "Unknown"
            return "Correct" if row["Country_cleaned"].lower() == row["Detected_Country"].lower() else "Wrong"
        cgg_df["Country_Match"] = cgg_df.apply(classify_match, axis=1)
        # ---- Static Map ----
        map_data = cgg_df[~cgg_df[coord_has_na_col_name] & cgg_df[converted_lat_col_name].between(-90, 90) & cgg_df[converted_lon_col_name].between(-180, 180)].copy()
        geometry = [Point(xy) for xy in zip(map_data[converted_lon_col_name], map_data[converted_lat_col_name])]
        map_gdf = gpd.GeoDataFrame(map_data, geometry=geometry, crs="EPSG:4326")
        fig, ax = plt.subplots(figsize=(12, 8))
        world.plot(ax=ax, color='white', edgecolor='gray')
        colors = map_gdf["Country_Match"].map({"Correct": "black", "Wrong": "red"}).fillna("gray")     
        # ---- Interactive Map ----
        m = folium.Map(zoom_start=2)
        colors = {"Correct": "black", "Wrong": "red", "Unknown": "blue"}
        for _, row in map_gdf.iterrows():
            folium.CircleMarker(
                location=(row[converted_lat_col_name], row[converted_lon_col_name]),
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

        # Save to file
        m.save(map_output_path)

        return cgg_df, m
    cgg_df_conv_3, _ = match_coord_to_country(cgg_df_conv_3, "coord_has_NA", "latitude_decimal", "longitude_decimal")
   
    cgg_df = cgg_df_conv_3.copy()
    cgg_df.converted_lon = cgg_df.longitude_decimal
    cgg_df.converted_lat = cgg_df.latitude_decimal
    cgg_df = cgg_df.drop(columns=['latitude_decimal', 'longitude_decimal'])

    cgg_df['BadColumns'] = [[]] * len(cgg_df) 

    mask = (cgg_df['converted_lon_direction'] == 'invalid direction')
    cgg_df.loc[mask, 'BadColumns'] = cgg_df.loc[mask, 'BadColumns'].apply(lambda x: x + ['Invalid Lon direction'])

    mask = (cgg_df['converted_lat_direction'] == 'invalid direction')
    cgg_df.loc[mask, 'BadColumns'] = cgg_df.loc[mask, 'BadColumns'].apply(lambda x: x + ['Invalid Lat direction'])


    mask = (cgg_df[lat_col_name].isna())
    cgg_df.loc[mask, 'BadColumns'] = cgg_df.loc[mask, 'BadColumns'].apply(lambda x: x + ['Missing Lat'])

    mask = (cgg_df['lat_format'] == 'invalid format')
    cgg_df.loc[mask, 'BadColumns'] = cgg_df.loc[mask, 'BadColumns'].apply(lambda x: x + ['Invalid Lat'])


    mask = (cgg_df['lon_format'] == 'invalid format')
    cgg_df.loc[mask, 'BadColumns'] = cgg_df.loc[mask, 'BadColumns'].apply(lambda x: x + ['Invalid Lon'])

    mask = (cgg_df[lon_col_name].isna())
    cgg_df.loc[mask, 'BadColumns'] = cgg_df.loc[mask, 'BadColumns'].apply(lambda x: x + ['Missing Lon'])

    mask = ((cgg_df.converted_lat.isna()) & (~cgg_df[lat_col_name].isna())) 
    cgg_df['InvalidLatFormat'] = mask
    mask = ((cgg_df.converted_lon.isna()) & (~cgg_df[lon_col_name].isna())) 
    cgg_df['InvalidLonFormat'] = mask
    mask = cgg_df.BadColumns.apply(lambda x: 'Invalid Lat direction' in x)
    cgg_df['InvalidLatDirection'] = mask
    mask = cgg_df.BadColumns.apply(lambda x: 'Invalid Lon direction' in x)
    cgg_df['InvalidLonDirection'] = mask

    cgg_df['converted_lon'] = cgg_df['converted_lon'].astype(float)
    cgg_df['converted_lat'] = cgg_df['converted_lat'].astype(float)
    cgg_df['lat_diffs_flag'] = (((cgg_df['converted_lat'] - cgg_df['converted_lat'].shift(1)).abs() == 1) | 
                                ((cgg_df['converted_lat'] - cgg_df['converted_lat'].shift(-1)).abs() == 1))  # Returns true if the previous or subsequent value is -1 or +1
    cgg_df['lon_diffs_flag'] = (((cgg_df['converted_lon'] - cgg_df['converted_lon'].shift(1)).abs() == 1) | 
                                ((cgg_df['converted_lon'] - cgg_df['converted_lon'].shift(-1)).abs() == 1)) 
    mask = (cgg_df["lat_diffs_flag"] == True)
    cgg_df['possible_fill_handle_error_lat'] = mask

    mask = (cgg_df["lon_diffs_flag"] == True)
    cgg_df['possible_fill_handle_error_lon'] = mask

    cgg_df_essential = cgg_df.drop(columns=['coord_has_NA', 
                                            'converted_lon_direction', 
                                            'converted_lat_direction', 
                                            'lat_has_leading_zeroes',
                                            'lon_has_leading_zeroes',
                                            'cleaned_lat_split',
                                            'cleaned_lon_split',
                                            'lat_format',
                                            'lon_format',
                                            'lat_direction',
                                            'lon_direction',
                                            'BadColumns',
                                            'lat_diffs_flag', 
                                            'lon_diffs_flag'], errors='raise')

    cgg_df_essential = cgg_df_essential.rename(columns={
        'Country_Match': 'Country_Lat_Lon_match',
        'Detected_Country': 'country_detected',
        'InvalidLatFormat': 'Lat_invalid_format',
        'InvalidLonFormat': 'Lon_invalid_format',
        'InvalidLatDirection': 'Lat_invalid_direction',
        'InvalidLonDirection': 'Lon_invalid_direction',
        'cleaned_lon': 'Lon_cleaned',
        'cleaned_lat': 'Lat_cleaned',
        'converted_lon': 'Lon_cleaned_converted',
        'converted_lat': 'Lat_cleaned_converted',
        'possible_fill_handle_error_lat': 'Lat_possible_fill_handle_error',
        'possible_fill_handle_error_lon': 'Lon_possible_fill_handle_error'}, errors='raise')
    
    
    hb = False
    for col in cgg_df_essential.columns:
        if col.endswith(suf):
            new_col_name = col[:-len(suf)]
            if new_col_name not in cgg_df_essential.columns:
                cgg_df_essential.rename(columns={col: new_col_name}, inplace=True)
            else:
                processed_col_name = f"{new_col_name}_new"
                cgg_df_essential.rename(columns={new_col_name: processed_col_name}, inplace=True)
                cgg_df_essential.rename(columns={col: new_col_name}, inplace=True)
                
                if not hb:
                    
                    print(f'''
WARNING: The script created a one or more columns with a name that already existed in the input Excel sheet. _new names of the columns that were added by this script. 
See details below:''')
                    hb = True
                
                print(f'''
Input column:  {new_col_name}
New column:     {processed_col_name}''')
                 
    
    cgg_df_essential.to_excel(excel_output_path, sheet_name='result', index=False)
    
    print()
    print('Output Excel file added to:  ', excel_output_path)
    print('Map added to:                ', map_output_path)

def main():
    parser = argparse.ArgumentParser(
    description=dedent("""
        This script processes an Excel file containing latitude, longitude, and country columns.
        
        It performs basic cleaning and standardization. Any rows with invalid data will be flagged 
        using helper columns. Definitions of these columns can be found in:
        "../Column descriptions.xlsx".
        
        For example, the script attempts to convert coordinates to decimal degrees. If it fails, the 
        row is flagged using columns like 'Lat_invalid_format' or 'Lon_invalid_format'.

        The following regex patterns are used to identify valid coordinate formats (without directions, as directions are placed in 
        a seperate column):

        Latitude formats:
            - Decimal degrees:                      ^\d{1,2}(\.\d+)?(°| °)?$
            - Degrees and decimal minutes:          ^\d{1,2}( |° |°)\d{1,2}(\.\d+)?('| ')?$
            - Degrees minutes and decimal seconds:  ^\d{1,2}( |° |°)\d{1,2}( |' |')\d{1,2}(\.\d+)?("| ")?$

        Longitude formats:
            - Decimal degrees:                      ^\d{1,3}(\.\d+)?(°| °)?$
            - Degrees and decimal minutes:          ^\d{1,3}( |° |°)\d{1,2}(\.\d+)?('| ')?$
            - Degrees minutes and decimal seconds:  ^\d{1,3}( |° |°)\d{1,2}( |' |')\d{1,2}(\.\d+)?("| ")?$

        Note:
        If helper columns already exist in the input file, the script will not overwrite them. 
        Instead, it will create new ones with a '_new' suffix.
    """),
    formatter_class=argparse.RawDescriptionHelpFormatter
)
    parser.add_argument("-i", "--input_excel_path", required=True, type=str, help="Path to input Excel file, that you want to process. IMPORTANT: Close this file before you run the script")
    parser.add_argument("-s", "--input_excel_sheet_name", type=str, default= "Data After Manual Cleaning", help="Name of the sheet in the input Excel file that you want processed. Default: Data After Manual Cleaning")
    parser.add_argument("-la", "--input_latitude_column_name", required=True, type=str, help="Name of latitude column to process")
    parser.add_argument("-lo", "--input_longitude_column_name", required=True, type=str, help="Name of longitude column to process")
    parser.add_argument("-c", "--input_country_column_name", required=True, type=str, help="Name of country column to process")

    results_folder = "results"
    excel_output_path = os.path.join(results_folder, "result.xlsx")
    map_output_path = os.path.join(results_folder, "country_match_map.html")

    args = parser.parse_args()
    run(args.input_excel_path, 
        args.input_excel_sheet_name, 
        args.input_latitude_column_name, 
        args.input_longitude_column_name, 
        args.input_country_column_name, 
        excel_output_path, map_output_path)


if __name__ == "__main__":
    main()