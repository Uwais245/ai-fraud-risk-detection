"""Test that all modules import correctly"""
import pytest


def test_config_import():
    from app.core.config import settings
    assert settings.APP_NAME == "AI Fraud Risk Detection API"


def test_database_import():
    from app.core.database import Base, engine, get_db
    assert Base is not None


def test_security_import():
    from app.core.security import (
        verify_password,
        get_password_hash,
        create_access_token,
        decode_token
    )
    assert callable(verify_password)
    assert callable(get_password_hash)


def test_models_import():
    from app.models import (
        User, UserRole,
        Transaction, TransactionChannel,
        RiskAssessment,
        Alert, AlertSeverity, AlertStatus,
        Rule,
        CustomerRiskProfile,
        Feedback, FeedbackType
    )
    assert User is not None


def test_schemas_import():
    from app.schemas import (
        UserCreate, UserResponse, Token,
        TransactionCreate, TransactionResponse,
        RiskScoreRequest, RiskAssessmentResponse,
        AlertCreate, AlertResponse,
        DashboardStats, DashboardData,
        NetworkGraphResponse,
        InvestigationDetail,
        ReportRequest, ReportResponse,
        RuleCreate, RuleResponse,
        FeedbackCreate, FeedbackResponse
    )
    assert UserCreate is not None


def test_services_import():
    from app.services import (
        ml_service,
        ai_service,
        DashboardService,
        RulesEngineService,
        InvestigationService,
        ReportsService,
        NetworkService,
        CSVImportService
    )
    assert ml_service is not None


def test_routers_import():
    from app.routers import (
        auth, transactions, risk, dashboard, network,
        investigation, reports, rules, alerts, feedback
    )
    assert auth.router is not None


def test_main_app():
    from app.main import app
    assert app is not None
    assert app.title == "AI Fraud Risk Detection API"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])