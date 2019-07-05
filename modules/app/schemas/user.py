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

ach_link_schema = {
    "type": "object",
    "properties": {
        "user_name": {
            "type": "string"
        },
        "user_pw": {
            "type": "string"
        },
        "user_bank": {
            "type": "string"
        }
    },
    "required": ["user_name", "user_pw", "user_bank"],
    "additionalProperties": False
}

mfa_schema = {
    "type": "object",
    "properties": {
        "access_token": {
            "type": "string"
        },
        "mfa_answer": {
            "type": "string"
        }
    },
    "required": ["access_token", "mfa_answer"],
    "additionalProperties": False
}

def validate_link_ach(data):
    try:
        validate(data, ach_link_schema)
    except ValidationError as e:
        return {'ok': False, 'message': e}
    except SchemaError as e:
        return {'ok': False, 'message': e}
    return {'ok': True, 'data': data}

def validate_mfa(data):
    try:
        validate(data, mfa_schema)
    except ValidationError as e:
        return {'ok': False, 'message': e}
    except SchemaError as e:
        return {'ok': False, 'message': e}
    return {'ok': True, 'data': data}

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
