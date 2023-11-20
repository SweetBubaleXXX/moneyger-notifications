from datetime import datetime

import factory
from factory.fuzzy import FuzzyText

from app import models


class UserFactory(factory.Factory):
    class Meta:
        model = models.User

    account_id = factory.Sequence(int)
    email = factory.Faker("email")
    token = FuzzyText(length=32)
    subscribed_to_chat = False


class MessageFactory(factory.Factory):
    class Meta:
        model = models.Message

    id = FuzzyText(length=32)
    sender = factory.Faker("first_name")
    from_admin = False
    text = factory.Faker("sentence")
    timestamp = factory.LazyAttribute(lambda *_: datetime.utcnow())
