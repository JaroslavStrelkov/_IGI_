from django.test import TestCase
from django.contrib.auth.models import User

from apps.reviews.models import Review


class ReviewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='review_user', password='12345678Qq')
        self.review = Review.objects.create(user=self.user, rating=5, text='Excellent salon')

    def test_review_created(self):
        self.assertEqual(self.review.rating, 5)

    def test_review_text(self):
        self.assertEqual(self.review.text, 'Хайп')

    def test_review_author(self):
        self.assertEqual(self.review.user.username, 'review_user')
