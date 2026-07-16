-- Example queries against pittsburgh_water.db
-- Run any of these:  sqlite3 db/pittsburgh_water.db < db/queries.sql
-- or paste one into the live explorer at db/index.html.

-- 1. Every headline figure the two stories reported, computed in one row.
SELECT * FROM v_headline;

-- 2. The unbroken record: every meeting, and the fact that not one produced a split vote.
SELECT meeting_date, total_resolutions, unanimous, abstentions, split_votes
FROM meetings
ORDER BY meeting_date;

-- 3. Unanimity when all members voted = 223 / (228 - 5 recusal abstentions) = 100%.
SELECT SUM(unanimous)                                   AS unanimous,
       SUM(total_resolutions) - SUM(abstentions)        AS votes_all_present,
       ROUND(100.0 * SUM(unanimous)
             / (SUM(total_resolutions) - SUM(abstentions)), 1) AS unanimity_pct
FROM meetings;

-- 4. Who did the asking, recomputed from the normalized junction table (not a stored total).
SELECT bm.name, bm.role,
       SUM(rq.question_count)                                   AS questions,
       ROUND(100.0 * SUM(rq.question_count)
             / (SELECT SUM(question_count) FROM resolution_questions), 1) AS pct
FROM resolution_questions rq
JOIN board_members bm ON bm.member_id = rq.member_id
GROUP BY rq.member_id
ORDER BY questions DESC;

-- 5. The most-interrogated resolutions, and how many members engaged each.
SELECT qr.resolution_no, qr.total_questions,
       COUNT(rq.member_id) AS members_engaged
FROM questioned_resolutions qr
JOIN resolution_questions rq ON rq.resolution_no = qr.resolution_no
GROUP BY qr.resolution_no
ORDER BY qr.total_questions DESC, members_engaged DESC
LIMIT 10;

-- 6. The 156 resolutions that drew no question at all = 228 total minus the 72 questioned.
SELECT (SELECT SUM(total_resolutions) FROM meetings)
       - (SELECT COUNT(*) FROM questioned_resolutions) AS resolutions_with_no_question;

-- 7. Public participation: the five meetings, out of 24, where any resident spoke.
SELECT meeting_date, public_speakers, notable_items
FROM meetings
WHERE public_speakers > 0
ORDER BY meeting_date;

-- 8. The peer test: Pittsburgh Water's 100% against the sampled peer boards' 69%.
SELECT utility, votes, unanimous, contested, unanimity_pct, longest_meeting_min
FROM peer_boards
ORDER BY unanimity_pct DESC;

-- 9. Spending authorized per year, without a single no vote behind any of it.
SELECT substr(meeting_date, 1, 4) AS year,
       COUNT(*)                    AS meetings,
       SUM(total_resolutions)      AS resolutions,
       ROUND(SUM(dollars_millions), 2) AS dollars_millions
FROM meetings
GROUP BY year
ORDER BY year;
