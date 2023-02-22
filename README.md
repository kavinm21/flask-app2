# Interview schedule platform
A data store app for fulfilling Cloud Computing Coursework Requirements

# Tech Stack:
Mongo, Flask, Python

# API:


Vercel: https://flask-app2.vercel.app/

Azure: https://flaskselva.azurewebsites.net/

URL Suffix           | Functions
-------------        | -------------
/home                | Displays all the interview details
/interview/{int:id}  | Displays specific iterview details
/interview/update    | Updates an interview
/interview/delete    | Deletes an interview

Deploy Branch is deployed to the links mentioned above.
home and interview/id functionalities are currently active and the rest requires frontend for functioning.

## API Usage:


### 1. home:

send a GET request to     
```
https://flask-app2.vercel.app/home
```
or
```
https://flaskselva.azurewebsites.net/home
```

all available interviews are returned

the data is returned in JSON format


### 2. iterview/id:

send a GET request to
```
https://flask-app2.vercel.app/interview/{int:id}
```
or
```
https://flaskselva.azurewebsites.net/interview/{int:id}
```

the interview with the id mentioned is returned

the data is returned in JSON format


### 3. interview/update:
 

send a POST request to
```
https://flask-app2.vercel.app/interview/update
```
or
```
https://flaskselva.azurewebsites.net/interview/update
```

the interview with the id mentioned in JSON request is updated

return update status

    
### 4. interview/delete:
 

send a POST request to
```
https://flask-app2.vercel.app/interview/delete
```
or
```
https://flaskselva.azurewebsites.net/interview/delete
```

the interview with the id mentioned in JSON request is deleted

return delete status
