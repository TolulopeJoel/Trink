from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, Response, status

from services.plaid import PlaidService


class GetLinkTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Generate a Plaid Link token for the authenticated user.
        """
        if token := PlaidService.create_link_token(str(request.user.id)):
            return Response(token)

        return Response(
            {'error': 'Failed to generate link token'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class ExchangePublicTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Exchange public token and store access token for the user.
        """
        public_token = request.data.get('public_token')
        if not public_token:
            return Response(
                {'error': 'Public token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        token_response = PlaidService.exchange_public_token(public_token)
        access_token = token_response.get('access_token')

        if not access_token:
            return Response(
                {'error': 'Invalid token exchange response'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        profile = self.request.user.profile
        profile.plaid_token = access_token
        profile.save()
        return Response({'message': '"Successfully exchanged Plaid public token'})
