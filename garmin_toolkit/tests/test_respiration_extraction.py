from datetime import date
from unittest.mock import MagicMock
from garmin_training_toolkit_sdk.extractors.biometrics import get_respiration_data


def test_respiration_data_extraction():
    garmin_mock = MagicMock()
    garmin_mock.get_respiration_data.return_value = {
        "userProfileId": 12345,
        "lowestRespirationValue": 12.0,
        "highestRespirationValue": 25.0,
        "wakingRespirationValue": 15.0,
        "sleepRespirationValue": 13.0,
        "respirationValuesArray": [[1600000000000, 14.0], [1600000060000, 15.0]],
        "hourlyAverages": [
            [1600000000000, 14.5, 15.0, 14.0],
            [1600003600000, 15.5, 15.5, None],
        ],
    }

    respiration = get_respiration_data(garmin_mock, "2023-10-10")

    assert respiration is not None
    assert respiration.calendar_date == date(2023, 10, 10)
    assert respiration.lowest_respiration == 12.0
    assert respiration.highest_respiration == 25.0
    assert respiration.avg_waking_respiration == 15.0
    assert respiration.avg_sleep_respiration == 13.0

    assert len(respiration.timeseries) == 2
    assert respiration.timeseries[0] == (1600000000000, 14.0)
    assert respiration.timeseries[1] == (1600000060000, 15.0)

    assert len(respiration.hourly_averages) == 2
    assert respiration.hourly_averages[0] == (1600000000000, 14.5, 15.0, 14.0)
    assert respiration.hourly_averages[1] == (1600003600000, 15.5, 15.5, None)


def test_respiration_data_not_found():
    garmin_mock = MagicMock()
    garmin_mock.get_respiration_data.return_value = None

    respiration = get_respiration_data(garmin_mock, "2023-10-10")
    assert respiration is None
