from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Pension, PensionAccount

User = get_user_model()

class PensionModelTests(TestCase):

    def test_create_pension(self):
        pension = Pension.objects.create(
            name='Test Pension',
            payBill_number='1234567890',
            status='Active'
        )
        self.assertEqual(pension.name, 'Test Pension')
        self.assertEqual(pension.payBill_number, '1234567890')
        self.assertEqual(pension.status, 'Active')
        self.assertIsNotNone(pension.created_at)
        self.assertIsNotNone(pension.updated_at)

    def test_pension_str(self):
        pension = Pension.objects.create(name='Test Pension', payBill_number='123', status='Active')
        self.assertEqual(str(pension), 'Test Pension')


class PensionAccountModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='manager@example.com',
            password='testpass123',
            first_name='Manager',
            last_name='One',
            user_type='MANAGER',
            phone_number='+254700000001'
        )

    def test_create_pension_account(self):
        pension_account = PensionAccount.objects.create(
            member=self.user,
            total_pension_amount=1000.00,
            is_opted_in=True,
            contribution_percentage=5.00,
        )
        self.assertEqual(pension_account.member, self.user)
        self.assertEqual(pension_account.total_pension_amount, 1000.00)
        self.assertTrue(pension_account.is_opted_in)
        self.assertEqual(pension_account.contribution_percentage, 5.00)
        self.assertIsNotNone(pension_account.created_at)
        self.assertIsNotNone(pension_account.updated_at)

    def test_pension_account_str(self):
        pension_account = PensionAccount.objects.create(
            member=self.user,
            total_pension_amount=1000.00,
            is_opted_in=False,
            contribution_percentage=3.50,
        )
        self.assertEqual(str(pension_account), f"PensionAccount {self.user}")