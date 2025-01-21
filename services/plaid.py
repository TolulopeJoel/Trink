import logging
import time
from typing import Any, Dict, List, Optional

import plaid
from django.conf import settings
from plaid.api import plaid_api
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import \
    ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import \
    LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.transactions_sync_request import TransactionsSyncRequest

logger = logging.getLogger(__name__)


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
    def create_link_token(cls, user_id: str, products: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a Plaid link token for a specific user.
        """
        logger.info(f"Creating Plaid link token for user_id: {user_id}")
        try:
            request = LinkTokenCreateRequest(
                language='en',
                client_name=settings.APPLICATION_NAME,
                products=[Products(p) for p in (
                    products or ['auth', 'transactions'])],
                country_codes=[CountryCode('US')],
                redirect_uri=settings.PLAID_REDIRECT_URI,
                user=LinkTokenCreateRequestUser(client_user_id=user_id)
            )

            response = cls.client.link_token_create(request)
            logger.info(f"Successfully created link token for user_id: {user_id}")
            return response.to_dict()

        except plaid.ApiException as e:
            logger.error(
                f"Failed to create Plaid link token for user_id: {user_id}. "
                f"Error code: {e.status}, message: {e.body}",
                exc_info=True
            )
            return {}

    @classmethod
    def exchange_public_token(cls, public_token: str) -> Dict[str, Any]:
        """
        Exchange a public token for an access token.
        """
        logger.info("Initiating public token exchange")
        try:
            plaid_request = ItemPublicTokenExchangeRequest(
                public_token=public_token
            )

            response = cls.client.item_public_token_exchange(plaid_request)
            logger.info("Successfully exchanged public token for access token")
            return response.to_dict()
        except plaid.ApiException as e:
            logger.error(
                "Failed to exchange public token. "
                f"Error code: {e.status}, message: {e.body}",
                exc_info=True
            )
            return {}

    @classmethod
    def get_accounts(cls, access_token: str) -> Dict[str, Any]:
        """
        Retrieve a list of user's accounts information
        """
        try:
            request = AccountsGetRequest(
                access_token=access_token
            )
            accounts_response = cls.client.accounts_get(request)
            logger.info(f"Successfully retrieved {len(accounts_response.accounts)} accounts")
            return accounts_response.to_dict().get('accounts')

        except plaid.ApiException as e:
            logger.error(
                "Failed to retrieve accounts. "
                f"Error code: {e.status}, message: {e.body}",
                exc_info=True
            )
            return {}

    @classmethod
    def get_transactions(cls, profile) -> List[Dict[str, Any]]:
        """
        Retrieve transactions for a user profile.
        """
        cursor = profile.next_cursor
        access_token = profile.plaid_token

        logger.info(f"Starting transaction sync for profile ID: {profile.id}")
        added = []  # New transaction updates since "cursor"
        has_more = True

        try:
            # Iterate through each page of new transaction updates
            while has_more:
                request = TransactionsSyncRequest(
                    access_token=access_token,
                    cursor=cursor,
                )
                response = cls.client.transactions_sync(request).to_dict()
                cursor = response['next_cursor']

                # If no transactions are available yet, wait and poll the endpoint
                if cursor == '':
                    logger.debug("No transactions available yet, polling...")
                    time.sleep(2)
                    continue

                added.extend(response['added'])
                has_more = response['has_more']

                logger.info(f"Retrieved {len(added)} new transactions. Has more: {has_more}")

                # Save the cursor for future requests
                profile.next_cursor = cursor
                profile.save()

            logger.info(f"Completed transaction sync. Total transactions retrieved: {len(added)}")
            return added

        except plaid.ApiException as e:
            logger.error(
                f"Failed to export transactions for profile ID: {profile.id}. "
                f"Error code: {e.status}, message: {e.body}",
                exc_info=True
            )
            return []
