import factory

from app import models


class UserFactory(factory.Factory):
    class Meta:
        model = models.User

    email = factory.Faker("email")
