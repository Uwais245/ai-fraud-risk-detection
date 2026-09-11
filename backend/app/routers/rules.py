from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.core.deps import get_current_active_user, require_admin
from app.models.user import User
from app.services.rules_engine import RulesEngineService
from app.schemas.rules import (
    RuleCreate, RuleUpdate, RuleResponse, RuleListResponse
)

router = APIRouter()


@router.get("/", response_model=RuleListResponse)
async def list_rules(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """List all rules (admin only)"""
    from sqlalchemy import select, func
    from app.models.rule import Rule
    
    stmt = select(Rule)
    if is_active is not None:
        stmt = stmt.where(Rule.is_active == is_active)
    
    # Get total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt) or 0
    
    # Paginate
    stmt = stmt.order_by(Rule.id).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(stmt)
    rules = result.scalars().all()
    
    return RuleListResponse(
        rules=rules,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=(total + per_page - 1) // per_page
    )


@router.post("/", response_model=RuleResponse, status_code=201)
async def create_rule(
    rule_data: RuleCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new rule (admin only)"""
    service = RulesEngineService(db)
    rule = await service.create_rule(rule_data.model_dump(), current_user.id)
    return rule


@router.get("/{rule_id}", response_model=RuleResponse)
async def get_rule(
    rule_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific rule"""
    from sqlalchemy import select
    from app.models.rule import Rule
    
    stmt = select(Rule).where(Rule.id == rule_id)
    result = await db.execute(stmt)
    rule = result.scalar_one_or_none()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    return rule


@router.patch("/{rule_id}", response_model=RuleResponse)
async def update_rule(
    rule_id: int,
    rule_data: RuleUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update a rule (admin only)"""
    service = RulesEngineService(db)
    rule = await service.update_rule(rule_id, rule_data.model_dump(exclude_unset=True))
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    return rule


@router.delete("/{rule_id}", status_code=204)
async def delete_rule(
    rule_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete a rule (admin only)"""
    service = RulesEngineService(db)
    success = await service.delete_rule(rule_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Rule not found")


@router.post("/test")
async def test_rules(
    transaction_data: dict,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Test rules against sample transaction data"""
    service = RulesEngineService(db)
    risk_increase, flags = await service.evaluate_rules(transaction_data)
    
    return {
        "risk_increase": risk_increase,
        "triggered_flags": flags
    }