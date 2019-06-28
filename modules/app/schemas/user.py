from jsonschema import validate
from jsonschema.exceptions import ValidationError
from jsonschema.exceptions import SchemaError

user_schema = {
    "type": "object",
    "properties":  {
        "email":    {
            "type": "string",
            "format": "email"
        },
        "phone_number": {
            "type":  "string",
            "pattern": "^(\\([0-9]{3}\\))?[0-9]{3}-[0-9]{4}$"
        },
        "legal_name": {
            "type": "string"
        }    
    },
    "required": ["email", "phone_number", "legal_name"],
    "additionalProperties": False
}
# user_schema = {
#     "type": "object",
#     "properties": {
#         "logins": {
#             "type": "array",
#         },
#         "phone_numbers": {
#             "type": "array",
    
#         },
#         "legal_names": {
#             "type": "array"
#         }
#     },
#     "required": ["logins", "phone_numbers", "legal_names"],
#     "additionalProperties": False
# }

saving_schema = {
    "type": "object",
    "properties": {
        "nickname": {
            "type": "string"
        }
    },
    "required": ["nickname"],
    "additionalProperties": False    
}

saving_deposit_schema = {
    "type": "object",
    "properties": {
        "receiving_account": {
            "type": "string"
        },
        "amount": {
            "type": "number",
            "minimum": 1
        }
    },
    "required": ["receiving_account", "amount"],
     "additionalProperties": False
}


def validate_saving_funds(data):
    try:
        validate(data, saving_deposit_schema)
    except ValidationError as e:
        return {'ok': False, 'message': e}
    except SchemaError as e:
        return {'ok': False, 'message': e}
    return {'ok': True, 'data': data}

def validate_saving(data):
    try:
        validate(data, saving_schema)
    except ValidationError as e:
        return {'ok': False, 'message': e}
    except SchemaError as e:
        return {'ok': False, 'message': e}
    return {'ok': True, 'data': data}


def validate_user(data):
    try:
        validate(data, user_schema)
    except ValidationError as e:
        return {'ok': False, 'message': e}
    except SchemaError as e:
        return {'ok': False, 'message': e}
    return {'ok': True, 'data': data}
