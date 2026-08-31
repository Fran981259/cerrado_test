"""Unit tests para NewsClassifier."""
from app.classifier import NewsClassifier

def test_high_importance_tech():
    c = NewsClassifier()
    art = {"title": "OpenAI announces GPT-5 with breakthrough", "summary": "OpenAI revela novo modelo", "category": "technology", "source": "TechCrunch"}
    res = c.classify(dict(art))
    assert res["classification"]["priority_tier"] in ("TIER_1", "TIER_2")
    assert res["classification"]["importance_score"] >= 3.5

def test_low_importance_gossip_rejected():
    c = NewsClassifier()
    art = {"title": "Celebrity shares recipe for chocolate cake lifestyle gossip", "summary": "horoscope viral video meme", "category": "culture", "source": "Blog"}
    res = c.classify(dict(art))
    # deve cair para TIER_3 ou REJECT
    assert res["classification"]["priority_tier"] in ("TIER_3", "REJECT")

def test_engagement_viral_scandal():
    c = NewsClassifier()
    art = {"title": "Shocking scandal exposed: arrested after leaked video", "summary": "unbelievable controversy", "category": "general", "source": "Portal"}
    res = c.classify(dict(art))
    assert res["classification"]["engagement_score"] >= 4

def test_filter_by_priority_order():
    c = NewsClassifier()
    arts = [
        {"title": "Federal Reserve raises interest rates", "summary": "inflation recession", "category": "economy", "source": "Bloomberg"},
        {"title": "Simple recipe for cake", "summary": "lifestyle gossip", "category": "culture", "source": "Blog"},
    ]
    classified = [c.classify(dict(a)) for a in arts]
    filtered = c.filter_by_priority(classified, min_tier="TIER_2")
    # só o primeiro passa
    assert len(filtered) == 1
    assert "Federal Reserve" in filtered[0]["title"]

def test_final_score_weighted():
    c = NewsClassifier()
    art = {"title": "Test article", "summary": "Test summary", "category": "general", "source": "Portal"}
    res = c.classify(dict(art))
    imp = res["classification"]["importance_score"]
    eng = res["classification"]["engagement_score"]
    final = res["classification"]["final_score"]
    # 0.6*imp + 0.4*eng
    expected = round(imp*0.6 + eng*0.4, 2)
    assert abs(final - expected) < 0.05
