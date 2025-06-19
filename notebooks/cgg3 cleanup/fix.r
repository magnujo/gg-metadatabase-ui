## double check country etc
#install.packages(c("sf", "rnaturalearth", "rnaturalearthdata", "rgeoboundaries"))
#install.packages("hoardr")
#remotes::install_github("wmgeolab/rgeoboundaries")
library(dplyr)
library(sf)
library(rnaturalearth)
library(rnaturalearthdata)
library(rgeoboundaries)
library(ggplot2)
library(readr)
library(tidyverse)
library(readxl)
library(sf)
library(leaflet)
#install.packages("leaflet", dependencies = TRUE)


CGG <- read_excel("CGG_Database_Sediment_Water_231115_PSO.xlsx")

# Select specific columns from the CGG data frame
#selected_data <- CGG |> select(Country, Site, Lat, Lon, `Sample Provider`)

CGG_noNA <- CGG |> filter(!is.na(Lat))

# check for NA in either Lat or Lon, and count if presence in either
CGG_NA <- CGG |> filter(is.na(Lat))
unique(CGG_NA$Lon)

CGG_Lon_NA <- CGG |> filter(is.na(Lon))
unique(CGG_NA$Lat)



#### convert coordinates function
convert_to_decimal <- function(lat_lon, type = c("lat", "lon")) {
  type <- match.arg(type)
  
  if (is.na(lat_lon) || lat_lon == "" || lat_lon %in% c("N", "NA")) {
    return(NA)
  }
  
  lat_lon <- trimws(lat_lon)
  lat_lon_clean <- gsub("\\s+", "", lat_lon)
  
  # Decimal with optional comma
  if (grepl("^[+-]?\\d+[,\\.]\\d+$", lat_lon_clean)) {
    lat_lon_clean <- gsub(",", ".", lat_lon_clean)
    return(as.numeric(lat_lon_clean))
  }
  
  # Simple decimal
  if (grepl("^[+-]?\\d+\\.\\d+$", lat_lon_clean)) {
    return(as.numeric(lat_lon_clean))
  }
  
  # DMS as compact integer: 835647
  if (grepl("^-?\\d{6}$", lat_lon_clean)) {
    negative <- substr(lat_lon_clean, 1, 1) == "-"
    num <- abs(as.numeric(lat_lon_clean))
    degrees <- floor(num / 10000)
    minutes <- floor((num %% 10000) / 100)
    seconds <- num %% 100
    decimal <- degrees + minutes / 60 + seconds / 3600
    if (negative) decimal <- -decimal
    return(decimal)
  }
  
  # Degrees and minutes with symbols: dd°dd.dd' or ddd°dd.dd'
  if (grepl("^\\d+°\\d+[,\\.]?\\d*'?[NSEW]?$", lat_lon)) {
    parts <- regmatches(lat_lon, regexec("^(\\d+)°(\\d+[,\\.]?\\d*)'?([NSEW]?)$", lat_lon))[[1]]
    degrees <- as.numeric(parts[2])
    minutes <- as.numeric(gsub(",", ".", parts[3]))
    direction <- parts[4]
    decimal <- degrees + minutes / 60
    if ((type == "lat" && direction == "S") || (type == "lon" && direction == "W")) decimal <- -decimal
    return(decimal)
  }
  
  # DMS full with symbols: dd°dd'dd.dd" or variants
  if (grepl("^\\d+°\\d+'\\d+[,\\.]?\\d*\"?[NSEW]?$", lat_lon)) {
    parts <- regmatches(lat_lon, regexec("^(\\d+)°(\\d+)'(\\d+[,\\.]?\\d*)\"?([NSEW]?)$", lat_lon))[[1]]
    degrees <- as.numeric(parts[2])
    minutes <- as.numeric(parts[3])
    seconds <- as.numeric(gsub(",", ".", parts[4]))
    direction <- parts[5]
    decimal <- degrees + minutes / 60 + seconds / 3600
    if ((type == "lat" && direction == "S") || (type == "lon" && direction == "W")) decimal <- -decimal
    return(decimal)
  }
  
  # DMS spaced, e.g., "45 34 23.5", possibly with direction
  if (grepl("^\\d+\\s+\\d+\\s+\\d+[,\\.]?\\d*\\s?[NSEW]?$", lat_lon)) {
    parts <- unlist(strsplit(lat_lon, "\\s+"))
    degrees <- as.numeric(parts[1])
    minutes <- as.numeric(parts[2])
    seconds <- as.numeric(gsub(",", ".", parts[3]))
    direction <- ifelse(length(parts) == 4, parts[4], "")
    decimal <- degrees + minutes / 60 + seconds / 3600
    if ((type == "lat" && direction == "S") || (type == "lon" && direction == "W")) decimal <- -decimal
    return(decimal)
  }
  
  # Degrees + minutes only with ° symbol: dd°dd'
  if (grepl("^\\d+°\\d+'[NSEW]?$", lat_lon)) {
    parts <- regmatches(lat_lon, regexec("^(\\d+)°(\\d+)'([NSEW]?)$", lat_lon))[[1]]
    degrees <- as.numeric(parts[2])
    minutes <- as.numeric(parts[3])
    direction <- parts[4]
    decimal <- degrees + minutes / 60
    if ((type == "lat" && direction == "S") || (type == "lon" && direction == "W")) decimal <- -decimal
    return(decimal)
  }
  
  # Fallback integer
  if (grepl("^\\-?\\d+$", lat_lon_clean)) {
    return(as.numeric(lat_lon_clean))
  }
  
  return(NA)
}


# Apply the conversion to the Lat column
CGG_noNA$Lat2 <- sapply(CGG_noNA$Lat, convert_to_decimal)
CGG_noNA$Lon2 <- sapply(CGG_noNA$Lon, convert_to_decimal)


## lets add country, region and local area to the df

# Disable S2 geometry engine (important!)
sf::sf_use_s2(FALSE)

# Assume Lat2 and Lon2 exist and are numeric
CGG_noNA_clean <- CGG_noNA %>%
  filter(!is.na(Lat2), !is.na(Lon2)) %>%
  filter(Lat2 >= -90 & Lat2 <= 90) %>%
  filter(Lon2 >= -180 & Lon2 <= 180)


# Convert
CGG_noNA_sf <- st_as_sf(CGG_noNA_clean, coords = c("Lon2", "Lat2"), crs = 4326)
CGG_noNA_sf$Lon2 <- CGG_noNA_clean$Lon2
CGG_noNA_sf$Lat2 <- CGG_noNA_clean$Lat2

CGG_noNA_sf |> filter(is.na(geometry)) |> nrow()


# Join with countries (add Country2)
world <- ne_countries(scale = "medium", returnclass = "sf")
CGG_noNA_sf <- st_join(CGG_noNA_sf, world["name"], left = TRUE)

CGG_noNA_sf$Country2 <- CGG_noNA_sf$name

CGG_noNA_sf$correct_ountry <- CGG_noNA_sf$Country == CGG_noNA_sf$Country2

# Ensure S2 is off
sf::sf_use_s2(FALSE)

# ADM1 for Region2
adm1 <- gb_adm1()
adm1 <- st_transform(st_make_valid(adm1), st_crs(CGG_noNA_sf))
adm1 <- adm1 %>% rename(Region2 = shapeName)  # rename BEFORE the join
CGG_noNA_sf <- st_join(CGG_noNA_sf, adm1["Region2"], left = TRUE)

# ADM2 for Site2
adm2 <- gb_adm2()
adm2 <- st_transform(st_make_valid(adm2), st_crs(CGG_noNA_sf))
adm2 <- adm2 %>% rename(Site2 = shapeName)  # rename BEFORE the join
CGG_noNA_sf <- st_join(CGG_noNA_sf, adm2["Site2"], left = TRUE)

#### BEN ARBEJDE xew


df <- CGG_noNA_sf

# Clean coordinate columns (ensure numeric)
df$Lon2 <- as.numeric(df$Lon2)
df$Lat2 <- as.numeric(gsub("^\\+", "", df$Lat2))

# Filter out NA values
df_clean <- df |> filter(!is.na(Lon) & !is.na(Lat2))

# Convert to sf (assume WGS84)
df_sf <- st_as_sf(df_clean, coords = c("Lon2", "Lat2"), crs = 4326)

# Extract coordinates and add to object
coords <- st_coordinates(df_sf)
df_sf$X <- coords[, 1]
df_sf$Y <- coords[, 2]

# Filter only valid WGS84 coordinate ranges
df_sf_clean <- df_sf |> 
  filter(X >= -180 & X <= 180, Y >= -90 & Y <= 90) |>
  select(-X, -Y)  # remove temp columns if not needed

#  Load country polygons
world <- ne_countries(scale = "medium", returnclass = "sf")

#  Ensure CRS match
df_sf_clean <- st_transform(df_sf_clean, crs = st_crs(world))

# Spatial join — detect the actual country
#df_checked <- st_join(df_sf_clean, world[, c("name")])  # 'name' is the country name from naturalearth
df_checked <- df_sf_clean 
## Inspect one point manually

colnames(df_sf_clean)

#  Rename and compare
df_checked <- df_checked |> 
  rename(Detected_Country = name)

# View mismatches between original and detected country
df_mismatches <- df_checked |> 
  filter(Country != Detected_Country)


#  Add a flag for mismatch
df_checked <- df_checked |> 
  mutate(Match_Status = ifelse(Country == Detected_Country, "Match", "Mismatch"))

#  Plot world map with points
ggplot() +
  geom_sf(data = world, fill = "white", color = "gray70") +
  geom_sf(data = df_checked, aes(color = Match_Status), size = 1, alpha = 0.7) +
  scale_color_manual(values = c("Mismatch" = "red", "Match" = "black")) +
  labs(
    title = "Country Match Check for Coordinates",
    color = "Status"
  ) +
  theme_minimal() +
  theme(
    legend.position = "bottom"
  )

## lets make an interactive version


# Transform your sf object to WGS84 (required for leaflet)
df_sf_clean <- st_transform(df_sf_clean, crs = 4326)

# Build the map
leaflet_map <- leaflet(df_sf_clean) %>%
  addProviderTiles(providers$OpenStreetMap) %>%
  addCircleMarkers(
    radius = 5,
    color = "red",
    stroke = FALSE,
    fillOpacity = 0.8,
    popup = ~paste0(
      "<b>Site:</b> ", Site, "<br>",
      "<b>cgg:</b> ", cgg, "<br>",
      "<b>Age:</b> ", Age
    )
  )

# Show the map
leaflet_map