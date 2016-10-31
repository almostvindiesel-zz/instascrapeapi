"""

- download pic and videos
- replicate db on pythonanywhere





"""


from app import app
import os
import shutil

import requests
import urllib
from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy import UniqueConstraint, distinct, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship


#from PIL import Image
#from resizeimage import resizeimage
#import imghdr

from flaskext.mysql import MySQL
import MySQLdb


#print "os environment: ", os.environ["NOMNOMTES_ENVIRONMENT"]

print "Loading models.py..."
db = SQLAlchemy(app)

#alter table insta_media_asset modify longitude Float(10,6)
#alter table insta_media_asset modify latitude Float(10,6)
#alter table insta_media_asset modify column latitude varchar(1000);
#ALTER TABLE insta_media_asset DROP COLUMN image_full
#ALTER TABLE insta_media_asset DROP COLUMN image_thumb
#ALTER TABLE insta_media_asset ADD full_width Integer
#ALTER TABLE insta_media_asset ADD full_height Integer
#ALTER TABLE insta_media_asset ADD thumb_width Integer
#ALTER TABLE insta_media_asset ADD thumb_height Integer


class InstaMediaAsset(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    code = db.Column(db.String(500))
    type = db.Column(db.String(100))


    image_url  = db.Column(db.String(500))
    video_url  = db.Column(db.String(500))
    instagram_url  = db.Column(db.String(500))

    full_width = db.Column(db.Integer)
    full_height = db.Column(db.Integer)
    thumb_width = db.Column(db.Integer)
    thumb_height = db.Column(db.Integer)
    """
    image_full  = db.Column(db.String(200))
    image_thumb = db.Column(db.String(200))
    """
    caption  = db.Column(db.String(1000))
    likes = db.Column(db.Integer)
    travel_day_nbr = db.Column(db.Integer)

    location_id = db.Column(db.Integer)
    location_name  = db.Column(db.String(200))
    latitude  = db.Column(db.Float(16))
    longitude  = db.Column(db.Float(16))

    created_date = db.Column(db.Date)

    __table_args__ = {'mysql_charset': 'utf8mb4'}

    def __init__(self, code, instagram_url):
        self.code = code
        self.instagram_url = instagram_url

    def __repr__(self):
        return '<InstaMediaAsset %r>' % self.id

    UniqueConstraint('travel_day_nbr', name='travel_day_constraint')

    def insert(self):
        try:
            db.session.add(self)
            db.session.commit()
            print "--- inserted insta media asset, day #:",  self.travel_day_nbr
        except Exception as e:
            print "Could not insert insta media asset:"
            print "id: %s travel_day_nbr: %s" % (self.id, self.travel_day_nbr)
            print e.message, e.args

    """
    def set_city_state_country_with_lat_lng_from_google_location_api(self):

        try: 
            gurl = 'http://maps.googleapis.com/maps/api/geocode/json?latlng=%s,%s&sensor=false' % (self.latitude, self.longitude)
            print "--- Searching for Location attributes from Google Loc API on lat (%s) long (%s): \r\n %s " % (self.latitude, self.longitude, gurl)

            r = requests.get(gurl)
            g_json = r.json()
            for datums in g_json['results'][0]['address_components']:
                if datums['types'][0] == 'locality':
                    self.city = datums['long_name']
                    print "--- From Google Lat Long API, City:  ", datums['long_name']
                if datums['types'][0] == 'administrative_area_level_1':
                    self.state = datums['long_name']
                    print "--- From Google Lat Long API, State: ", datums['long_name']
                if datums['types'][0] == 'country':
                    self.country = datums['long_name']
                    print "--- From Google Lat Long API, Country: ", datums['long_name']
        
        except Exception as e:
            print "Could not get data from google api api: ", e.message, e.args


    def set_lat_lng_state_from_city_country(self):

        try: 
            gurl = 'https://maps.googleapis.com/maps/api/geocode/json?address=%s&components=country:%s' % (self.city, self.country)
            print "--- Searching for Location attributes from Google Loc API on city (%s) country (%s): \r\n %s " % (self.city, self.country, gurl)

            r = requests.get(gurl)
            g_json = r.json()
            for datums in g_json['results'][0]['address_components']:
            #    if datums['types'][0] == 'locality':
            #        self.city = datums['long_name']
            #        print "--- From Google Lat Long API, City:  ", datums['long_name']
                if datums['types'][0] == 'administrative_area_level_1':
                    self.state = datums['long_name']
                    print "--- From Google Lat Long API, State: ", datums['long_name']
            #    if datums['types'][0] == 'country':
            #        self.country = datums['long_name']
            #        print "--- From Google Lat Long API, State: ", datums['long_name']
            if 'lat' in g_json['results'][0]['geometry']['location']:
                self.latitude = g_json['results'][0]['geometry']['location']['lat']
            if 'lng' in g_json['results'][0]['geometry']['location']:
                self.longitude = g_json['results'][0]['geometry']['location']['lng']
        
        except Exception as e:
            print "Could not get data from google api : ", e.message, e.args
    """
            



############################################################


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def init_db():  
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())

@app.cli.command('initdb')
def initdb_command():
    """ s the database tables."""
    init_db()
    print('Initialized the database.')

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db



