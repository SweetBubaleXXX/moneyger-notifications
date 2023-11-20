import factory
from factory.fuzzy import FuzzyText

from app import models


class UserFactory(factory.Factory):
    class Meta:
        model = models.User

    account_id = factory.Sequence(int)
    email = factory.Faker("email")
    token = FuzzyText(length=32)
