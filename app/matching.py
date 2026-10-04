"""
Smarter matching engine for SkillSwap.

Instead of only surfacing perfect mutual matches (A teaches what B wants AND
B teaches what A wants), this scores EVERY other user on how useful a match
they'd be, so users see a ranked list of partial matches too.

Score = WEIGHT_DIRECT_MATCH   * direct_match_score
      + WEIGHT_RECIPROCAL_MATCH * reciprocal_match_score
      + WEIGHT_RATING         * normalized_rating

- direct_match_score: of the skills YOU want to learn, what fraction can
  this person teach you? Weighted by their proficiency in each skill
  (expert counts more than beginner).
- reciprocal_match_score: of the skills YOU can teach, what fraction does
  this person want to learn? (mutual benefit - they'd want to connect too)
- normalized_rating: their average past session rating, scaled 0-1.
"""

from flask import current_app
from app.models import User, UserSkillTeach, Review


def _proficiency_weight(proficiency):
    weights = current_app.config["PROFICIENCY_WEIGHTS"]
    return weights.get(proficiency, 0.5)


def _direct_match_score(me, other):
    """How much of what I want to learn, `other` can teach me (proficiency-weighted)."""
    my_learn_ids = me.learn_skill_ids()
    if not my_learn_ids:
        return 0.0, []

    other_teach_map = other.teach_proficiency_map()  # skill_id -> proficiency
    overlap_ids = my_learn_ids & set(other_teach_map.keys())
    if not overlap_ids:
        return 0.0, []

    total_weight = sum(_proficiency_weight(other_teach_map[sid]) for sid in overlap_ids)
    score = total_weight / len(my_learn_ids)
    return min(score, 1.0), overlap_ids


def _reciprocal_match_score(me, other):
    """How much of what I can teach, `other` wants to learn."""
    my_teach_ids = me.teach_skill_ids()
    if not my_teach_ids:
        return 0.0, []

    other_learn_ids = other.learn_skill_ids()
    overlap_ids = my_teach_ids & other_learn_ids
    if not overlap_ids:
        return 0.0, []

    score = len(overlap_ids) / len(my_teach_ids)
    return min(score, 1.0), overlap_ids


def _normalized_rating(other):
    avg = other.average_rating()
    if avg is None:
        return 0.6  # neutral default for users with no reviews yet, so they aren't buried
    return avg / 5.0


def compute_matches(me, limit=20, min_score=0.01):
    """Return a ranked list of match dicts for user `me`."""
    cfg = current_app.config
    candidates = User.query.filter(User.id != me.id).all()

    results = []
    for other in candidates:
        direct_score, they_can_teach_ids = _direct_match_score(me, other)
        reciprocal_score, i_can_teach_ids = _reciprocal_match_score(me, other)

        if direct_score == 0 and reciprocal_score == 0:
            continue  # no relevance at all, skip

        rating_score = _normalized_rating(other)

        total = (
            cfg["WEIGHT_DIRECT_MATCH"] * direct_score
            + cfg["WEIGHT_RECIPROCAL_MATCH"] * reciprocal_score
            + cfg["WEIGHT_RATING"] * rating_score
        )

        if total < min_score:
            continue

        skill_id_to_name = {s.skill.id: s.skill.name for s in other.teach_links}
        skill_id_to_name.update({s.skill.id: s.skill.name for s in me.teach_links})

        results.append({
            "user": other,
            "score": round(total * 100, 1),  # as a 0-100 "match %"
            "they_can_teach_you": sorted(skill_id_to_name.get(sid, "?") for sid in they_can_teach_ids),
            "you_can_teach_them": sorted(skill_id_to_name.get(sid, "?") for sid in i_can_teach_ids),
            "rating": other.average_rating(),
            "review_count": other.review_count(),
        })

    results.sort(key=lambda r: r["score"], reverse=True)
    return results[:limit]
