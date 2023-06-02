from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from user.models import User

UserModel = get_user_model()


class Command(BaseCommand):
    help = 'Prepare test superusers for develop'

    def handle(self, *args, **options):
        admin = User.objects.create_superuser('admin@mail.ru', 'admin')
        if admin:
            print("Superuser is created\nEmail: admin@mail.ru\nPassword: admin")
