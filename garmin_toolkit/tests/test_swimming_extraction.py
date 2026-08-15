from unittest.mock import MagicMock
from garmin_training_toolkit_sdk.extractors.activities import (
    get_activities,
    get_activity_splits,
    get_activity_hr_zones,
)


def test_swimming_activities_extraction():
    garmin_mock = MagicMock()
    garmin_mock.get_activities_by_date.return_value = [
        {
            "activityId": 1234,
            "activityName": "Pool Swim",
            "activityType": {"typeKey": "lap_swimming"},
            "startTimeLocal": "2023-10-10 10:00:00",
            "duration": 1800.0,
            "movingDuration": 1500.0,
            "elapsedDuration": 1900.0,
            "distance": 1500.0,
            "averageHR": 140.0,
            "maxHR": 160.0,
            "minHR": 100.0,
            "recoveryHeartRate": 110.0,
            "averageSpeed": 1.2,
            "maxSpeed": 1.5,
            "poolLength": 25.0,
            "strokes": 450.0,
            "averageSWOLF": 35.0,
            "swimStroke": "FREESTYLE",
            "averageSwimCadence": 30.0,
            "activeLengths": 60,
            "avgStrokes": 15.0,
            "averageStrokeDistance": 1.6,
            "calories": 400.0,
            "moderateIntensityMinutes": 20,
            "vigorousIntensityMinutes": 10,
            "pr": True,
            "laps": 10,
        },
        {
            "activityId": 1235,
            "activityName": "Indoor Cardio",
            "activityType": {"typeKey": "indoor_cardio"},
            "startTimeLocal": "2023-10-11 10:00:00",
            "duration": 3600.0,
            "movingDuration": 3600.0,
            "elapsedDuration": 3600.0,
            "distance": None,
            "averageHR": 130.0,
            "maxHR": 150.0,
            "minHR": 90.0,
            "averageSpeed": None,
            "maxSpeed": None,
            "calories": 500.0,
            "steps": 5000,
        },
    ]

    activities = get_activities(garmin_mock, "2023-10-10", "2023-10-11")
    assert len(activities) == 2

    swim = activities[0]
    assert swim.id == 1234
    assert swim.type == "lap_swimming"
    assert swim.moving_duration_sec == 1500.0
    assert swim.elapsed_duration_sec == 1900.0
    assert swim.min_hr == 100.0
    assert swim.recovery_hr == 110.0
    assert swim.pool_length_m == 25.0
    assert swim.total_strokes == 450.0
    assert swim.avg_swolf == 35.0
    assert swim.swim_stroke == "FREESTYLE"
    assert swim.avg_swim_cadence == 30.0
    assert swim.active_lengths == 60
    assert swim.avg_strokes_per_length == 15.0
    assert swim.avg_stroke_distance_m == 1.6
    assert swim.moderate_intensity_min == 20
    assert swim.vigorous_intensity_min == 10
    assert swim.is_personal_record is True
    assert swim.lap_count == 10

    cardio = activities[1]
    assert cardio.id == 1235
    assert cardio.type == "indoor_cardio"
    assert cardio.distance_m is None
    assert cardio.max_speed_mps is None
    assert cardio.lap_count == 5000


def test_swimming_splits_extraction():
    garmin_mock = MagicMock()
    garmin_mock.get_activity_splits.return_value = {
        "lapDTOs": [
            {
                "lapIndex": 1,
                "intensityType": "ACTIVE",
                "distance": 100.0,
                "duration": 90.0,
                "movingDuration": 90.0,
                "elapsedDuration": 90.0,
                "averageHR": 140.0,
                "maxHR": 150.0,
                "averageSpeed": 1.1,
                "averageSwimCadence": 28.0,
                "calories": 25.0,
                "strokes": 30,
                "averageSWOLF": 32.0,
                "swimStroke": "FREESTYLE",
                "activeLengths": 4,
                "avgStrokes": 15.0,
                "lengthDTOs": [
                    {
                        "lengthIndex": 1,
                        "distance": 25.0,
                        "duration": 22.0,
                        "averageSpeed": 1.1,
                        "maxSpeed": 1.2,
                        "averageHR": 135.0,
                        "maxHR": 140.0,
                        "strokes": 15,
                        "averageSWOLF": 31.0,
                        "swimStroke": "FREESTYLE",
                        "calories": 6.0,
                    }
                ],
            },
            {
                "lapIndex": 2,
                "intensityType": "REST",
                "distance": 0.0,
                "duration": 30.0,
                "movingDuration": 0.0,
                "elapsedDuration": 30.0,
                "averageHR": 120.0,
                "maxHR": 130.0,
                "averageSpeed": 0.0,
                "averageSwimCadence": 0.0,
                "calories": 5.0,
                "strokes": 0,
                "averageSWOLF": 0.0,
                "swimStroke": "UNKNOWN",
                "activeLengths": 0,
                "avgStrokes": 0.0,
                "lengthDTOs": [],
            },
        ]
    }

    splits = get_activity_splits(garmin_mock, 1234)
    assert len(splits) == 2

    lap1 = splits[0]
    assert lap1.index == 1
    assert lap1.distance_m == 100.0
    assert lap1.avg_swim_cadence == 28.0
    assert lap1.active_lengths == 4
    assert lap1.avg_strokes_per_length == 15.0
    assert lap1.elapsed_duration_sec == 90.0
    assert lap1.swim_stroke == "FREESTYLE"
    assert len(lap1.lengths) == 1

    length1 = lap1.lengths[0]
    assert length1.length_index == 1
    assert length1.distance_m == 25.0
    assert length1.swim_stroke == "FREESTYLE"
    assert length1.avg_swolf == 31.0

    lap2 = splits[1]
    assert lap2.index == 2
    assert lap2.distance_m == 0.0
    assert lap2.type == "REST"
    assert len(lap2.lengths) == 0


def test_activity_hr_zones():
    garmin_mock = MagicMock()
    garmin_mock.get_activity_hr_in_timezones.return_value = [
        {"zoneNumber": 1, "secsInZone": 300.0, "zoneLowBoundary": 100},
        {"zoneNumber": 2, "secsInZone": 600.0, "zoneLowBoundary": 120},
        {"zoneNumber": 3, "secsInZone": 900.0, "zoneLowBoundary": 140},
    ]

    zones = get_activity_hr_zones(garmin_mock, 1234)
    assert len(zones) == 3
    assert zones[0].zone_number == 1
    assert zones[0].secs_in_zone == 300.0
    assert zones[0].zone_low_boundary_bpm == 100
    assert zones[2].zone_number == 3
    assert zones[2].secs_in_zone == 900.0
    assert zones[2].zone_low_boundary_bpm == 140
