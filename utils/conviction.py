
def compute_conviction_score(features, weights, override_config=None):
    score = 0
    total_weight = 0
    overrides = []

    for factor, value in features.items():
        weight = weights.get(factor, 0)
        score += value * weight
        total_weight += weight

    final_score = round((score / total_weight) * 100, 2) if total_weight else 0

    # Apply override flags based on conviction threshold
    if override_config:
        for param, rule in override_config.items():
            threshold = rule.get("threshold", 90)
            if final_score >= threshold:
                overrides.append(param)

    return {
        "score": final_score,
        "overrides": overrides
    }
