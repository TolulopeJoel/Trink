import logging

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, Response, status

from .services import get_receipt_data

logger = logging.getLogger(__name__)

class ExtractReceiptAPIView(APIView):
    permission_classes = [IsAuthenticated]

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
            return Response({**ocr_data})

        return Response(
            {"error": "Failed to extract receipt data."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
