import requests
import json
import numpy as np

#get json .geometry of satellite image
#find distance from pixel corner to pixel tl, tr, bl, br of landing spot
#find ratio of pixel distance over total length/width
#use json .geometry corner and ratio to find location of tl, tr, bl, br

#Input: Bounding box corners (converted to long/lat)
#Process: Choose interval, divide tl-to-tr and bl-to-br by interval and input each into maps api
#Output: Yes: elevation points within mean or No: elevation points out of mean
#from dummy_cv import *

#Choose line sampling number of divisions
line_freq = 10

from object_size import *

#print 'Flatland'
#tl = [33.071831, -115.607114]
#tr = [33.073078, -115.574369]
#bl = [33.055599, -115.608358]
#br = [33.056030, -115.568447]

#top arrays
top_x = np.linspace(tl[0], tr[0], line_freq)
top_y = np.linspace(tl[1], tr[1], line_freq)

#bottom arrays
bottom_x = np.linspace(bl[0], br[0], line_freq)
bottom_y = np.linspace(bl[1], br[1], line_freq)

#Run api and append each line to elevation dictionary
elevations = []
elev_freq = 3
for i in range(len(top_x)):
    r = requests.get('https://maps.googleapis.com/maps/api/elevation/json?path='\
        + str(top_x[i]) + ',' + str(top_y[i]) + '|' + str(bottom_x[i]) + ','\
        + str(bottom_y[i]) + '&samples=' + str(elev_freq) + '&key=AIzaSyCNyDD5upV_IYf4yVzfAmsXrOX5Z66gp_E')
    python_dict = json.loads(r.text)
    llama = python_dict['results']

    for j in llama:
        key = j['elevation']
        elevations.append(key)

#Split elevations list into chunks of elev_freq
chunks = [elevations[x:x+elev_freq] for x in range(0, len(elevations), elev_freq)]

#Gradient check, max 2% for airplane using nearest neighbors
#For slope, find distance from one point on one line sample to other sample

lat_sep = abs((top_x[1] - top_x[0]) * (10000000/90))
vert_sep = abs((top_y[0] - bottom_y[0]) * (10000000/90))
diag_sep = abs(((lat_sep**(2.0) + vert_sep**(2.0))**(1/2.0)) * (10000000/90))

X = len(chunks)
Y = len(chunks[0])

#Gives coordinate of neighbors in matrix: row and column
neighbors = lambda x, y : [(x2, y2) for x2 in range(x-1, x+2)
                               for y2 in range(y-1, y+2)
                               if (-1 < x < X and
                                   -1 < y < Y and
                                   (x != x2 or y != y2) and
                                   (0 <= x2 < X) and
                                   (0 <= y2 < Y))]

#List of slope differences
check = []
for i in range(X):
    for j in range(Y):  #(i,j) = (1,0)
        neigh_coord = neighbors(i,j) #(1,1), (0,1), (0,0)
        # print(neigh_coord)
        for b in range(len(neigh_coord)):
            # if horizontal neighbor
            if abs(i - neigh_coord[b][0] == 1) and abs(j - neigh_coord[b][1] == 0) and abs((chunks[i][j] - chunks[neigh_coord[b][0]][neigh_coord[b][1]]) / lat_sep) <= 1:
                check.append(1)
            # if vertical neighbor
            elif abs(i - neigh_coord[b][0] == 0) and abs(j - neigh_coord[b][1] == 1) and abs((chunks[i][j] - chunks[neigh_coord[b][0]][neigh_coord[b][1]]) / vert_sep) <= 1:
                check.append(1)
            # if diagonal neighbor
            elif abs(i - neigh_coord[b][0] == 1) and abs(j - neigh_coord[b][1] == 1) and abs((chunks[i][j] - chunks[neigh_coord[b][0]][neigh_coord[b][1]]) / diag_sep) <= 1:
                check.append(1)
            else:
                check.append(0)

# print(check)
zeros = check.count(0)
print(str((float(zeros)/len(check)) * 100) + ' % Rough')

if (len(check)*.3) < check.count(1) <= (len(check)):
    print ('Even Terrain')
elif (len(check)*.2) < check.count(1) <= (len(check)*.3):
    print ('Slightly Rough Terrain')
elif (len(check)*.1) < check.count(1) <= (len(check)*.2):
    print ('Medium Rough Terrain')
elif 0 <= check.count(1) <= (len(check)*.1):
    print ('Very Rough Terrain')
else:
    print ('Invalid Entry')
