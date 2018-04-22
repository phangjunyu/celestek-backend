from lxml import etree
import pyproj
import math

x = [
'{http://schemas.planet.com/ps/v1/planet_product_metadata_geocorrected_level}topLeft',
'{http://schemas.planet.com/ps/v1/planet_product_metadata_geocorrected_level}topRight',
'{http://schemas.planet.com/ps/v1/planet_product_metadata_geocorrected_level}bottomLeft',
'{http://schemas.planet.com/ps/v1/planet_product_metadata_geocorrected_level}bottomRight'
]
xml_coordinates = []
for _,v in etree.iterparse("test_xml.xml"):
    if v.tag in x:
        lat = float(v.find('{http://schemas.planet.com/ps/v1/planet_product_metadata_geocorrected_level}latitude').text)
        long = float(v.find('{http://schemas.planet.com/ps/v1/planet_product_metadata_geocorrected_level}longitude').text)
        xml_coordinates.append((lat, long))
    elif v.tag == '{http://schemas.planet.com/ps/v1/planet_product_metadata_geocorrected_level}epsgCode':
        current_epsg = v.text

print("xml_coordinates are", xml_coordinates)
#
p1 = pyproj.Proj(init="epsg:"+current_epsg)
p2 = pyproj.Proj(init="epsg:3857")

changed = []
#in order topleft, topright, bottomright, bottomleft
for i in xml_coordinates:
    changed.append((pyproj.transform(p1, p2, i[0], i[1])))

length = math.sqrt(math.pow(changed[0][0]-changed[1][0], 2) + math.pow(changed[0][1] - changed[1][1], 2))
height = math.sqrt(math.pow(changed[1][0]-changed[2][0], 2) + math.pow(changed[1][1] - changed[2][1], 2))

STANDARD_LENGTH = 900
STANDARD_HEIGHT = 350
print(changed)
print("length is", length, "height is", height)
