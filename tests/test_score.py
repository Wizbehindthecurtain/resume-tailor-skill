import score

def test_compute_score_weights():
    assert score.compute_score(1.0, 1.0, 1.0) == 100
    assert score.compute_score(1.0, 0.5, 0.0) == 65

def test_score_literal_matching():
    payload = {"resume_text": "Built CI in Python and Kubernetes",
               "keywords": ["python", "kubernetes", "terraform"],
               "must_haves": ["python"], "semantic_match": 1.0}
    out = score.score(payload)
    assert out["must_have_hit_rate"] == 1.0
    assert abs(out["keyword_coverage"] - 2 / 3) < 1e-9
    assert "terraform" in out["missing"]
    assert out["score"] == 90  # 0.50*1 + 0.30*0.667 + 0.20*1 = 0.90
