# A simple savings account utilizing the synpasefi api with Flask and Mongo

#### Assumptions

Device fingerprint is `e83cf6ddcf778e37bfe3d48fc78a6502062fc` since this was used on a development environment as well as the ip of the user `127.0.0.1` and headers will always be json, and client id and secret is provided on the server


### Prerequisites  

* Install Docker
* Mongodb for client purposes
* Build the Docker Image `docker-compose up -d --build`


## API Endpoints

#### Sign up

Route `/register` 

HTTP verb `POST`

Headers `Content-type = application/json`

Body

```
{
	"email": "blah@gmail.com",
	"phone_number": "(323)220-5555",
	"legal_name":	"Drewskie"
}
```

Required: email, phone_number,legal_name

Response 


` { oauth_key: 'abcd123', user_id: 123 }`

Note: You will need need a oauth key on making requests on behalf of the user. Oauth keys typically expire at a period of time. New oauth keys require a refresh token also expires at a period of time. 
Also, oauth keys must be passed in the headers like so `'oauth_key' = 'oauth_1233'`

### Refresh Token

Route `/refresh_token/:user_id`

HTTP verb `POST`


Response ` { oauth_key: 'abcd123', user_id: 123 }`

### Open Savings Account

Route `/open_savings_account/:user_id`

HTTP verb `POST`

Headers `Content-type = 'application/json', oauth_key = 'oauth_123' }

Body `{ nickname = 'myAccount' }

Response

```
{
  "account_id": "abc123",
  "account_info: {
                    "balance" : {
                                    "amount" : 0,
                                    "currency": "USD",
                                    "interest": 0.0,
                                 },
                     "bank_node":  "EBT",
                     "document_id": None,
                     "monthly_withdrawls_remaining: 6,
                     "name_on_account": '',
                     "nicname": "myAccount"
                     },
                    },
   }
```

### Deposit funds to Savings Account

Route `/deposit_funds/:user_id/nodes/:account_id/trans`

HTTP verb `POST`

Headers `Content-type = 'application/json', oauth_key = 'oauth_123'

Body 
```
{
	"receiving_account": "abcd123",
	"amount": 50
}
```

Response

```
{
    "amount": 50,
    "currency": "USD",
    "receiving_account": {
        "id": "abcdfds123",
        "nickname": "Testing",
        "type": "IB-DEPOSIT-US",
        "user": {
            "_id": "abcd",
            "legal_names": [
                "Drewskie"
            ]
        }
    },
    "sending_account": {
        "id": "abcd",
        "nickname": "Testing",
        "type": "IB-DEPOSIT-US",
        "user": {
            "_id": "abcdd",
            "legal_names": [
                "Drewskie"
            ]
        }
    },
    "transaction_id": "abcd132"
}
```


### View all User Savings Accounts 

Route `/all_user_savings_accounts/:user_id`

HTTP verb `GET`

Headers `oauth_key = 'oauth_123'


### View all User Deposit Transctions for a particular account

Route '/all_user_deposits/:account_id

HTTP verb `POST`

Headers `oauth_key = 'oauth_123`


