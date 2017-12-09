# the geo json geometry object we got from geojson.io
class Filter:
	def __init__(self):
		# filter any images which are more than 10% clouds
		self.cloud_cover_filter = {
		  "type": "RangeFilter",
		  "field_name": "cloud_cover",
		  "config": {
		    "lte": 0.1
		  }
		}

	def set_date_range_filter(self, current_date, month_ago):
		# filter images acquired in a certain date range
		self.date_range_filter = {
		  "type": "DateRangeFilter",
		  "field_name": "acquired",
		  "config": {
		    "gte": month_ago,
		    "lte": current_date
		  }
		}
	def set_geo_json_geometry(self, coordinates):
		self.geo_json_geometry = {
			"type": "LineString",
		    "coordinates": coordinates
		        # "coordinates": [
		          # [
		          #   -121.92729949951172,
		          #   37.36920220581394
		          # ],
		          # [
		          #   -121.87665939331055,
		          #   37.379024258638026
		          # ]
		        # ]
		}
	def set_geometry_filter(self):
		# filter for items the overlap with our chosen geometry
		self.geometry_filter = {
		  "type": "GeometryFilter",
		  "field_name": "geometry",
		  "config": self.geo_json_geometry
		}

	def get_main_filter(self):
		return self.main_filter

	def set_main_filter(self):
		# create a filter that combines our geo and date filters
		# could also use an "OrFilter"
		self.main_filter = {
		  "type": "AndFilter",
		  "config": [self.geometry_filter, self.date_range_filter, self.cloud_cover_filter]
		}


filterClass = Filter()
