import plaid
from django.conf import settings
from plaid.api import plaid_api
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import \
    ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import \
    LinkTokenCreateRequestUser
from plaid.model.products import Products


class PlaidService:
    """Service for handling Plaid API interactions."""
    _configuration = plaid.Configuration(
        host=plaid.Environment.Sandbox,
        api_key={
            'clientId': settings.PLAID_CLIENT_ID,
            'secret': settings.PLAID_SECRET,
            'plaidVersion': '2020-09-14'
        }
    )
    _api_client = plaid.ApiClient(_configuration)
    client = plaid_api.PlaidApi(_api_client)

    @classmethod
    def create_link_token(cls, user_id: str, products: list = None) -> dict:
        """
        Create a Plaid link token for a specific user.
        """
        try:
            request = LinkTokenCreateRequest(
                language='en',
                client_name=settings.APPLICATION_NAME,
                products=[Products(p) for p in (products or ['auth'])],
                country_codes=[CountryCode('US')],
                redirect_uri=settings.PLAID_REDIRECT_URI,
                user=LinkTokenCreateRequestUser(client_user_id=user_id)
            )

            response = cls.client.link_token_create(request)
            return response.to_dict()
        except Exception as e:
            # Log the error for debugging, Error creating link token: {e}
            return {}

    @classmethod
    def exchange_public_token(cls, public_token: str) -> dict:
        """
        Exchange a public token for an access token.
        """
        try:
            plaid_request = ItemPublicTokenExchangeRequest(
                public_token=public_token
            )

            response = cls.client.item_public_token_exchange(plaid_request)
            return response.to_dict()
        except Exception as e:
            # Log the error for debugging, Error exchanging public token: {e}
            return {}
