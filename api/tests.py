
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import Member
from .models import SavingsAccount, SavingsContribution, VSLA_Account

class SavingsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.member = Member.objects.create(member_id="M001")
        self.savings_account = SavingsAccount.objects.create(
            saving_id="SA001",
            member=self.member,
            member_account_balance=0.00,
            interest_incurred=0.00
        )
        self.vsla_account = VSLA_Account.objects.create(
            vsla_id=1,
            account_name="Main VSLA Pool",
            account_balance=0.00
        )

    def test_create_member(self):
        url = reverse('member-list')
        data = {"member_id": "M002"}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Member.objects.count(), 2)

    def test_create_savings_account(self):
        url = reverse('savingsaccount-list')
        data = {
            "saving_id": "SA002",
            "member_id": "M001",
            "member_account_balance": "1500.00",
            "interest_incurred": "75.00"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SavingsAccount.objects.count(), 2)

    def test_create_contribution_with_pension(self):
        url = reverse('savingscontribution-list')
        data = {
            "contribution_id": "C001",
            "saving_id": "SA001",
            "contributed_amount": "1000.00",
            "pension_percentage": "10.00"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        contribution = SavingsContribution.objects.get(contribution_id="C001")
        self.assertEqual(float(contribution.pension_amount), 100.00)
        self.assertEqual(float(contribution.vsla_amount), 900.00)

    def test_create_contribution_no_pension(self):
        url = reverse('savingscontribution-list')
        data = {
            "contribution_id": "C002",
            "saving_id": "SA001",
            "contributed_amount": "800.00",
            "pension_percentage": "0.00"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        contribution = SavingsContribution.objects.get(contribution_id="C002")
        self.assertEqual(float(contribution.pension_amount), 0.00)
        self.assertEqual(float(contribution.vsla_amount), 800.00)

    def test_contribution_updates_vsla_balance(self):
        self.vsla_account.account_balance = 0.00
        self.vsla_account.save()

        url = reverse('savingscontribution-list')
        data = {
            "contribution_id": "C003",
            "saving_id": "SA001",
            "contributed_amount": "500.00",
            "pension_percentage": "20.00"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.vsla_account.refresh_from_db()
        self.assertEqual(float(self.vsla_account.account_balance), 400.00)  

    def test_get_vsla_account(self):
        url = reverse('vslaaccount-detail', args=[1])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['account_name'], "Main VSLA Pool")

    def test_create_vsla_account(self):
        url = reverse('vslaaccount-list')
        data = {
            "account_name": "Emergency Fund",
            "account_balance": "5000.00"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(VSLA_Account.objects.count(), 2)