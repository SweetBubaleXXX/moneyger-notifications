import argparse

from app.application import create_container
from app.services.predictions import PredictionPeriod


def main():
    parser = argparse.ArgumentParser(description="Send expense predictions.")
    parser.add_argument(
        "period",
        choices=["WEEK", "MONTH"],
        help="The prediction period to send (WEEK or MONTH).",
    )
    args = parser.parse_args()

    container = create_container()
    period = PredictionPeriod[args.period]
    container.email_service().send_predictions(period)


if __name__ == "__main__":
    main()
