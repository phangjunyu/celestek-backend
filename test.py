from lxml import etree
import pyproj

x = [
'{http://schemas.planet.com/ps/v1/planet_product_metadata_geocorrected_level}topLeft',
'{http://schemas.planet.com/ps/v1/planet_product_metadata_geocorrected_level}topRight',
'{http://schemas.planet.com/ps/v1/planet_product_metadata_geocorrected_level}bottomLeft',
'{http://schemas.planet.com/ps/v1/planet_product_metadata_geocorrected_level}bottomRight'
]
xml_coordinates = []
for _,v in etree.iterparse("20180312_181743_101e.xml"):
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
for i in range(0, 4, 2):
    changed.append(pyproj.transform(p1, p2, xml_coordinates[i][0], xml_coordinates[i][1]))

print("height is", abs(changed[0][1] - changed[1][1]), "width is", abs(changed[0][0] - changed[1][0]))
