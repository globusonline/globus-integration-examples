import json
import requests
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from rest_framework import exceptions
from rest_framework.authentication import get_authorization_header, BaseAuthentication
from restapi.models import AccessToken


UserModel = get_user_model()


class GlobusAuthentication(BaseAuthentication):

    def authenticate(self, request):
        """
        Returns two-tuple of (user, token) if authentication succeeds,
        or None otherwise.
        """

        auth = get_authorization_header(request).split()

        if len(auth) == 1:
            msg = 'Invalid bearer header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = 'Invalid bearer header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)
        elif auth[0].lower() != b'bearer':
            msg = 'Invalid bearer header. Missing Bearer'
            raise exceptions.AuthenticationFailed(msg)

        access_token = auth[1]

        """ Introspect the token """
        resp = requests.post(
                settings.GLOBUS_INTROSPECTION_URL,
                data={'token': access_token},
                auth=(settings.GLOBUS_CLIENT_ID, settings.GLOBUS_CLIENT_SECRET)
        )
        content = resp.json()
        user = None
        if "active" in content and content["active"] is True:
            if "username" in content:
                user, _created = UserModel.objects.get_or_create(
                    **{UserModel.USERNAME_FIELD: content["username"]}
                )
                dependent_token = self.dependent_token(access_token)
                at = AccessToken.objects.filter(user=user)
                if len(at):
                    at[0].access_token = access_token
                    at[0].dependent_token = dependent_token
                    at[0].save()
                else:
                    AccessToken.objects.create(user=user, access_token=access_token, dependent_token=dependent_token)

        return user, None

    def dependent_token(self, access_token):
        """
        Get dependent token
        """

        resp = requests.post(
                settings.GLOBUS_DEPENDENT_TOKEN_URL,
                data={
                    'grant_type': 'urn:globus:auth:grant_type:dependent_token',
                    'token': access_token
                },
                auth=(settings.GLOBUS_CLIENT_ID, settings.GLOBUS_CLIENT_SECRET)
        )
        content = resp.json()
        return content[0]['access_token']
