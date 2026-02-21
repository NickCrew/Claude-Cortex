import pytest
from claude_ctx_py.tui_dashboard import DashboardCard

def test_create_health_card_with_recommendations():
    score = 85
    issues = ["Issue 1"]
    recommendations = [{"type": "enable", "target": "Some Feature"}]
    
    card = DashboardCard.create_health_card(score, issues, recommendations, width=40)
    
    # Verify the recommendation line is present
    recommendation_found = False
    for line in card:
        if "ENABLE" in line and "Some Feature" in line:
            recommendation_found = True
            break
            
    assert recommendation_found

def test_create_compact():
    card = DashboardCard.create_compact("Test", "Value", icon="Icon")
    assert "Test" in card
    assert "Value" in card
    assert "Icon" in card
