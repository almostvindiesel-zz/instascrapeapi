#!/usr/bin/env python
# -*- coding: utf-8 -*-

print "Loading views.py ..."

from app import app
import warnings
from flask.exthook import ExtDeprecationWarning
warnings.simplefilter('ignore', ExtDeprecationWarning)
#import sqlite3
import urllib
import os
#import sys
import random
import requests
import requests.packages.urllib3
import re
import urllib
from fuzzywuzzy import fuzz
from datetime import datetime
import json
from json import dumps, loads

#from contextlib import closing #from werkzeug.utils import secure_filename #requests.packages.urllib3.disable_warnings()
from sqlalchemy import UniqueConstraint, distinct, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import text
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, render_template_string, flash, jsonify, make_response
from sqlalchemy.dialects import postgresql
from werkzeug.datastructures import ImmutableMultiDict

from PIL import Image
from resizeimage import resizeimage
import imghdr

from models import db, InstaMediaAsset

from flaskext.mysql import MySQL
import MySQLdb
import datetime

"""
https://api.instagram.com/v1/locations/1671689?access_token=

{
    data: {
    latitude: 33.979926643789,
    id: "1671689",
    longitude: -118.44584195529,
    name: "The Marina Del Rey Hotel"
    }
}

"""
@app.route('/resize_and_store_image_dimensions')
def resize_and_store_image_dimensions():

    assets = InstaMediaAsset.query.all()

    for a in assets:

        image_full_name = str(a.id) + '.jpg'
        image_thumb_name = str(a.id) + '_thumb.jpg'

        image_dir = 'img/'
        image_full_path = os.path.join(image_dir, image_full_name) 
        image_thumb_path = os.path.join(image_dir, image_thumb_name) 

        thumb_width = 200
        thumb_height = 200

        try:   
            print " Resizing image from %s to %s x %s" % (image_full_path, thumb_width, thumb_height)
            fd_img = open(image_full_path, 'r')
            img = Image.open(fd_img)

            #Write size of original image to database
            a.full_width = img.size[0]
            a.full_height = img.size[1]

            #Resize thumb and write new dimensions to database
            img = resizeimage.resize_thumbnail(img, [thumb_width, thumb_height])
            img.save(image_thumb_path)
            fd_img.close()

            a.thumb_width = thumb_width
            a.thumb_height = thumb_height
            db.session.commit()

            print " Saved thumb img: %s " % (image_thumb_path)
        except Exception as e:
            print "--- Exception ", e.message, e.args

    return 'done'



@app.route('/process_images')
def download_and_resize_images():

    assets = InstaMediaAsset.query.all()

    for a in assets:
        
        """
        a.image_url
        a.video_url

        a.image_full
        a.image_thumb
        """

        image_full_name = str(a.id) + '.jpg'
        image_thumb_name = str(a.id) + '_thumb.jpg'

        image_dir = 'img/'
        image_full_path = os.path.join(image_dir, image_full_name) 
        image_thumb_path = os.path.join(image_dir, image_thumb_name) 

        thumbnail_width = 200

        try:   
            print "Getting image and saving to directory (%s) from url: \r\n %s" % (image_dir + image_full_name, a.image_url)
            f = open(image_full_path,'wb')
            f.write(urllib.urlopen(a.image_url).read())
            f.close()

            try:   
                fd_img = open(image_full_path, 'r')
                print " Resizing image to width %s" % thumbnail_width
                img = Image.open(fd_img)
                img = resizeimage.resize_width(img, thumbnail_width)
                img.save(image_thumb_path)
                #img.save(image_thumb_path, img.format)
                print " Saved thumb img: %s " % (image_thumb_path)
            except Exception as e:
                print "--- Exception ", e.message, e.args

        except Exception as e:
            print "--- Exception ", e.message, e.args

    return 'done'

        

@app.route('/update_location')
def update_location():

    assets = InstaMediaAsset.query.all()

    # https://api.instagram.com/v1/locations/275709079?access_token=254876496.fc522f8.ca74640371e04fa6a7200253d0b4a0d5
    access_token = app.config['INSTAGRAM_ACCESS_TOKEN']


    for a in assets:
        if a.location_id and not a.latitude:
            insta_location_url = 'https://api.instagram.com/v1/locations/%s?access_token=%s' % (a.location_id, access_token)
            try: 
                r = requests.get(insta_location_url)
                r_json = r.json()
                a.latitude = r_json['data']['latitude']
                a.longitude = r_json['data']['longitude']
                db.session.commit()
                print "--- Updated id: %s with location_id: %s with lat: %s and long %s" % (a.id, a.location_id, a.latitude, a.longitude)
            except Exception as e:
                print "--- Could not get data from instagram location api: ", e.message, e.args

    return 'done'

@app.route('/api/add', methods=['POST', 'GET'])
def add_media_asset():

    a = InstaMediaAsset(
        request.form.get('code', None),
        request.form.get('instagram_url', None)
    )

    a.image_url  = request.form.get('image_url', None)
    a.video_url  = request.form.get('video_url', None)
    a.travel_day_nbr  = request.form.get('travel_day_nbr', None)
    a.caption  = request.form.get('caption', None)
    a.likes  = request.form.get('likes', None)
    a.type  = request.form.get('type', None)
    if request.form.get('location_id'):
        a.location_id = request.form.get('location_id')
        print "--------------------got here"

    if request.form.get('location_name'):
        a.location_name = request.form.get('location_name')

    """
    if request.form.get('location_id'):
        
    else:
        a.location_id = None
    if request.form.get('location_name'):
    """
        

    created_date_epoch = request.form.get('created_date_epoch', None)
    print "created_date_epoch: ", created_date_epoch

    a.created_date =  datetime.datetime.fromtimestamp(int(created_date_epoch)).strftime('%Y-%m-%d %H:%M:%S')
    #a.latitude  = request.form.get('latitude', None)
    #a.longitude  = request.form.get('longitude', None)

    """
    print "Getting location data from instagram api for location: ", a.location_id
    access_token = 
    insta_location_url = 'https://api.instagram.com/v1/locations/%s?access_token=%s' % (a.location_id, access_token)
    if a.location_id:
        try: 
            r = requests.get(insta_location_url)
            r_json = r.json()
            print "latitude: ", r_json['latitude']
            print "longitude", r_json['longitude']
        except Exception as e:
            print "-- Could not get data from instagram location api: ", e.message, e.args
    """

    a.insert()

    return jsonify(id=a.id, travel_day_nbr=a.travel_day_nbr, created_date=a.created_date, location_name=request.form.get('location_name', None))

@app.route('/admin/api/createtable/<table>', methods=['GET'])
def create_table(table):

    print '-' * 50
    print "About to create table: ", table

    import models
    klass = getattr(models, table)
    #t = klass()

    try: 
        klass.__table__.create(db.session.bind, checkfirst=True)
        msg = "Created table: %s" % (table)
        return jsonify(msg="success")

    except Exception as e:
        print "Exception ", e.message, e.args
        msg = "ERROR. Could NOT create table: %s" % (table)
        return jsonify(msg="failed")

            

@app.route('/admin/api/droptable/<table>', methods=['GET'])
def drop_table(table):

    print '-' * 50
    print "About to drop table: ", table

    import models
    klass = getattr(models, table)
    #t = klass()

    try: 
        klass.__table__.drop(db.session.bind, checkfirst=True)
        msg = "Dropped table: %s" % (table)
        return jsonify(msg="success")

    except Exception as e:
        print "Error ", e.message, e.args
        msg = "ERROR. Could NOT drop table: %s" % (table)
        return jsonify(msg="failed")
        
    

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()



