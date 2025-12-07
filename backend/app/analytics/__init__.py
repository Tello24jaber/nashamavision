"""
Analytics module initialization - Phase 3
"""
from app.analytics.physical import (
    PhysicalMetricsEngine,
    TeamMetricsEngine,
    PhysicalMetrics,
    TrackPointData
)
from app.analytics.heatmap import (
    HeatmapEngine,
    ZoneAnalyzer,
    Heatmap,
    HeatmapConfig
)
from app.analytics.models import (
    PlayerMetric,
    PlayerMetricTimeSeries,
    PlayerHeatmap,
    TeamMetric,
    MetricType,
    TimeSeriesMetricType
)
from app.analytics.tactical import (
    TacticalAnalysisEngine,
    TeamTacticalSnapshot,
    TransitionEvent,
    compute_tactical_snapshots
)
from app.analytics.xt import (
    ExpectedThreatEngine,
    XTEvent,
    PlayerXTSummary,
    compute_match_xt
)
from app.analytics.events import (
    EventDetectionEngine,
    FootballEvent,
    detect_match_events
)

__all__ = [
    # Phase 2
    "PhysicalMetricsEngine",
    "TeamMetricsEngine",
    "PhysicalMetrics",
    "TrackPointData",
    "HeatmapEngine",
    "ZoneAnalyzer",
    "Heatmap",
    "HeatmapConfig",
    "PlayerMetric",
    "PlayerMetricTimeSeries",
    "PlayerHeatmap",
    "TeamMetric",
    "MetricType",
    "TimeSeriesMetricType",
    # Phase 3
    "TacticalAnalysisEngine",
    "TeamTacticalSnapshot",
    "TransitionEvent",
    "compute_tactical_snapshots",
    "ExpectedThreatEngine",
    "XTEvent",
    "PlayerXTSummary",
    "compute_match_xt",
    "EventDetectionEngine",
    "FootballEvent",
    "detect_match_events"
]
