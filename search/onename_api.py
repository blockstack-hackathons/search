
#!/usr/bin/env python
#-----------------------
# Copyright 2014 Halfmoon Labs, Inc.
# All Rights Reserved
#-----------------------

'''
	Developer  API -- powers onename Search  
'''

from flask import request, jsonify, Flask
from search_api import get_people
from flask import make_response
import json
from bson import json_util
from helpers import *

app = Flask(__name__)

DEFAULT_LIMIT = 35

from pymongo import MongoClient
c = MongoClient()
#----------------------------------------------
@app.route('/v1/gen_developer_key/<developer_id>', methods = ['GET'])
def create_account(developer_id):
	#saves the ID and returns the access token
	access_token = save_user(developer_id, 'basic')
	
	return jsonify({'developer_id':developer_id,
					  'access_token':access_token})

#----------------------------------------------
#Search API 
#The Search API returns the profiles based on keyword saerches.
#Results are retrieved through indexed data
#----------------------------------------------
@app.route('/v1/people-search/<developer_id>/<access_token>', methods = ['GET'])
def search_people(developer_id,access_token):
	#1. verify key
	if not is_key_valid(access_token):
		return make_response(jsonify( { 'error': 'Invalid Token' } ), 400)

	#2. verify available quota
	if is_overquota(developer_id):
		return make_response(jsonify( { 'error': 'Quota Exceeded' } ), 401)
	
	results = ""
	#TODO: Add error handling if keywords is missing
	request_val = request.values

	#handle keyword search
	if 'keywords' in request_val:
		results = get_people(request.values['keywords'])
	elif 'full-name' in request_val:
		results = get_people(request.values['full-name'])
	elif 'twitter' in request_val:
		results = get_people(request.values['twitter'])
	elif 'btc_address' in request_val:
		results = get_people(request.values['btc_address'])

	#TODO: check for errors, check for empty response 
	if results == "":
		return make_response(jsonify( { 'error': 'invalid request' } ), 401)
	else:
		return results

#---------------------------------------------
#Profile API 
#The Profile API returns the public Onename profile based.
#Results are retrieved from the onename_db
#---------------------------------------------
@app.route('/v1/people/id=<onename_id>', methods = ['GET'])
def get_onename_profile(onename_id):
	return json.dumps(query_people_database(onename_id))

#----------------------untested--not working----------------------
@app.route('/v1/people/url=<onename_profile_url>', methods = ['GET'])
def get_profile_from_url(onename_profile_url):
	#untested
	return ""#jsonify(query_people_database(onename_profile_url))

#-------------------------------------------
def query_people_database(onename_id,limit_results=DEFAULT_LIMIT):

	db = c['onename_search']
	
	nodes = db.nodes

	onename_profile = nodes.find_one({"name": 'u/' + onename_id})

	#onename_profile = nodes.find({'value': {"$elemMatch": {"website":"http://muneebali.com"} }})
	
	profile_details = json.loads(onename_profile['value'])
	
	#TODO: add error handling
	return onename_profile

#custom error handling to return JSON error msgs
#----------------------------------------------
@app.errorhandler(404)
def not_found(error):
    '''
    Returns a jsonified 404 error message instead of a HTTP 404 error.
    '''
    return make_response(jsonify({ 'error': '404 not found' }), 404)

#----------------------------------------------
@app.errorhandler(503)
def not_found(error):
    '''
    Returns a jsonified 503 error message instead of a HTTP 404 error.
    '''
    return make_response(jsonify({ 'error': '503 something wrong' }), 503)

#----------------------------------------------
@app.errorhandler(500)
def not_found(error):
    '''
    Returns a jsonified 500 error message instead of a HTTP 404 error.
    '''
    return make_response(jsonify({ 'error': '500 something wrong' }), 500)
#----------------------------------------------
if __name__ == '__main__':
	app.run(debug=True, port=5003)

