from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Тестовая команда'

    def handle(self, *args, **options):
        self.stdout.write('Тест работает!')
