import logging

from django.core.management import call_command
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import SubCategory

logger = logging.getLogger(__name__)


@receiver(post_migrate)
def run_on_migrate(sender, **kwargs):
    if sender.name == "apps.categories":
        if not SubCategory.objects.exists():
            logger.info("SubCategory table is empty. Importing categories from seed file.")
            call_command("import_categories", "./seed_file.csv")
