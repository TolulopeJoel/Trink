import logging
from decimal import Decimal

from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, Response, status

from apps.categories.models import SubCategory
from apps.transactions.models import StoreItem, StoreTransaction
from services.ocr import get_receipt_data

logger = logging.getLogger(__name__)

class ExtractReceiptAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def clean_price(self, price):
        return Decimal(price.replace(',', ''))

    def post(self, request, *args, **kwargs):
        """
        Extract receipt data from an image.
        """
        if 'image' not in request.FILES:
            return Response(
                {"error": "No image file provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if ocr_data := get_receipt_data(request.FILES['image']):
            with transaction.atomic():
                store_transaction = StoreTransaction.objects.create(
                    user=request.user,
                    store_name=ocr_data['store_name'],
                    transaction_date=ocr_data['date_time'],
                    amount=self.clean_price(ocr_data['total_amount']),
                )

                subcategories = {
                    sc.name: sc for sc in SubCategory.objects.all()
                }

                for item in ocr_data['items']:
                    new_item = StoreItem.objects.create(
                        transaction=store_transaction,
                        name=item['name'],
                        quantity=int(float(item['quantity'])),
                        unit_price=self.clean_price(item['unit_price']),
                        total_amount=self.clean_price(item['total_price']),
                    )

                    if subcategory := subcategories.get(item['category']):
                        new_item.subcategories.add(subcategory)
                    else:
                        logger.error(f"Subcategory not found: {item['category']}")
            
            return Response(
                {"message": "Receipt data extracted and stored successfully."},
                status=status.HTTP_201_CREATED
            )

        return Response(
            {"error": "Failed to extract receipt data."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
