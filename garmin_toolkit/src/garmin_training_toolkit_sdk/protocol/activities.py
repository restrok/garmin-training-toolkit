from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class HRZoneTime(BaseModel):
    zone_number: int
    secs_in_zone: float
    zone_low_boundary_bpm: int


class ActivityHRZones(BaseModel):
    zones: List[HRZoneTime] = Field(default_factory=list)


class SwimLength(BaseModel):
    length_index: int
    start_time_gmt: Optional[datetime] = None
    distance_m: Optional[float] = None
    duration_sec: Optional[float] = None
    avg_speed_mps: Optional[float] = None
    max_speed_mps: Optional[float] = None
    avg_hr: Optional[float] = None
    max_hr: Optional[float] = None
    total_strokes: Optional[int] = None
    avg_swolf: Optional[float] = None
    swim_stroke: Optional[str] = None
    calories: Optional[float] = None


class ActivitySplit(BaseModel):
    index: int
    type: Optional[str] = None
    distance_m: Optional[float] = None
    duration_sec: Optional[float] = None
    moving_duration_sec: Optional[float] = None
    avg_hr: Optional[float] = None
    max_hr: Optional[float] = None
    avg_pace_mps: Optional[float] = None
    avg_cadence: Optional[float] = None
    calories: Optional[float] = None
    # Swimming Specific
    strokes: Optional[float] = None
    avg_swolf: Optional[float] = None
    swim_stroke: Optional[str] = None
    avg_swim_cadence: Optional[float] = None
    active_lengths: Optional[int] = None
    avg_strokes_per_length: Optional[float] = None
    elapsed_duration_sec: Optional[float] = None
    lengths: Optional[List[SwimLength]] = Field(default_factory=list)
    # Cycling Specific
    avg_power: Optional[float] = None
    max_power: Optional[float] = None


class Activity(BaseModel):
    id: int
    name: str
    type: str
    date: datetime
    duration_sec: Optional[float] = None
    distance_m: Optional[float] = None
    avg_hr: Optional[float] = None
    max_hr: Optional[float] = None
    avg_pace: Optional[float] = None
    calories: Optional[float] = None
    elevation_gain: Optional[float] = None
    vo2max: Optional[float] = None
    moving_duration_sec: Optional[float] = None
    elapsed_duration_sec: Optional[float] = None
    min_hr: Optional[float] = None
    max_speed_mps: Optional[float] = None
    moderate_intensity_min: Optional[int] = None
    vigorous_intensity_min: Optional[int] = None
    is_personal_record: Optional[bool] = None
    lap_count: Optional[int] = None
    recovery_hr: Optional[float] = None
    # Swimming Specific
    pool_length_m: Optional[float] = None
    total_strokes: Optional[float] = None
    avg_swolf: Optional[float] = None
    swim_stroke: Optional[str] = None
    avg_swim_cadence: Optional[float] = None
    active_lengths: Optional[int] = None
    avg_strokes_per_length: Optional[float] = None
    avg_stroke_distance_m: Optional[float] = None
    # Cycling Specific
    avg_power: Optional[float] = None
    max_power: Optional[float] = None
    normalized_power: Optional[float] = None
    avg_cadence: Optional[float] = None
    max_cadence: Optional[float] = None
    splits: Optional[List[ActivitySplit]] = Field(default_factory=list)
