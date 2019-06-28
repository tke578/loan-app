import os
from flask import request, jsonify, redirect, url_for
from app import app, mongo
from app.schemas import validate_user, validate_saving, validate_saving_funds
import logger
import requests
import json

ROOT_PATH = os.environ.get('ROOT_PATH')
LOG = logger.get_root_logger(
    __name__, filename=os.path.join(ROOT_PATH, 'output.log'))



@app.route('/register', methods=['POST'])
def register():
	data = validate_user(request.get_json())
	
	if data['ok']:
		headers = {
					'X-SP-GATEWAY': os.environ.get('CLIENT_ID')+'|'+os.environ.get('CLIENT_SECRET'),
					'X-SP-USER-IP': '127.0.0.1',
					'X-SP-USER': '|e83cf6ddcf778e37bfe3d48fc78a6502062fc', #DEFAULT FINGERPRINT
					'Content-Type': 'application/json'
					}
		data = data['data']
		api_end_point = 'https://uat-api.synapsefi.com/v3.1/users'
		headers['X-SP-GATEWAY'] = os.environ.get('CLIENT_ID')+'|'+os.environ.get('CLIENT_SECRET')
		response = requests.post(url=api_end_point, data=json.dumps(data), headers=headers)

		if response.status_code == 200:
			mongo.db.users.insert_one(response.json())
			generate_oauth(response.json()['_id'], response.json()['refresh_token'])
			user = mongo.db.users.find_one({'_id': response.json()['_id']})
			msg = { 'oauth_key': user['oauth_key'], 'user_id': user['_id'] }
			return jsonify(msg), 200
		else:
			return jsonify({'ok': False, 'message': 'Bad request parameters: {}'.format(data['message'])}), 400
	else:
		return jsonify(response.json())

# 		

def generate_oauth(user_id, refresh_token):
	api_end_point = 'https://uat-api.synapsefi.com/v3.1/oauth/'
	headers = {
					'X-SP-GATEWAY': os.environ.get('CLIENT_ID')+'|'+os.environ.get('CLIENT_SECRET'),
					'X-SP-USER-IP': '127.0.0.1',
					'X-SP-USER': '|e83cf6ddcf778e37bfe3d48fc78a6502062fc', #DEFAULT FINGERPRINT
					'Content-Type': 'application/json'
				}
	token_obj = { 'refresh_token': refresh_token }
	headers['X-SP-GATEWAY'] = os.environ.get('CLIENT_ID')+'|'+os.environ.get('CLIENT_SECRET')
	response = requests.post(url=api_end_point+'/'+user_id, data=json.dumps(token_obj), headers=headers)
	# breakpoint()
	oauth_key = response.json()['oauth_key']
	mongo.db.users.update_one({"_id": user_id}, {'$set': { 'oauth_key': oauth_key}})


@app.route('/open_savings_account/<user_id>', methods=['POST'])
def open_savings_account(user_id):
	if 'oauth_key' in request.headers:
		oauth_key = request.headers['oauth_key']	
		api_end_point = 'https://uat-api.synapsefi.com/v3.1/users/'+user_id+'/nodes'
		headers = {
					'X-SP-USER-IP': '127.0.0.1',
					'X-SP-USER': oauth_key+'|e83cf6ddcf778e37bfe3d48fc78a6502062fc', #DEFAULT FINGERPRINT
					'Content-Type': 'application/json'
		}
		data = validate_saving(request.get_json())
		if data['ok']:
			payload = { 
					"type": "IB-DEPOSIT-US",
					"info": data['data']
				}
			response = requests.post(url=api_end_point, data=json.dumps(payload), headers=headers)
			if response.json()['success'] == False:
				return jsonify(response.json())
			else:
				mongo.db.savings.insert_one(response.json()['nodes'][0])
				return jsonify(response.json()['nodes'])
		else:
			return jsonify(response.json())
	else:
		return jsonify({'ok': False, 'message': 'Missing oauth key!'}), 400

@app.route('/refresh_token/<user_id>', methods=['POST'])
def get_refresh(user_id):
	api_end_point = 'https://uat-api.synapsefi.com/v3.1/users/'
	headers = {
				'X-SP-GATEWAY': os.environ.get('CLIENT_ID')+'|'+os.environ.get('CLIENT_SECRET'),
				'X-SP-USER-IP': '127.0.0.1',
				'X-SP-USER': '|e83cf6ddcf778e37bfe3d48fc78a6502062fc', #DEFAULT FINGERPRINT
				'Content-Type': 'application/json'
	}
	response = requests.get(url=api_end_point+user_id, headers=headers)
	if response.status_code == 200:
		generate_oauth(response.json()['_id'], response.json()['refresh_token'])
		user = mongo.db.users.find_one({'_id': response.json()['_id']})
		msg = { 'oauth_key': user['oauth_key'], 'user_id': user['_id'] }
		return jsonify(msg), 200
	else:
		return jsonify(response.json()), 400
		
@app.route('/deposit_funds/<user_id>/nodes/<node_id>/trans', methods=['POST'])
def depost_funds(user_id, node_id):
	api_end_point = 'https://uat-api.synapsefi.com/v3.1/users/'+user_id+'/nodes/'+node_id+'/trans'
	if 'oauth_key' in request.headers:
		oauth_key = request.headers['oauth_key']
		headers = {
					'X-SP-USER-IP': '127.0.0.1',
					'X-SP-USER': oauth_key+'|e83cf6ddcf778e37bfe3d48fc78a6502062fc', #DEFAULT FINGERPRINT
					'Content-Type': 'application/json'
		}
		# breakpoint()
		data = validate_saving_funds(request.get_json())
		if data['ok']:
			data = data['data']
			payload = {
				"to": {
					"type": "IB-DEPOSIT-US",
					"id": data['receiving_account']
				},
				"amount": {
					"amount": data['amount'],
					"currency": "USD"
				},
				"extra": {
					"ip": "127.0.0.1"
				}
			}
			response = requests.post(url=api_end_point, data=json.dumps(payload), headers=headers)
			if response.status_code == 200:
				mongo.db.deposits.insert_one(response.json())
				return jsonify(response.json())		
			else:
				return jsonify(response.json())
		else:
			return jsonify({'ok': False, 'message': 'Bad request parameters: {}'.format(data['message'])}), 400
		

	else:
		return jsonify({'ok': False, 'message': 'Missing oauth key!'}), 400



@app.route('/all_user_savings_accounts/<user_id>', methods=['GET'])
def all_user_savings_accounts(user_id):
	savings = mongo.db.savings.find({'user_id': user_id})
	if savings.count() > 0:
		collection = []
		for acct in savings:
			collection.append(acct)
		return jsonify(collection), 200
	else:
		return jsonify({'ok': True, 'message': 'No savings accounts found under that user'})


@app.route('/all_user_deposits/<node_id>', methods=['GET'])
def all_user_deposits(node_id):
	collection = []
	deposits = mongo.db.deposits.find({'to.id': node_id })
	if deposits.count() > 0:
		for dep in deposits:
			collection.append(dep)
		return jsonify(collection), 200
	else:
		return jsonify({'ok': True, 'message': 'No deposits found under that account'})
	
# {
#   "to": {
#     "type": "IB-DEPOSIT-US",
#     "id": "5bb6fbd085411800baebc9a3"
#   },
#   "amount": {
#     "amount": 375.21,
#     "currency": "USD"
#   },
#   "extra": {
#     "ip": "127.0.0.1",
#     "note": "Test transaction"
#   }
# }

		


	
