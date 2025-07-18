# Transaction system
I decided to split the application into two modules, first transactions and the other reports. Such division was due to the required to implement endpoints with prefix reports/ and transactions/. This gives a clear division of responsibilities of each application.
Intentionally in the endpoints with reports and file loading I used function based view and in those related to downloading transactions I used class based view. Thanks to this, in the case of potentially longer responding urls only the view defined by me is executed, which shortens the response time, and in the case of ends with transactions and CBV we get automatic pagination handling.

You can check transactions in django admin panel.
The default admin credentials are created by entrypoint.sh:
```
http://localhost:8080/admin
user:admin
password:admin
```


### Logging:
Logging was implemented using regular loggers in case of production you can implement sentry.  In the case of exposing the application to k8s, these logs will be captured by kubernetss which will enable accurate debugging. 

### Authorization:
In order to implement simple authorization, I thought the best idea would be to create a new middleware that checks for the presence of a valid token in the header before each request.
For every request, you must add the authorization header:
```
Authorization: Bearer 1a9b7f47c9454e4fb8d1e2aa9013f6d4
```

In order to keep the code consistent and readable, I implemented a pre-commit with black, isort, flake8, mypy modules.

### To start app:
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

By default, the app is accessible via:
```
http://localhost:8080/
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

### Upload csv file example:
```
curl -X POST -H "Authorization: Bearer 1a9b7f47c9454e4fb8d1e2aa9013f6d4" -F "file=@your_file_name.csv" http://localhost:8080/transactions/upload/
```