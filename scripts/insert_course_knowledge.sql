INSERT INTO courses_required_knowledges (course_id, knowledge_id, quality)
SELECT 
    cc.course_id,
    ck.knowledge_id,
    AVG(ck.quality) / 10 AS average_quality
FROM 
    courses_cards AS cc
JOIN 
    cards_knowledges AS ck ON cc.card_id = ck.card_id
GROUP BY 
    cc.course_id, ck.knowledge_id
ON CONFLICT (course_id, knowledge_id) 
DO UPDATE SET quality = EXCLUDED.quality;
