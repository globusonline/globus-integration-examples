Tornado
======

`Tornado`_ is a Python web framework and asynchronous networking library. 
Request handlers in Tornado web applications that take advantage of 
non-blocking network I/O, have to be implemented in a certain way, 
different than in web apps built based on frameworks like `Django`_ or `Flask`_.
This section shows how to create a simple Tornado web app with a Globus login handler. 
The Globus login handler extends ``tornado.auth.OAuth2Mixin`` class from Tornado version 6. 
If you need to use an older version of Tornado, please check out the corresponding handler and example at 
`tornado_v5 <https://github.com/globusonline/globus-integration-examples/tree/master/src/tornado/tornado_v5/>`_

Develop web app
------------------------

First, we will create a virtual environment named ``venv``, activate it to run our web application in the environment and install Tornado:

.. code-block:: bash

   $ python3 -m venv venv
   $ . venv/bin/activate
   $ pip install tornado


We will start developing the web app from the minimal `hello world <https://www.tornadoweb.org/en/stable/guide/structure.html>`_ example 
on the official Tornado documentation, and will be modifying it to add Globus OAuth2 authentication. 
First, we will extend the ``MainHandler`` to show ``Login`` and ``Logout`` links, and, when a user is logged in which means ``user_id`` cookie set, 
display information about the user. To do this, we will use the Tornado template (``home.html``):

.. code-block:: html

    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Tornado Web App</title>
    </head>
    <body>
        <div>
        <h1>Tornado web app with authentication delegated to Globus Auth</h1>
        <p>
             <br/>
        {% if user_id %}
            Hello {{ name }}!<br/>
            &nbsp; Username: {{ username }}<br/>
            &nbsp; Email: {{ email }}<br/>
            &nbsp; UUID: {{ user_id }}<br/>
            &nbsp; Organization: {{ organization }}<br/>
            &nbsp; Access token: {{ access_token }}<br/>
            &nbsp; Refresh token: {{ refresh_token }}<br/>
            <br/>
            <a href="/logout">Logout</a>
        {% else %}
            <a href="/login">Login to Globus</a>
        {% end %}
        </p>
        </div>
    </body>
    </html>

The template shows user's information and ``Logout`` link when ``user_id`` is defined, and shows ``Login to Globus`` link otherwise. 
The ``MainHandler`` will extract user's information from cookies, that the app sets in the authentication process, and render the template.

.. code-block:: python

    class MainHandler(tornado.web.RequestHandler):
        def get_current_user(self):
            return self.get_secure_cookie("user_id")
    
        def get(self):
            self.render("home.html",
                        user_id=self.current_user,
                        username=self.get_secure_cookie("username"),
                        email=self.get_secure_cookie("email"),
                        name=self.get_secure_cookie("name"),
                        organization=self.get_secure_cookie("organization"),
                        access_token=self.get_secure_cookie("access_token"),
                        refresh_token=self.get_secure_cookie("refresh_token"))

When a user logs out, the ``user_id`` cookie must be cleared. We will do it in the ``LogoutHandler``:

.. code-block:: python

    class LogoutHandler(tornado.web.RequestHandler):
        async def get(self):
            self.clear_cookie("user_id")
            self.redirect("/")

The request from a user's web browser generated when the user click the ``Login`` link and the OAuth2 flow 
will be handled by a separate class:

.. code-block:: python

    class GlobusOAuth2LoginHandler(tornado.web.RequestHandler,
                                   globus.GlobusOAuth2Mixin):
        async def get(self):
            if self.get_argument("code", False):
                tokens = await self.get_tokens(
                    redirect_uri=self.settings["globus_oauth"]["redirect_uri"],
                    code=self.get_argument("code"))
                expires_at = int(time.time()) + tokens["expires_in"]
                user_info = await self.get_user_info(tokens["access_token"])
                # Save the user with e.g. set_secure_cookie
                self.set_secure_cookie("user_id", user_info["sub"], expires=expires_at-60)
                self.set_secure_cookie("username", user_info["preferred_username"])
                self.set_secure_cookie("email", user_info["email"])
                self.set_secure_cookie("name", user_info["name"])
                self.set_secure_cookie("organization", user_info["organization"])
                self.set_secure_cookie("access_token", tokens["access_token"])
                self.set_secure_cookie("refresh_token", tokens["refresh_token"])
                self.redirect("/")
            else:
                self.authorize_redirect(
                    redirect_uri=self.settings["globus_oauth"]["redirect_uri"],
                    client_id=self.settings["globus_oauth"]["key"],
                    scope=self.settings["globus_oauth"]["scope"],
                    response_type="code",
                    extra_params={"access_type": "offline"})

When a user clicks the ``Login`` link, the ``authorized_redirect()`` function in the ``else`` block is called. 
The functions is defined in one of the supper classes. The function redirects the user's web browser to Globus Auth. 
Once the user authenticates to Globus Auth, the user's web browser is redirected back to the web app. 
The redirection response comes with the ``code`` parameter set. The parameter is detected by ``get_argument()`` function. 
In the subsequent lines, the ``code`` is exchanged to access tokens, then one of the access tokens is used to get a user info, 
and the access tokens and user information are saved in cookies. Functions ``get_tokens()`` and ``get_user_info()`` are specific 
to Globus Auth and have to be implemented in a subclass of ``tornado.auth.OAuth2Mixin``, 
`GlobusOAuth2Mixin class <https://github.com/globusonline/globus-integration-examples/tree/master/src/tornado/globus.py/>`_.

Once we have all handlers implemented, we have to tie them with URLs: ``/``, ``/login``, ``/logout``. To do it, We will modify ``make_app()``:

.. code-block:: python

    def make_app():
        settings = {
            "cookie_secret": "32oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            "xsrf_cookies": True,
            "globus_oauth": {
                "key": "<Globus_OAuth2_Client_Id>",
                "secret": "<Globus_OAuth2_Client_Secret>",
                "redirect_uri": "https://<your_server_host_name>/login",
                "scope": [
                    "openid",
                    "profile",
                    "email",
                    "urn:globus:auth:scope:transfer.api.globus.org:all"
                ]
            }
        }
        handlers = [
            (r"/", MainHandler),
            (r"/login", GlobusOAuth2LoginHandler),
            (r"/logout", LogoutHandler),
        ]
        return tornado.web.Application(handlers, **settings)

To get OAuth2 client id and secret that you have to provide in ``settings``, register this web app on 
https://developers.globus.org with ``https://<your_server_host_name>/login`` as a redirect URL.

After all of the changes are made, you can run the app:

.. code-block:: bash

   $ python -m tornado.autoreload app.py

Configure Apache server
-----------------------

The web app can be run behind an reverse proxy server. If you use Debian-based system, for example Ubuntu, add the following lines to ``/etc/apache2/sites-available/default-ssl.conf`` in ``<VirtualHost _default_:443>`` section

.. code-block:: apache

        ProxyPass / http://127.0.0.1:8888/
        ProxyPassReverse / http://127.0.0.1:8888/

After restarting the Apache server, the application should be accessible at https://<your_server_host_name>/.

.. _Tornado: https://tornadoweb.org/
.. _Django: https://djangoproject.com/
.. _Flask: http://flask.pocoo.org/


