import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from utils.vectordb import get_vector_store, vectors_collection

from .models import BankTransaction, StoreTransaction

logger = logging.getLogger(__name__)


@receiver(post_save, sender=BankTransaction)
@receiver(post_save, sender=StoreTransaction)
def update_embeddings(sender, instance, created, *args, **kwargs):
    try:
        vector_document = instance.to_vector_document()
        vector_store = get_vector_store()

        if not created:
            vectors_collection.delete_one({'transaction_id': str(instance.id)})

        vector_store.add_documents([vector_document])

    except Exception as e:
        logger.error(f"Failed to update embeddings for {instance}: {e}")
