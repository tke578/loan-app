# A simple savings account utilizing the synpasefi api with Flask and Mongo

#### Assumptions

Device fingerprint is `e83cf6ddcf778e37bfe3d48fc78a6502062fc` since this was used on a development environment as well as the ip of the user `127.0.0.1` and headers will always be json, and client id and secret is provided on the server


### Setup 

* Install Docker
* Build the Docker Image `docker-compose up -d --build`


## API Endpoints

#### Sign up
`POST  /register/`

Response 
returns the oauth key of the user which you will need to supply on behalf of the user.

` { oauth_key: 'abcd123', user_id: 123 }`


