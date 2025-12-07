"""
Matches Router
Handles match CRUD operations
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from typing import List
from uuid import UUID
import logging

from app.db.session import get_db
from app.models.models import Match
from app.schemas.schemas import MatchCreate, MatchUpdate, MatchResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
async def create_match(match_data: MatchCreate, db: Session = Depends(get_db)):
    """
    Create a new match
    """
    try:
        match = Match(**match_data.model_dump())
        db.add(match)
        db.commit()
        db.refresh(match)
        return match
    except OperationalError as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database unavailable. Please check your connection."
        )


@router.get("/")
async def list_matches(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all matches with pagination
    Returns mock data if database is unavailable
    """
    try:
        matches = db.query(Match).offset(skip).limit(limit).all()
        return matches
    except OperationalError as e:
        logger.warning(f"Database unavailable, returning mock data: {e}")
        from app.mock_data import get_mock_matches
        return get_mock_matches()


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(match_id: UUID, db: Session = Depends(get_db)):
    """
    Get a specific match by ID
    """
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID {match_id} not found"
        )
    return match


@router.patch("/{match_id}", response_model=MatchResponse)
async def update_match(
    match_id: UUID,
    match_data: MatchUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a match
    """
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID {match_id} not found"
        )
    
    # Update only provided fields
    update_data = match_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(match, field, value)
    
    db.commit()
    db.refresh(match)
    return match


@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_match(match_id: UUID, db: Session = Depends(get_db)):
    """
    Delete a match (cascades to videos and related data)
    """
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match with ID {match_id} not found"
        )
    
    db.delete(match)
    db.commit()
    return None
