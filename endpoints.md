|**Endpoint** | **Description**| **Parameters**|
|---|---|---|
|/auth/users/| Register a new user | username, email and password |
| /auth/users/me/ | retrieve/update the currently logged in user | Bearer Token |
| /auth/jwt/create/| create a JWT by passing a valid user in the post request to this endpoint| username and password |
|/auth/jwt/refresh/ | get a new JWT once the lifetime of the previously generated one expires |username, password and refresh
|/api/account/profile/{user-id} | Update user properties|  Bearer Token |
|/api/account/all-profiles | get all users |  Bearer Token |