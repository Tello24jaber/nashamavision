"""
Mock data for demo mode when database is unavailable
"""
from datetime import datetime, timedelta
from uuid import uuid4

def get_mock_matches():
    """Return mock match data"""
    base_date = datetime.now() - timedelta(days=7)
    
    return [
        {
            "id": str(uuid4()),
            "name": "Premier League - Week 15",
            "home_team": "Manchester City",
            "away_team": "Arsenal",
            "home_score": 3,
            "away_score": 1,
            "date": (base_date + timedelta(days=1)).isoformat(),
            "venue": "Etihad Stadium",
            "competition": "Premier League",
            "status": "completed"
        },
        {
            "id": str(uuid4()),
            "name": "La Liga - Matchday 16",
            "home_team": "Real Madrid",
            "away_team": "Barcelona",
            "home_score": 2,
            "away_score": 2,
            "date": (base_date + timedelta(days=2)).isoformat(),
            "venue": "Santiago Bernabéu",
            "competition": "La Liga",
            "status": "completed"
        },
        {
            "id": str(uuid4()),
            "name": "Champions League - Group Stage",
            "home_team": "Bayern Munich",
            "away_team": "Paris Saint-Germain",
            "home_score": 1,
            "away_score": 0,
            "date": (base_date + timedelta(days=3)).isoformat(),
            "venue": "Allianz Arena",
            "competition": "UEFA Champions League",
            "status": "completed"
        },
        {
            "id": str(uuid4()),
            "name": "Serie A - Round 14",
            "home_team": "Juventus",
            "away_team": "Inter Milan",
            "home_score": 2,
            "away_score": 1,
            "date": (base_date + timedelta(days=4)).isoformat(),
            "venue": "Juventus Stadium",
            "competition": "Serie A",
            "status": "completed"
        },
        {
            "id": str(uuid4()),
            "name": "Bundesliga - Matchday 13",
            "home_team": "Borussia Dortmund",
            "away_team": "RB Leipzig",
            "home_score": 4,
            "away_score": 2,
            "date": (base_date + timedelta(days=5)).isoformat(),
            "venue": "Signal Iduna Park",
            "competition": "Bundesliga",
            "status": "completed"
        }
    ]


def get_mock_players(match_id):
    """Return mock player data for a match"""
    return [
        {
            "id": str(uuid4()),
            "match_id": match_id,
            "jersey_number": 10,
            "name": "Kevin De Bruyne",
            "position": "Midfielder",
            "team": "home"
        },
        {
            "id": str(uuid4()),
            "match_id": match_id,
            "jersey_number": 7,
            "name": "Bukayo Saka",
            "position": "Forward",
            "team": "away"
        }
    ]
