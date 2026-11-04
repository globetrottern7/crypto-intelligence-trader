def explain_analysis(analysis: dict) -> dict:
    """Deterministic explanation; an LLM cannot change risk decisions."""
    recommendation = analysis.get("recommendation", "no_trade")
    reasons = analysis.get("reasons", [])
    if recommendation == "candidate_long":
        headline = "A bullish setup candidate is present, not an instruction to buy."
    elif recommendation == "avoid_long":
        headline = "Long exposure is not supported by the current trend evidence."
    else:
        headline = "No actionable setup is confirmed; staying in cash is acceptable."
    return {
        "headline": headline, "evidence": reasons,
        "caveats": [
            "Indicator scores are descriptive, not probabilities of profit.",
            "Risk Guardian and data-quality gates take precedence over this explanation.",
            "AI explanations cannot create, approve or submit orders.",
        ],
        "model_role": "explain_only",
    }
