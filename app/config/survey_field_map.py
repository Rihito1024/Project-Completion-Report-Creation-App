SURVEY_FIELD_MAP = {
    "goal_achievement": ["ゴール達成度", "達成度", "goal_achievement"],
    "satisfaction": ["満足度", "satisfaction"],
    "communication_load": ["やり取り負荷", "コミュニケーション負荷", "communication_load"],
    "nps_segment": ["NPS区分", "NPS", "nps_segment"],
    "output_quality": ["アウトプット品質", "成果物品質", "output_quality"],
    "technical_expertise": ["技術的専門性", "technical_expertise"],
    "business_understanding": ["推進/提案/ビジネス理解", "ビジネス理解", "business_understanding"],
    "positive_comment": ["良かったところや感想", "良かった点", "positive_comment"],
    "improvement_comment": ["気になったところや改善点", "改善点", "improvement_comment"],
    "communication_difficulty_comment": ["やり取りで難しさを感じたところ", "難しかった点", "communication_difficulty_comment"],
}

NUMERIC_FIELDS = {
    "goal_achievement",
    "satisfaction",
    "communication_load",
    "output_quality",
    "technical_expertise",
    "business_understanding",
}

TEXT_FIELDS = {
    "nps_segment",
    "positive_comment",
    "improvement_comment",
    "communication_difficulty_comment",
}
