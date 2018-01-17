Atlassian Confluence and JIRA
=============================

Configuring Atlassian Confluence and JIRA to authenticate user access using Globus Auth and the OpenID protocol.

Globus Auth implements a standard `OpenID Connect`_ (OIDC) service accesible using an existing OpenID Authentication add-on for Confluence and JIRA. This external OpenID authentication may be used for unprivileged user access. For privileged adminstrative access Confluence and JIRA require the administrator to use an `internal password`_.

.. _`OpenID Connect`: http://openid.net/connect/
.. _`internal password`: https://confluence.atlassian.com/adminjiraserver071/configuring-secure-administrator-sessions-802593160.html

Before you can start
--------------------

Login to Confluence or JIRA as an administrator.

Install the plug-in
-------------------

1. Navigate to "Administration -> Atlassian Marketplace -> Find new add-ons" and search for the "OpenID Authentication" add-on for Confluence or JIRA.

.. image:: atlassian-images/jira-openid-marketplace.jpg
   :width: 100%

2. Install the OpenID Authentication add-on from Pavel Niewiadomski.
3. Obtain and configure a full license or trial license.

Configure the OpenID plug-in
----------------------------

5. Navigate to "Administration -> Atlassian Marketplace -> Manage add-ons".
6. Under OpenID Authentication for Confluence (or JIRA) select the “Configure” option.
7. Under Providers select “Add Provider”.

.. image:: atlassian-images/jira-openid-providers.jpg
   :width: 100%

In “Add Authentication Provider”:

8. Select provider “OpenID Connect/OAuth 2.0”.
9. Enter:

   Name “My Login” (or whatever label you want users to see on the login window).

   Provider URL “https://auth.globus.org”.

10. Copy the generated Callback URL to place in the Redirects field when registering your Confluence or JIRA application with Globus Auth in the following step.

11. In a new Incognito Browser Window follow the `application registration instructions`_ in the Globus Auth Developer's Guide.

.. _`application registration instructions`: https://docs.globus.org/api/auth/developer-guide/#register-app

12. Copy the newly generated Client Secret for the Confluence or JIRA application registered in Globus Auth.

.. image:: atlassian-images/GlobusApplications.jpg
   :width: 100%

13. Return to the Confluence or JIRA provider registration window.
14. Paste the Client Secret generated for the Confluence or JIRA application registered in Globus Auth above.
15. Enter the Scope “openid email profile”.
16. Leave “Allowed Domains” blank.
17. Select Authentication prompt “consent”.
18. Click “Add Provider”.
19. Make sure “Automatically Create Users” has the desired value.

Test the plug-in
----------------

From a new Incognitor Browser Window access your Confluence or JIRA service and authenticate using "Your Login".
