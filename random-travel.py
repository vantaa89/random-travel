import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm
import math
import urllib
from PIL import Image
from io import BytesIO
import requests

import random
from geopy.geocoders import Nominatim


class BoundBox:
    def __init__(self, lat_south, lat_north, lon_west, lon_east):
        self.lat_south = lat_south
        self.lat_north = lat_north
        self.lon_west = lon_west
        self.lon_east = lon_east
    
    def deg2pix(self, lat, lon, zoom):
        lat_num_south, lon_num_west = deg2num(self.lat_south, self.lon_west, zoom)
        lat_num_north, lon_num_east = deg2num(self.lat_north, self.lon_east, zoom)
        width_pixels, height_pixels = int(256 * int(lon_num_west - lon_num_east)), int(256 * (lat_num_north - lat_num_south))
        lat_num, lon_num = deg2num(lat, lon, zoom)
        lat_pixel = int((lat_num - lat_num_south) / (lat_num_north - lat_num_south) * height_pixels)
        lon_pixel = int((lon_num - lon_num_west) / (lon_num_east - lon_num_west) * width_pixels)
        return (lat_pixel, width_pixels - lon_pixel)

    def get_map(self, zoom):
        smurl = r"http://a.tile.openstreetmap.org/{0}/{1}/{2}.png"
        xmin, ymax = deg2num(self.lat_south, self.lon_west, zoom)
        xmax, ymin = deg2num(self.lat_north, self.lon_east, zoom)

        cluster = Image.new('RGB',(int((xmax-xmin)*256),int((ymax-ymin)*256)))
        for xtile in range(math.floor(xmin), math.ceil(xmax)):
            for ytile in range(math.floor(ymin), math.ceil(ymax)):
                try:
                    imgurl = smurl.format(zoom, xtile, ytile)
                    headers = {
                        'User-Agent': 'My User Agent 1.0',
                        'From': 'youremail@domain.example'
                    }

                    response = requests.get(imgurl, headers=headers)
                    image = Image.open(BytesIO(response.content))
                    cluster.paste(image, box=(int((xtile-xmin)*256) , int((ytile-ymin)*255)))
                except:
                    print(f"Couldn't download image from {imgurl}")
                    tile = None

        return cluster

    def random_point(self):
        lat = self.lat_south + random.random() * (self.lat_north - self.lat_south)
        lon = self.lon_west + random.random() * (self.lon_east - self.lon_west)
        return (lat, lon)

def deg2num(lat_deg, lon_deg, zoom, floor=False):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = ((lon_deg + 180.0) / 360.0 * n)
    ytile = ((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    if floor:
        return (int(xtile), int(ytile))
    else:
        return (xtile, ytile)


def num2deg(xtile, ytile, zoom, floor=False):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)


if __name__ == "__main__":
    bbox = BoundBox(34.5, 38.5, 126, 130)
    zoom_level = 9
    a = bbox.get_map(zoom_level)

    point_lat, point_lon = bbox.random_point()
    fig = plt.figure(figsize=(10, 10))
    print(point_lat, point_lon)
    geolocator = Nominatim(user_agent="my user agent 1.0")
    location = geolocator.reverse(f"{point_lat}, {point_lon}")
    if location is not None:
        print(location.address)

    fig.patch.set_facecolor('white')
    plt.imshow(np.asarray(a))
    pixel_x, pixel_y = bbox.deg2pix(point_lat, point_lon, zoom_level)
    plt.plot(pixel_x, pixel_y, 'ro')
    plt.show()
