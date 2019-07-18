# A simple savings account utilizing the synpasefi api with Flask and Mongo

#### Assumptions

Device fingerprint is fixed for all users while used in a development environment as well as IP addreres. Headers with a payload on the body will always be `json` and and client id and secret is provided on the server. 


### Prerequisites  

* Install Docker
* Mongodb for client purposes
* Build the Docker Image `docker-compose up -d --build`
* Navigate to localhost:4000


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
Also, oauth keys must be passed in the headers like so `'Oauth-Key' = 'oauth_1233'`

### Refresh Token

Route `/refresh_token/:user_id`

HTTP verb `POST`


Response `{ "oauth_key": 'abcd123', "user_id": 123 }`

### Link ACH Account with Bank Login


Note: Majority of time, MFA(Multi-factor Authorization) is required to prove the legitimacy of the account holder.
For development purposes, use dummy values ` "bank_id":"synapse_good", "bank_pw":"test1234", "bank_name":"fake" `
For mfa answer,  supply `"test_answer"`

Route '/link_ach/:user_id/nodes'

HTTP verb `POST`

Headers `Content-Type = 'application/json', Oauth-Key = 'oauth_123' }`

Body `{ "user_name": "synapse_good", "user_pw": "test1234", "user_bank": "fake" }`

Response with MFA required 
```
{
    "access_token": "fake_cd60680b9addc013ca7fb25b2b704be324d0295b34a6e3d14473e3cc65aa82d3",
    "message": "I heard you like questions so we put a question in your question?",
    "type": "question"
}
```

MFA Request 

Route `/link_ach/:user_id/nodes`

HTTP verb `POST`

Body
```
{
    "access_token":"fake_cd60680b9addc013ca7fb25b2b704be324d0295b34a6e3d14473e3cc65aa82d3",
    "mfa_answer":"test_answer"
}
```

Response 

```
nodes": [
        {
            {"_id": "5d1d490f2f826f3083c4da62"}
	 }.....
"info": {
                "account_num": "8901",
                "address": "PO BOX 85139, RICHMOND, VA, US",
                "balance": {
                    "amount": "800.00",
                    "currency": "USD",
                    "updated_on": 1562207822000
                },
                "bank_logo": "https://cdn.synapsepay.com/bank_logos/new/co.png",
                "bank_long_name": "CAPITAL ONE N.A.",
                "bank_name": "CAPITAL ONE N.A.",
                "class": "CHECKING",
                "match_info": {
                    "email_match": "not_found",
                    "name_match": "not_found",
                    "phonenumber_match": "not_found"
                },
                "name_on_account": " ",
                "nickname": "SynapsePay Test Checking Account - 8901",
                "routing_num": "6110",
                "type": "PERSONAL"
            }
```

### Get User Linked ACH account

Route `/ach/<user_id>/nodes/<node_id>`

HTTP verb `GET`



### Open Savings Account

Route `/open_savings_account/:user_id`

HTTP verb `POST`

Headers `Content-Type = 'application/json', Oauth-Key = 'oauth_123' }`

Body `{ "nickname": "myAccount" }`

Response returns account

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

Headers `Content-Type = 'application/json', Oauth-Key = 'oauth_123' }`

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


### View all User Deposit Transctions for a particular account

Route '/all_user_deposits/:account_id

HTTP verb `GET`

