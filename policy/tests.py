from django.test import TestCase
from .models import Policy
from django.utils import timezone

class PolicyModelTests(TestCase):

    def test_create_policy(self):
        policy = Policy.objects.create(
            title='savings',
            description='SACCO policies ensure transparency, fairness, and accountability. All operations comply with regulations and protect member interests.',
            effective_date=timezone.now()
        )
        self.assertEqual(policy.title, 'savings')
        self.assertEqual(policy.description, 'SACCO policies ensure transparency, fairness, and accountability. All operations comply with regulations and protect member interests.')
        self.assertIsNotNone(policy.effective_date)
        self.assertIsNotNone(policy.created_at)
    
    def test_policy_str(self):
        policy = Policy.objects.create(
            title='loans',
            description='SACCO policies ensure transparency, fairness, and accountability. All operations comply with regulations and protect member interests.',
            effective_date=timezone.now()
        )
        expected_str = f"{policy.title} Policy ({policy.id})"
        self.assertEqual(str(policy), expected_str)