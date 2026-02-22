import pytest
from rich.text import Text
from claude_ctx_py.tui_dashboard import DashboardCard

def test_create_health_card_with_recommendations():
    score = 85
    issues = ["Issue 1"]
    recommendations = [{"type": "enable", "target": "Some Feature"}]
    width = 40
    
    card = DashboardCard.create_health_card(score, issues, recommendations, width=width)
    
    # Verify the recommendation line is present
    recommendation_found = False
    for line in card:
        if "ENABLE" in line and "Some Feature" in line:
            recommendation_found = True
        
        # Verify padding correctness: all box lines should have visible width matching the card width
        if line.startswith("│") or line.startswith("╭") or line.startswith("╰") or line.startswith("├"):
            visible_len = Text.from_markup(line).cell_len
            assert visible_len == width, f"Line width {visible_len} != {width}: {line}"
            
    assert recommendation_found

def test_create_compact():
    card = DashboardCard.create_compact("Test", "Value", icon="Icon")
    assert "Test" in card
    assert "Value" in card
    assert "Icon" in card
