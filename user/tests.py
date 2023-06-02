from django.test import TestCase
from .models import User
from .models import StaffMember
from .models import Admin


class UserTestCase(TestCase):
    def setUp(self):
        self.credentials = {
            'email': 'test_email@mail.com',
            'username': 'test_username',
            'full_name': 'Test Full Name',
            'password': 'test_password',
        }

    def test_user_creates_user(self):
        user = User.objects.create_user(**self.credentials)
        self.assertEqual(User.objects.filter(id=user.id).count(), 1)

    def test_creates_staff_member(self):
        user = User.objects.create_staff_member(**self.credentials)
        self.assertTrue(user.is_staff_member)
        self.assertEqual(StaffMember.objects.filter(user=user).count(), 1)

    def test_creates_admin(self):
        user = User.objects.create_superuser(**self.credentials)
        self.assertTrue(user.is_superuser)
        self.assertEqual(Admin.objects.filter(user=user).count(), 1)

    def test_removes_user(self):
        user = User.objects.create_user(**self.credentials)
        deleted_user_id = user.id
        user.delete()
        self.assertEqual(User.objects.filter(id=deleted_user_id).count(), 0)

    def test_removes_staff_member_if_user_was_removed(self):
        user = User.objects.create_staff_member(**self.credentials)
        staff_member = user.staffmember_set.get().user
        user.delete()
        self.assertEqual(StaffMember.objects.filter(user=staff_member).count(), 0)

    def test_removes_admin_member_if_user_was_removed(self):
        user = User.objects.create_superuser(**self.credentials)
        admin = user.admin_set.get().user
        user.delete()
        self.assertEqual(Admin.objects.filter(user=admin).count(), 0)

    def test_staff_member_removes_if_is_staff_status_sets_to_false(self):
        user = User.objects.create_staff_member(**self.credentials)
        user.is_staff_member = False
        user.save()
        self.assertEquals(StaffMember.objects.filter(user=user).count(), 0)

    def test_staff_member_creates_if_staff_status_sets_to_true(self):
        user = User.objects.create(**self.credentials)
        user.is_staff_member = True
        user.save()
        self.assertEquals(StaffMember.objects.filter(user=user).count(), 1)

    def test_admin_removes_if_is_superuser_status_sets_to_false(self):
        user = User.objects.create_superuser(**self.credentials)
        user.is_superuser = False
        user.save()
        self.assertEquals(Admin.objects.filter(user=user).count(), 0)

    def test_admin_creates_if_superuser_sets_to_true(self):
        user = User.objects.create(**self.credentials)
        user.is_superuser = True
        user.save()
        self.assertEquals(Admin.objects.filter(user=user).count(), 1)
