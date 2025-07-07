# Transaction system


### To start this up:
For Linux users:
```
cp env/local.env .env
```
For Windows:
```
copy env\local.env .env
```
Then:
```
docker compose -f docker-compose.yml build --no-cache
docker compose -f docker-compose.yml up
```


### To run tests:
For Linux users:
```
cp env/testing.env .env
```
For Windows:
```
copy env\testing.env .env
```
Then:
```
docker compose -f docker-compose.yml build --no-cache
docker compose -f docker-compose.yml up
```


### Authorization:
To every your requests you have to add authorization header:
```
Authorization: Bearer 1a9b7f47c9454e4fb8d1e2aa9013f6d4
```