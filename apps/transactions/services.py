import json

import google.generativeai as genai
import PIL.Image
from django.conf import settings

from apps.categories.models import SubCategory

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel(settings.GEMINI_MODEL)


def get_receipt_data(image_path=None):
    image = PIL.Image.open(image_path)
    subcatgories = SubCategory.objects.values_list("name", flat=True)
    subcatgories_string = ", ".join(subcatgories)

    prompt = f"""
    Return the transaction details in the receipt in JSON format.
    Use this JSON schema: 
    Transaction = {{
        store_location: str,
        date_time: str (ISO 8601 standard),
        items: [{{
            category: str (select one from here: {subcatgories_string}),
            name: str,
            quantity: int,
            unit_price: float
        }}]
    }}
    Return: dict[Transaction]
    """

    response = model.generate_content([prompt, image])
    json_string = response.text

    cleaned_string = json_string.replace("```json\n", "").replace("\n```", "")
    transaction_data = json.loads(cleaned_string)

    if items := transaction_data.get('items', []):
        transaction_data['total_amount'] = sum(
            item['quantity'] * item['unit_price']
            for item in items
        )

    return transaction_data
