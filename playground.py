
I have a pandas dataframe with a longitude and latitude column. The formatting of the coordinates in the columns are unstandardized. I will provide you all the unique formats of the columns, and I want you to create a function that converts the columns to WGS 84 decimal degrees format. Some formats might not be possible to convert. The function should account for this by returning 'Invalid format' if that is the case. Here are the formats (d is an arbitrary digit):
UNIQUE LATITUDE FORMATS:
+dd.dddd
+dd.ddddd
+dd.dddddd
+dddddddd
-dd.ddddd
-dd.dddddd
-dd.ddddddd
N dd.dddd
N dd.ddddd
N dd°dd.ddd'
Ndd.dddd
Ndd.ddddd
Ndd.dddddd
Ndddddd
Ndd° dd' dd.d"
Wddd dd' dd.dd"
Wddd dd' dd.ddd"
d.ddN
d.dddd
d.ddddd
d.dddddd
d.dddddd N
dd dd dd.dd N
dd dd' dd" N
dd dd.ddd N
dd' dd.dd"
dd.d
dd.dd
dd.ddN
dd.ddd
dd.ddd N
dd.dddd
dd.ddddd
dd.dddddd
dd.dddddd N
dd.ddddddd
dd.dddddddd
dd.ddddddddd
dd.dddddddddddd
dd.ddddddddddddd
dd.dddddddddddddd
dd.ddddddddddddddd
dd.ddddddddddddd°
dd.ddddddd°
dd.dddddd°
dd.dddddd°N
dd.ddddd°
dd.ddddd°N
dd.dddd° N
dd.dddd°N
dd.dd°N
ddd.ddd
ddd.ddddd
ddd.dddddd
ddddd
dddddd
dddddddd
dd° d' dd.dddd" N
dd° d'dd"N
dd° dd' dd" N
dd° dd' dd.d" N
dd° dd' dd.dd"
dd° dd' dd.dd" N
dd° dd'dd.dddd" N
dd° dd.ddd
dd° dd.ddd'S
dd° dd.dddd N
dd°d'dd"
dd°d'dd.dd" N
dd°dd'N
dd°dd'd" N
dd°dd'd.dd"N
dd°dd'dd"
dd°dd'dd" N
dd°dd'dd"N
dd°dd'dd.d"N
dd°dd'dd.d"S
dd°dd'dd.dd"N
dd°dd'dd.ddd"
dd°dd'ddd"N
dd°dd.ddd
d°dd'dd.d"S
d°dd.ddd'N


UNIQUE LONGITUDE FORMATS
'+d.dddd
+d.dddd
+d.dddddd
+dd.dddd
+dd.ddddd
+dd.dddddd
+ddd.dd
+ddd.ddd
+ddd.dddd
+ddd.ddddd
+ddd.dddddd
-d.dd
-d.dddd
-d.ddddd
-d.dddddd
-d.ddddddddddddddd
-d.ddddddd°
-d.dddddd°
-d.ddddd°
-dd.ddd
-dd.dddd
-dd.ddddd
-dd.dddddd
-dd.ddddddd
-dd.dddddddd
-dd.ddddddddddddd
-dd.dddddddddddddd
-dd.ddddddddddddddd
-dd.dddddd°
-dd.dddddd°E
-dd.dddddd°W
-dd.ddddd°W
-dd.dd°W
-ddd.dddd
-ddd.ddddd
-ddd.dddddd
-ddd.ddddddd
-ddd.dddddddd
-ddd.dddddd°
-dddddd
-dddddddd
E d.dddddd
E dd.ddddd
E dd°dd.ddd'
Ed.ddddd
Ed.dddddd
Edd.ddddd
Edd.dddddd
Eddddddd
Nddd dd' dd.dd"
Nddd dd' dd.ddd"
Ndd° dd' dd.dddd" W
Wdd.dddd
Wdd.ddddd
Wdd° dd' dd.d"
d.dd
d.ddd
d.dddd
d.ddddd
d.dddddd
d.ddddddddd
d.dddddddddddddd
d.ddddddddddddddd
d.ddddddd°
d.dddddd°
d.dddd°W
dd dd dd.d W
dd dd' dd" E
dd dd.ddd E
dd' dd.dd"
dd' dd.ddd"
dd.dd
dd.ddW
dd.ddd
dd.ddd W
dd.dddd
dd.ddddd
dd.dddddd
dd.dddddd E
dd.dddddddd
dd.dddddddddddd
dd.ddddddddddddd
dd.dddddddddddd°
dd.dddddd°
dd.ddddd°
dd.ddddd°E
dd.ddddd°W
dd.dddd° E
dd.dddd°E
dd.dddd°W
dd.ddd°E
ddd dd dd.dd W
ddd.ddW
ddd.ddd
ddd.ddd W
ddd.dddd
ddd.ddddd
ddd.dddddd
ddd.ddddddd
ddd.dddd°E
dddddd
ddddddd
dddddddd
ddd° dd' dd.dd"
ddd°dd'W
ddd°dd'dd.d"E
ddd°dd.ddd
ddd°dd.ddd'W
dd° dd' d.dddd" W
dd° dd' dd" E
dd° dd' dd.d" W
dd° dd' dd.dd"E
dd° dd' dd.dd"E.
dd° dd'd.dddd" W
dd° dd'dd" W
dd° dddddd E
dd°dd'W
dd°dd'd" W
dd°dd'd"W
dd°dd'dd"
dd°dd'dd" W
dd°dd'dd"E
dd°dd'dd.d"E
dd°dd'dd.d"W
dd°dd'dd.dd"
dd°dd'dd.dd" E
dd°dd'dd.dd" W
dd°dd'dd.dd"E
dd°dd'dd.dd"W
dd°dd'dd.ddd"
dd°dd'ddd"W
dd°dd.ddd'W
d° dd' dd.ddd" W
d°dd'dd.dd" E
d°dd'dd.dd"E
