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
        "store_name": "str"
        "date_time": "str (ISO 8601 standard)",
        "total_amount": "str",
        "items": [{{
            "name": "str",
            "quantity": "str",
            "unit_price": "str",
            "total_price": "str",
            "category": "str (select a single category from the list: {subcatgories_string})"
        }}]
    }}

    Return: dict[Transaction]
    """

    response = model.generate_content([prompt, image])
    json_string = response.text

    cleaned_string = json_string.replace("```json\n", "").replace("\n```", "")

    return json.loads(cleaned_string)