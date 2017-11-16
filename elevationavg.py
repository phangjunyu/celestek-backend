import requests
import json

#Display elevation along line, samples = 3
r = requests.get('https://maps.googleapis.com/maps/api/elevation/json?path=\
                  36.23998,-116.83171|36.23998,-114.83171&samples=3&\
                  key=AIzaSyCNyDD5upV_IYf4yVzfAmsXrOX5Z66gp_E')
#json_list = r.json()['results']
#print type(json_list)
python_dict = json.loads(r.text)
print type(python_dict)

for key in python_dict.keys:
    print key

    for j in python_dict[key].keys():
        print j
