import csv

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.category.models import Category, SubCategory


class Command(BaseCommand):
    help = 'Import categories from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def _normalize_name(self, name):
        """Convert names to a consistent format"""
        return " ".join(name.split("_")).lower()

    def _extract_subcategory_name(self, primary_category, detailed_category):
        """Extract subcategory name by removing primary category words"""
        primary_words = self._normalize_name(primary_category).split()
        detailed_words = self._normalize_name(detailed_category).split()
        return " ".join(detailed_words[len(primary_words):])

    @transaction.atomic
    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        
        # Read CSV and process data
        with open(csv_file_path, 'r') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Skip header

            # Collect and create primary categories
            unique_categories = set(
                self._normalize_name(row[0]) for row in reader
            )

            # Create primary categories
            for cat_name in unique_categories:
                Category.objects.get_or_create(name=cat_name)

            # Reset file reader
            csvfile.seek(0)
            next(reader)  # Skip header again

            # Create subcategories
            for row in reader:
                primary_category = self._normalize_name(row[0])
                detailed_category = row[1]
                description = row[2]

                # Get primary category
                primary_cat_obj = Category.objects.get(name=primary_category)

                # Extract and normalize subcategory name
                subcategory_name = self._extract_subcategory_name(row[0], detailed_category)

                # Create subcategory
                SubCategory.objects.get_or_create(
                    category=primary_cat_obj,
                    name=subcategory_name,
                    defaults={'description': description}
                )

        self.stdout.write(self.style.SUCCESS('Successfully imported categories'))