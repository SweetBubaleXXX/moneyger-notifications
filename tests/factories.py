import factory
from factory.fuzzy import FuzzyText

from app import models


class UserFactory(factory.Factory):
    class Meta:
        model = models.User

    token = FuzzyText(length=32)
    email = factory.Faker("email")
