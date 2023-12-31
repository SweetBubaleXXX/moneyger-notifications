from datetime import datetime, timedelta
from decimal import Decimal
from enum import StrEnum, auto
from typing import Callable

import pandas as pd
import pmdarima

from .exceptions import NotFound
from .transactions import TransactionsService


class PredictionPeriod(StrEnum):
    WEEK = auto()
    MONTH = auto()


class PredictionsService:
    def __init__(self, transactions_service: TransactionsService) -> None:
        self.transactions_service = transactions_service

    def predict_period(self, account_id: int, period: PredictionPeriod) -> Decimal:
        prediction_funcs: dict[PredictionPeriod, Callable[[int], Decimal]] = {
            PredictionPeriod.WEEK: self.predict_week,
            PredictionPeriod.MONTH: self.predict_month,
        }
        return prediction_funcs[period](account_id)

    def predict_week(self, account_id: int) -> Decimal:
        daily_totals = self._get_totals(account_id, days=365)
        return self._make_prediction(daily_totals, "W-MON")

    def predict_month(self, account_id: int) -> Decimal:
        daily_totals = self._get_totals(account_id, days=730)
        return self._make_prediction(daily_totals, "M")

    def _get_totals(self, account_id: int, days: int) -> pd.DataFrame:
        daily_totals = self.transactions_service.compute_daily_total(
            {
                "account_id": account_id,
                "transaction_type": "OUT",
                "start_time": datetime.now() - timedelta(days=days),
            }
        )
        dataset = pd.DataFrame(daily_totals)
        if not len(dataset):
            raise NotFound("No transactions fot given period")
        dataset["date"] = pd.to_datetime(dataset["date"])
        dataset.set_index("date", inplace=True)
        return dataset

    def _make_prediction(self, dataset: pd.DataFrame, resample_rule: str) -> Decimal:
        time_series = dataset["total_amount"].resample(resample_rule).sum().fillna(0)
        model = pmdarima.auto_arima(time_series)
        predictions = model.predict(1)
        return round(Decimal(predictions.iloc[0]), 2)
