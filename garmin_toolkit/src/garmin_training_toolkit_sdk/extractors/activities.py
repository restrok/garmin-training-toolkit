import logging
from typing import Any, List, Optional

from garminconnect import Garmin

from ..protocol.activities import Activity, ActivitySplit, SwimLength, HRZoneTime
from ..protocol.telemetry import ActivityTelemetry, ActivityTelemetryPoint

log = logging.getLogger(__name__)


def get_activity_telemetry(
    garmin_client: Garmin, activity_id: int
) -> ActivityTelemetry:
    """Fetch second-by-second telemetry data for an activity.

    Args:
        garmin_client: The Garmin API client instance.
        activity_id: The ID of the activity.

    Returns:
        An ActivityTelemetry object.
    """
    try:
        details = garmin_client.get_activity_details(activity_id)
        if not details or "activityDetailMetrics" not in details:
            return ActivityTelemetry(activity_id=activity_id, metric_count=0, ticks=[])

        descriptors = details.get("metricDescriptors", [])
        raw_metrics = details.get("activityDetailMetrics", [])

        # Create a mapping of metric key to its array index
        key_to_index = {d["key"]: d["metricsIndex"] for d in descriptors}

        # Helper to safely extract a value from the metrics array
        def get_val(metric_array: List[Any], key: str) -> Optional[Any]:
            if key in key_to_index:
                idx = key_to_index[key]
                if idx < len(metric_array):
                    return metric_array[idx]
            return None

        ticks = []
        for tick_data in raw_metrics:
            metrics_array = tick_data.get("metrics", [])
            if not metrics_array:
                continue

            # Time must exist
            timestamp = get_val(metrics_array, "directTimestamp")
            if timestamp is None:
                continue

            ticks.append(
                ActivityTelemetryPoint(
                    timestamp_ms=int(timestamp),
                    lat=get_val(metrics_array, "directLatitude"),
                    lng=get_val(metrics_array, "directLongitude"),
                    elevation_m=get_val(metrics_array, "directElevation"),
                    speed_mps=get_val(metrics_array, "directSpeed"),
                    hr_bpm=get_val(metrics_array, "directHeartRate"),
                    cadence_spm=get_val(metrics_array, "directDoubleCadence"),
                    power_w=get_val(metrics_array, "directPower"),
                    fractional_cadence=get_val(
                        metrics_array, "directFractionalCadence"
                    ),
                    gap_mps=get_val(metrics_array, "directGradeAdjustedSpeed"),
                    stride_length_mm=get_val(metrics_array, "directStrideLength"),
                    vertical_oscillation_cm=get_val(
                        metrics_array, "directVerticalOscillation"
                    ),
                    ground_contact_time_ms=get_val(
                        metrics_array, "directGroundContactTime"
                    ),
                    temperature_c=get_val(metrics_array, "directAmbientTemperature")
                    if get_val(metrics_array, "directAmbientTemperature") is not None
                    else get_val(metrics_array, "directAirTemperature"),
                    run_walk_index=get_val(metrics_array, "directRunWalkIndex"),
                    body_battery=get_val(metrics_array, "directBodyBattery"),
                    vertical_speed=get_val(metrics_array, "directVerticalSpeed"),
                    vertical_ratio=get_val(metrics_array, "directVerticalRatio"),
                    performance_condition=get_val(
                        metrics_array, "directPerformanceCondition"
                    ),
                )
            )

        return ActivityTelemetry(
            activity_id=activity_id, metric_count=len(ticks), ticks=ticks
        )
    except Exception as e:
        log.error("Failed to fetch telemetry for %d: %s", activity_id, e)
        return ActivityTelemetry(activity_id=activity_id, metric_count=0, ticks=[])


def get_activity_hr_zones(garmin_client: Garmin, activity_id: int) -> List[HRZoneTime]:
    """Fetch HR zones for an activity."""
    try:
        zones_data = garmin_client.get_activity_hr_in_timezones(activity_id)
        if not zones_data:
            return []

        zones = []
        for zone in zones_data:
            zones.append(
                HRZoneTime(
                    zone_number=zone.get("zoneNumber"),
                    secs_in_zone=zone.get("secsInZone"),
                    zone_low_boundary_bpm=zone.get("zoneLowBoundary"),
                )
            )
        return zones
    except Exception as e:
        log.warning("Failed to get HR zones for %d: %s", activity_id, e)
    return []


def get_activity_splits(garmin_client: Garmin, activity_id: int) -> List[ActivitySplit]:
    """Fetch detailed splits for an activity.

    Args:
        garmin_client: The Garmin API client instance.
        activity_id: The ID of the activity.

    Returns:
        A list of ActivitySplit objects.
    """
    try:
        splits_data = garmin_client.get_activity_splits(activity_id)
        if splits_data and "lapDTOs" in splits_data:
            laps = []
            for lap in splits_data["lapDTOs"]:
                lengths = []
                for length in lap.get("lengthDTOs", []):
                    lengths.append(
                        SwimLength(
                            length_index=length.get("lengthIndex"),
                            start_time_gmt=length.get("startTimeGMT"),
                            distance_m=length.get("distance"),
                            duration_sec=length.get("duration"),
                            avg_speed_mps=length.get("averageSpeed"),
                            max_speed_mps=length.get("maxSpeed"),
                            avg_hr=length.get("averageHR"),
                            max_hr=length.get("maxHR"),
                            total_strokes=length.get("strokes"),
                            avg_swolf=length.get("averageSWOLF"),
                            swim_stroke=length.get("swimStroke"),
                            calories=length.get("calories"),
                        )
                    )

                laps.append(
                    ActivitySplit(
                        index=lap.get("lapIndex"),
                        type=lap.get("intensityType"),
                        distance_m=lap.get("distance"),
                        duration_sec=lap.get("duration"),
                        moving_duration_sec=lap.get("movingDuration"),
                        elapsed_duration_sec=lap.get("elapsedDuration"),
                        avg_hr=lap.get("averageHR"),
                        max_hr=lap.get("maxHR"),
                        avg_pace_mps=lap.get("averageMovingSpeed")
                        or lap.get("averageSpeed"),
                        avg_cadence=lap.get("averageRunCadence")
                        or lap.get("averageBikeCadence")
                        or lap.get("averageSwimCadence"),
                        calories=lap.get("calories"),
                        strokes=lap.get("strokes"),
                        avg_swolf=lap.get("averageSWOLF"),
                        swim_stroke=lap.get("swimStroke"),
                        avg_swim_cadence=lap.get("averageSwimCadence"),
                        active_lengths=lap.get("activeLengths"),
                        avg_strokes_per_length=lap.get("avgStrokes"),
                        avg_power=lap.get("averagePower"),
                        max_power=lap.get("maxPower"),
                        lengths=lengths,
                    )
                )
            return laps
    except Exception as e:
        log.warning("Failed to get splits for %d: %s", activity_id, e)
    return []


def get_activities(
    garmin_client: Garmin, start_date: str, end_date: str, limit: int = 20
) -> List[Activity]:
    """Fetch activities within a date range.

    Args:
        garmin_client: The Garmin API client instance.
        start_date: Start date string (YYYY-MM-DD).
        end_date: End date string (YYYY-MM-DD).
        limit: Maximum number of activities to fetch.

    Returns:
        A list of Activity objects.
    """
    activities = []
    try:
        # Note: Garmin API usually uses start and limit for this endpoint
        # if using get_activities. If using by date, we might need a different client method.
        # For now, let's keep it consistent with how it's being called.
        raw_activities = garmin_client.get_activities_by_date(start_date, end_date)
        for a in raw_activities:
            activity_date = a.get("startTimeLocal", "")

            activity = Activity(
                id=a.get("activityId"),
                name=a.get("activityName", "Unknown"),
                type=a.get("activityType", {}).get("typeKey", "unknown"),
                date=activity_date,
                duration_sec=a.get("duration"),
                moving_duration_sec=a.get("movingDuration"),
                elapsed_duration_sec=a.get("elapsedDuration"),
                distance_m=a.get("distance"),
                avg_hr=a.get("averageHR"),
                max_hr=a.get("maxHR"),
                min_hr=a.get("minHR"),
                recovery_hr=a.get("recoveryHeartRate"),
                avg_pace=a.get("averageSpeed"),
                max_speed_mps=a.get("maxSpeed"),
                calories=a.get("calories"),
                elevation_gain=a.get("elevationGain"),
                vo2max=a.get("vO2MaxValue"),
                pool_length_m=a.get("poolLength"),
                total_strokes=a.get("strokes"),
                avg_swolf=a.get("averageSWOLF"),
                swim_stroke=a.get("swimStroke"),
                avg_swim_cadence=a.get("averageSwimCadence"),
                active_lengths=a.get("activeLengths"),
                avg_strokes_per_length=a.get("avgStrokes"),
                avg_stroke_distance_m=a.get("averageStrokeDistance"),
                avg_power=a.get("averagePower"),
                max_power=a.get("maxPower"),
                normalized_power=a.get("normPower"),
                avg_cadence=a.get("averageRunCadence")
                or a.get("averageBikeCadence")
                or a.get("averageSwimCadence"),
                max_cadence=a.get("maxRunCadence")
                or a.get("maxBikeCadence")
                or a.get("maxSwimCadence"),
                moderate_intensity_min=a.get("moderateIntensityMinutes"),
                vigorous_intensity_min=a.get("vigorousIntensityMinutes"),
                is_personal_record=a.get("pr"),
                lap_count=a.get("steps")
                if a.get("activityType", {}).get("typeKey") == "indoor_cardio"
                else a.get("laps"),
            )
            # You might want to fetch splits lazily or keep this separate to avoid rate limits
            activities.append(activity)
    except Exception as e:
        log.warning("Activities fetch failed: %s", e)
    return activities
