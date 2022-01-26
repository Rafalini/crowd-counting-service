import math
import os
import secrets
import requests

from PIL import Image
from crowdControll import app, db
from crowdControll.models import Post
from crowdControll.displayModels import PlaceGroup


def save_profile_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def save_post_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/post_imgs', picture_fn)
    i = Image.open(form_picture)
    i.save(picture_path, quality=100)
    return picture_fn


def getAddressFromDb(id):
    post = Post.query.get(id)
    post.address = getAddress(post.latitude, post.longitude)
    db.session.commit()


def getAddress(lat, lon): #municipality, city, town, village
    address = getAddressPlain(lat, lon)['address']
    # if 'county' in address:
    #     return address['county']
    if 'state' in address:
        return address['state']
    # if 'municipality' in address:
    #     return address['municipality']
    # if 'city' in address:
    #     return 'miasto ' + address['city']
    # if 'town' in address:
    #     return 'miasteczko ' + address['town']
    # if 'village' in address:
    #     return 'wieś ' + address['village']
    return 'unknown place'


def getAddressPlain(lat, lon):
    URL = "https://nominatim.openstreetmap.org/reverse"
    PARAMS = {'lat': lat, 'lon': lon, 'format': 'json'}
    r = requests.get(url=URL, params=PARAMS)
    return r.json()


def getDistanceFromLatLonInKm(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the earth in km
    dLat = deg2rad(lat2 - lat1)  # deg2rad below
    dLon = deg2rad(lon2 - lon1)

    sin1 = math.sin(dLat / 2) * math.sin(dLat / 2)
    cos1 = math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2))
    sin2 = math.sin(dLon / 2) * math.sin(dLon / 2)

    a = sin1 + cos1 * sin2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c  # Distance in km
    return d


def deg2rad(deg):
    return deg * (math.pi / 180)


def uniquePlaces(posts):
    groupedPosts = {}

    for post in posts:
        if post.address not in groupedPosts:
            groupedPosts[post.address] = PlaceGroup()

        groupedPosts[post.address].posts.append(post)
        groupedPosts[post.address].count += post.number_of_people

    places = []
    for key in groupedPosts:
        places.append(key)
    return places


def filterPosts(posts, place):
    for post in posts:
        if post.address != place:
            posts.remove(post)
    return posts

