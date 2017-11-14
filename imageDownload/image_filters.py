# the geo json geometry object we got from geojson.io
geo_json_geometry = {
	"type": "LineString",
        "coordinates": [
          [
            -121.92729949951172,
            37.36920220581394
          ],
          [
            -121.87665939331055,
            37.379024258638026
          ]
        ]
}

# filter for items the overlap with our chosen geometry
geometry_filter = {
  "type": "GeometryFilter",
  "field_name": "geometry",
  "config": geo_json_geometry
}

# filter images acquired in a certain date range
date_range_filter = {
  "type": "DateRangeFilter",
  "field_name": "acquired",
  "config": {
    "gte": "2017-10-15T00:00:00.000Z",
    "lte": "2017-11-11T00:00:00.000Z"
  }
}

# filter any images which are more than 10% clouds
cloud_cover_filter = {
  "type": "RangeFilter",
  "field_name": "cloud_cover",
  "config": {
    "lte": 0.1
  }
}

# create a filter that combines our geo and date filters
# could also use an "OrFilter"
sjc_golfcourse = {
  "type": "AndFilter",
  "config": [geometry_filter, date_range_filter, cloud_cover_filter]
}