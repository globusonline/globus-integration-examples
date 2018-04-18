import requests
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from restapi.authentication import GlobusAuthentication
from restapi.models import AccessToken


class EndpointAPIView(APIView):
    authentication_classes = (GlobusAuthentication,)
    renderer_classes = (JSONRenderer,)

    def get(self, request, format=None):
        user = request.user
        dependent_token = AccessToken.objects.get(user=user).dependent_token
        resp = requests.get(
                'https://transfer.api.globus.org/v0.10/endpoint_search',
                params={'filter_scope': 'recently-used'},
                headers={'Authorization': 'Bearer {}'.format(dependent_token)})
        return Response(resp.json())
