# Food Recipe Application API
## The Structure and Source Code of the Django web application called "food recipe".

# ----------------------------------------------------------------------

## How to be sure that the code works in your machine:
    1) Install Python and Configure Python
    2) Install Docker and Configure Docker
    3) Configure all other necessary tools (like Travis CI, Linting options)
#
## Getting Started:
### 1) Clone Food Recipe Application Project Repository into your local machine:
```
git clone <repo_name>
```
### 2) Build a Docker image and container on your machine with this code:
```
docker-compose build
```
### 3) If you want to check whether unit tests and linting pass or not (I wrote 51 tests and all of them passed):
```python
docker-compose run --rm app sh -c "python manage.py test && flake8"
```
### 4) Start Project by running server in docker container where the application is installed:
```docker
docker-compose up
```
#### After running a server, API will be available through this link:
http://127.0.0.1:8000

# ----------------------------------------------------------------------

# Project Capabilities
## Note: This project was constructed following all rules of PEP8 and TDD(Test Driven Development) process.
## User Creation, User Authentication and Permissions
- Created custom user model, and custom user manager.
- Applied the feature to login trough email instead of username
- Added custom create_user and create_superuser functions (meaning that the user can be created by using email field)
- Added permission roles, meaning that Super User has full rights provide to simple users staff status, or Full control over Django Admin Panel (aka. Django database admin panel)
- Token authentication. Added an extra layer of authentication in terms of token authentication.
- Generate Token to each user
- Added features "create, update, validate" users
- Unit testing all the features mentioned above

#### Django User Create Path From Front to DB
![Django User Create Path From Front to DB](https://user-images.githubusercontent.com/69118015/129601641-baf82cae-326e-4919-810a-19fe6586daf9.png)


## Models, Serializers, Views
- Added models for creating custom user and custom user manager
- Added models for Tag, Ingredient, Recipe in order to form objects in the database
- Added different serializers in order to transform data from db to specific format and vice verse(from specific format to language objects(python))
- Added Views in order to control the data input and output through serializers to API
- Unit testing all the features mentioned above

![User Serializer](https://user-images.githubusercontent.com/69118015/129601917-4d5739e2-40d0-48d9-8359-3b906cde24e2.png)

## Database
- As a Database PostgreSQL was chosen
- Configured PostgreSQL by connecting to the Docker container and Django framework
- All of the models are created in PostgreSQL
- Noted the mistake during Django and PostgreSQL integration. It occurs that Django tries to run before the PostgreSQL, that causes an error. 
- Added the feature to solve the error by providing db_wait function that makes the django to wait until the database is not available.
- Unit testing all the features mentioned above

## API management
- Implemented a fully functioning REST API using DRF(Django Rest Framework)
- Implemented all HTTP CRUD methods through APIView
- Implemented all inner "create, retrieve, list, update, partial_update, destroy" method through ViewSet 
#### Endpoints along with Brief Descriptions: ***Note that all data you see in API returned and formated in JSON format.***
    User:
    - 127.0.0.1:8000/admin             -> Access Django Admin Panel.
    - 127.0.0.1:8000/api/user/create   -> Create a user (Authentication not needed).
    - 127.0.0.1:8000/api/user/token    -> Generate Token in order to access "Authentication required" services. 
    - 127.0.0.1:8000/api/user/me       -> Update created current active user's information (Authentication required). 
                                          In order to be authenticated user needs to generate his/her unique token and
                                          authenticate with it by putting authentication token as a 'Authorization' header.
                                          Example: Authorization    Token 12b256ac456b5465n564t
    Recipe:                            
    - 127.0.0.1:8000/api/recipe                         -> To get endpoints registered to recipe (Authentication not needed).
    - 127.0.0.1:8000/api/recipe/tags                    -> Returns all tags assigned to a logged in user (Authentication required).
    - 127.0.0.1:8000/api/recipe/tags/?assigned_only=1   -> Filters/Returns all tags assigned to specific recipe(s) (Authentication required).
    
    - 127.0.0.1:8000/api/recipe/ingredients                    -> Returns all ingredients assigned to a logged in user (Authentication required).
    - 127.0.0.1:8000/api/recipe/ingredients/?assigned_only=1   -> Filters/Returns all ingredients assigned to specific recipe(s) (Authentication required).
    
    - 127.0.0.1:8000/api/recipe/recipes                    -> Returns all created recipes, and also allows to create recipes through POST method (Authentication required).
    - 127.0.0.1:8000/api/recipe/recipes/<recipe_id>        -> Retrieve a recipe with a given id (Authentication required). Also there are features to update(put, patch)
                                                              retrieved specific recipe, and delete(destroy, delete).
    - 127.0.0.1:8000/api/recipe/recipes/?tags=<recipe_id>         -> Filter recipes by given tag id. It will return all recipes in which given
                                                                     tag was assigned (Authentication required).
    - 127.0.0.1:8000/api/recipe/recipes/?ingredients=<recipe_id>  -> Filter recipes by given ingredient id. It will return all recipes in which given 
                                                                     ingredient was assigned (Authentication required).
    - 127.0.0.1:8000/api/recipe/recipes/?tags=<recipe_id>&ingredients=<recipe_id>  -> Filter recipes by given tag id and ingredient id. It will return all recipes in which given 
                                                                                      tag and ingredient were assigned (Authentication required).                                                           
## Filtering Feature
- Implemented Filtering Feature
- Filter by Tags, by Ingredients, and in recipe filter by both of them


# Other project related resources
## Viewset vs APIView

I would call Viewset dynamic comparing to APIView because Viewset dynamically identifies what action is being performed, and it will link dynamically a particular url to the specific action. 
#### example: 
     - "list"    -> common_router  -> .../list/     (they will all be dynamically generated in url)
     - "create"  -> common_router  -> .../create/..
     - "destroy" -> common_router  -> .../delete/.. 
     
                                                 
On the other hand, APIView works on the standart way of how the HTTP methods work, meaning that each action needs to be manually linked to the specific url.  
#### example: 
    - "post"   ->  .../create/    (it should be done manually),
    - "update" ->  .../update/... 

#### How ViewSet works:
![Viewset](https://user-images.githubusercontent.com/69118015/129601459-e26583fb-2692-450c-8db8-1f6eef318ad3.png)

#### ViewSet Methods:
![ViewSet API functions](https://user-images.githubusercontent.com/69118015/129601114-e160d80d-2ea3-4ae1-95eb-e65f04598e20.jpg)

#### APIView Methods:
![APIView API](https://user-images.githubusercontent.com/69118015/129601240-da7ff694-8c80-4ee3-be2f-136fada4d000.png)

## About Serializers in Django Rest Framework:

https://micropyramid.com/blog/django-rest-framework-send-extra-context-data-to-serializers/


## How to Implement Token Authentication using Django REST Framework

https://simpleisbetterthancomplex.com/tutorial/2018/11/22/how-to-implement-token-authentication-using-django-rest-framework.html


## Some advises on how to manage branches in Git

https://geekflare.com/delete-github-branch/

## Serializer Relations

https://www.django-rest-framework.org/api-guide/relations/#primarykeyrelatedfield

## How to efficiently use Serializers in Django
https://opensource.com/article/20/11/django-rest-framework-serializers

## Understanding the Python Mock Object Library
https://realpython.com/python-mock-library/#managing-a-mocks-side-effects
