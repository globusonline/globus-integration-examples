# Django REST Framework integrated with Globus Auth

Simple resource server built using Django REST Framework with the Globus Auth OAuth2 server as a remote authentication service.
The main part of the resource server is the GlbousAuthentication class (a subclass of BaseAuthentication class) that is responsible for extracting an access token from a request from a client, introspecting the access tokens against the Globus Auth, adding a new user to the resource server database, exchanging the access tokens to dependent tokens from the Globus Auth and storing the tokens in the database.
The resource server also provides an example view that calls the Transfer API to get a list of endpoints.
The view shows how to use dependent tokens to talk to Globus Services on behalf of a user.

## Install the web app

Create Python 2.7 virtual environment
```
$ python --version
Python 2.7.10
$ virtualenv venv
$ . venv/bin/activate
```
Download and install the REST API app with all required Python packages (Django, Python Social Auth, etc.)
```
(venv)$ git clone https://github.com/globusonline/globus-integration-examples.git
(venv)$ cd src/django-rest-framework/restapi
(venv)$ pip install -r requirements.txt
```
Create the database
```
(venv)$ ./manage.py migrate
```
## Register a resource server client

All OAuth2 clients need to register with Globus Auth to get a client id and secret. To register a client, go to `https://developers.globus.org/`, click 'Register your app with Globus', add a new project and add a new app in the project.
Enter a name of your app you want to be shown to users when they are asked for a consent when redirected to Globus Auth for authentication. Enter any URI as the redirect URI.
Click 'Create App'. Click 'Generate New Client Secret' and copy Client ID and a generated secret to `restapi/register_rs.py` script. Clients registered on `https://developers.globus.org` do not have `dependent_token` grant type and cannot be used by a resource server. However, they can be used to authenticate to the Globus Auth API to create a child client with dependent_token grant type and create a resource server scope.
The `restapi/register_rs.py` does all of this. Please run the script, and copy the child client id, a parent client secret, a resource server scope to `restapi/ttings.py` as `GLOBUS_CLIENT_ID`, `GLOBUS_CLIENT_SECRET`, `GLOBUS_SCOPE`.

## Apache/mod_wsgi

For example, on Ubuntu, add the following lines to /etc/apache2/sites-available/default-ssl.conf in `<VirtualHost _default_:443>`
```
    WSGIDaemonProcess globusrestapi user=<your_username> python-path=<your_base_dir>/restapi:<your_base_dir>/venv/lib/python2.7/site-packages
    WSGIScriptAlias /<prefix> <your_base_dir>/restapi/restapi/wsgi.py process-group=globusrestapi
    <Directory <your_base_dir>/restapi/restapi>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>
```
Restart Apache and run
```
$ curl -k -H 'Authorization: Bearer <access_token>' -H 'Accept: application/json; indent=4' https://drf.example.com/endpoint/
```
If you do not own `drf.example.com` domain, you may need to add:
```
127.0.0.1 drf.example.com
```
to your `/etc/hosts`.

