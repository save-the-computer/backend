from django.core.management.base import BaseCommand
from products.tasks import collect


class Command(BaseCommand):
    help = 'Manually collect product specs and products data'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        collect.apply_async()
