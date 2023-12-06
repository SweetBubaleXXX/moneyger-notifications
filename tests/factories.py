from datetime import datetime

import factory
from factory.fuzzy import FuzzyDecimal, FuzzyText

from app import models


class UserFactory(factory.Factory):
    class Meta:
        model = models.User

    account_id = factory.Sequence(int)
    email = factory.Faker("email")
    token = FuzzyText(length=32)
    subscribed_to_chat = False
    subscribed_to_predictions = False


class TransactionFactory(factory.Factory):
    class Meta:
        model = models.Transaction

    transaction_id = factory.Sequence(int)
    account_id = 1
    amount = FuzzyDecimal(1, 1000)
    transaction_time = factory.LazyAttribute(lambda *_: datetime.utcnow())


class MessageFactory(factory.Factory):
    class Meta:
        model = models.Message

    id = FuzzyText(length=32)
    sender = factory.Faker("first_name")
    from_admin = False
    text = factory.Faker("sentence")
    timestamp = factory.LazyAttribute(lambda *_: datetime.utcnow())
