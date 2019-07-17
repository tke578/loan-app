import os
from flask import request, jsonify, redirect, url_for
from app import app, mongo
from app.schemas import validate_user, validate_saving, validate_saving_funds, validate_link_ach, validate_mfa
import logger
import requests
import json
from functools import wraps

ROOT_PATH = os.environ.get('ROOT_PATH')
LOG = logger.get_root_logger(
    __name__, filename=os.path.join(ROOT_PATH, 'output.log'))


def required_headers(*expected_args):
	def decorator(func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			for expected_arg in expected_args:
				# breakpoint()
				if expected_arg not in request.headers:
					return jsonify({'ok': False, 'message': "Missing " + expected_arg}), 400
			return func(*args, **kwargs)
		return wrapper
	return decorator

@app.route('/register', methods=['POST'])
@required_headers('Content-Type')
def register():
	data = validate_user(request.get_json())
	
	if data['ok']:
		headers = {
					'X-SP-GATEWAY': os.environ.get('CLIENT_ID')+'|'+os.environ.get('CLIENT_SECRET'),
					'X-SP-USER-IP': '127.0.0.1',
					'X-SP-USER': '|e83cf6ddcf778e37bfe3d48fc78a6502062fca', #DEFAULT FINGERPRINT
					'Content-Type': 'application/json'
					}
		data = data['data']
		api_end_point = 'https://uat-api.synapsefi.com/v3.1/users'
		payload = {
				"logins": [
					{
					"email": data['email']
					}	
				],
				"phone_numbers": [
					data['phone_number']
				],
				"legal_names": [
					data['legal_name']
				]
			}
		headers['X-SP-GATEWAY'] = os.environ.get('CLIENT_ID')+'|'+os.environ.get('CLIENT_SECRET')
		response = requests.post(url=api_end_point, data=json.dumps(payload), headers=headers)

		if response.status_code == 200:
			mongo.db.users.insert_one(response.json())
			generate_oauth(response.json()['_id'], response.json()['refresh_token'])
			user = mongo.db.users.find_one({'_id': response.json()['_id']})
			msg = { 'oauth_key': user['oauth_key'], 'user_id': user['_id'] }
			return jsonify(msg), 200
		else:
			return jsonify(response.json()), 400
	else:
		return jsonify({'ok': False, 'message': 'Bad request parameters: {}'.format(data['message'])}), 400

# 		

def generate_oauth(user_id, refresh_token):
	api_end_point = 'https://uat-api.synapsefi.com/v3.1/oauth/'
	headers = {
					'X-SP-GATEWAY': os.environ.get('CLIENT_ID')+'|'+os.environ.get('CLIENT_SECRET'),
					'X-SP-USER-IP': '127.0.0.1',
					'X-SP-USER': '|e83cf6ddcf778e37bfe3d48fc78a6502062fca', #DEFAULT FINGERPRINT
					'Content-Type': 'application/json'
				}
	payload = { 'refresh_token': refresh_token }
	headers['X-SP-GATEWAY'] = os.environ.get('CLIENT_ID')+'|'+os.environ.get('CLIENT_SECRET')
	response = requests.post(url=api_end_point+'/'+user_id, data=json.dumps(payload), headers=headers)
	# breakpoint()
	if "http_code" in response.json():
		if response.json()["http_code"] == "202": #mfa required
			return jsonify(response.json())
	oauth_key = response.json()['oauth_key']
	mongo.db.users.update_one({"_id": user_id}, {'$set': { 'oauth_key': oauth_key}})

@app.route('/user/<user_id>', methods=['GET'])
def user(user_id):
	user = mongo.db.savings.find_one({'user_id': user_id})
	# breakpoint()
	if user:
		return jsonify(user), 200
	else:
		return jsonify({"ok": False, "msg": "No user found with that id"}), 400


@app.route('/link_ach/<user_id>/nodes', methods=['POST'])
@required_headers('Content-Type', 'Oauth-Key')
def link_ach(user_id):
	api_end_point = 'https://uat-api.synapsefi.com/v3.1/users/'+user_id+'/nodes'
	headers = {
		'X-SP-USER-IP': '127.0.0.1',
		'X-SP-USER': request.headers['Oauth-Key']+'|e83cf6ddcf778e37bfe3d48fc78a6502062fc', #DEFAULT FINGERPRINT
		'Content-Type': request.headers['Content-Type']
	}
	request_payload = request.get_json()
	# breakpoint()
	#CHECK IF A REQUEST IS A VALID LINK ACH OR MFA
	if 'access_token' in request_payload:
		data = validate_mfa(request.get_json())
		payload = { "access_token": request_payload["access_token"], "mfa_answer": request_payload["mfa_answer"] }
	else:
		data = validate_link_ach(request.get_json())
		payload = {
			"type": "ACH-US",
			"info": {
				"bank_id": request_payload["user_name"],
				"bank_pw": request_payload["user_pw"],
				"bank_name": request_payload["user_bank"]
			}
		}
	response = requests.post(url=api_end_point, data=json.dumps(payload), headers=headers)
	if data['ok']:
		if response.json()["http_code"] == "202": #MFA REQUIRED
				return jsonify(response.json()["mfa"])
		elif response.json()["http_code"] == "200": #MFA NOT REQUIRED
			mongo.db.link_ach.insert_one(response.json()['nodes'][0])
			return jsonify(response.json()['nodes'][0])
		else:
			return jsonify(response.json())
	else:
		return jsonify(response.json())

@app.route('/ach/<user_id>/nodes/<node_id>', methods=['GET'])
@required_headers('Content-Type', 'Oauth-Key')
def ach(user_id, node_id):
	api_end_point = 'https://uat-api.synapsefi.com/v3.1/users/'+user_id+'/nodes/'+node_id
	ach = mongo.db.link_ach.find_one({"_id": node_id})
	if ach:
		return jsonify(ach), 200
	else:
		return jsonify({'ok' : False, 'msg': 'No Linked ACH found!'}), 400

@app.route('/open_savings_account/<user_id>', methods=['POST'])
@required_headers('Content-Type', 'Oauth-Key')
def open_savings_account(user_id):	
	api_end_point = 'https://uat-api.synapsefi.com/v3.1/users/'+user_id+'/nodes'
	oauth_key = request.headers['Oauth_key']
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
			node_structure = response.json()['nodes'][0]
			response_account_obj = {
				"account_id": node_structure['_id'],
				"account_info": node_structure['info']
			}
			return jsonify(response_account_obj)
	else:
		return jsonify(response.json())

@app.route('/refresh_token/<user_id>', methods=['POST'])
@required_headers('Content-Type')
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
@required_headers('Content-Type', 'Oauth-Key')
def deposit_funds(user_id, node_id):
	api_end_point = 'https://uat-api.synapsefi.com/v3.1/users/'+user_id+'/nodes/'+node_id+'/trans'
	oauth_key = request.headers['oauth_key']
	headers = {
				'X-SP-USER-IP': '127.0.0.1',
				'X-SP-USER': oauth_key+'|e83cf6ddcf778e37bfe3d48fc78a6502062fc', #DEFAULT FINGERPRINT
				'Content-Type': 'application/json'
	}
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
			node_structure = response.json()
			transaction_obj = {
				"transaction_id": node_structure["_id"],
				"amount": node_structure["amount"]["amount"],
				"currency": node_structure["amount"]["currency"],
				"sending_account": node_structure["from"],
				"receiving_account": node_structure["to"]
			}
			return jsonify(transaction_obj), 200		
		else:
			return jsonify(response.json())
	else:
		return jsonify({'ok': False, 'message': 'Bad request parameters: {}'.format(data['message'])}), 400



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
