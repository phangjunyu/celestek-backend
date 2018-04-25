import image_slicer
from PIL import ImageDraw, ImageFont


tiles = image_slicer.slice('ndvi_cmap.png', 50, save=False)

# for tile in tiles:
    # overlay = ImageDraw.Draw(tile.image)
    # overlay.text((5, 5), str(tile.number), (255, 255, 255),
    #              ImageFont.load_default())

#Change it to become byteIO files
# with zipfile.ZipFile('tiles.zip', 'w') as zip:
#     for tile in tiles:
#         with io.BytesIO() as data:
#             tile.save(data)
#             zip.writestr(tile.generate_filename(path=False),
#             data.getvalue())
image_slicer.save_tiles(tiles, directory='./image_slices', prefix='slice')

# joined_image = image_slicer.join(tiles)
# joined_image.save('joined.jpg')
