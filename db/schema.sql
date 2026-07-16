PRAGMA foreign_keys = ON;

-- One row per board meeting (the census spine).
CREATE TABLE meetings (
  meeting_no        INTEGER PRIMARY KEY,
  meeting_date      TEXT NOT NULL,
  total_resolutions INTEGER NOT NULL,
  unanimous         INTEGER NOT NULL,
  abstentions       INTEGER NOT NULL,
  split_votes       INTEGER NOT NULL,
  questions_asked   INTEGER NOT NULL,   -- counted per meeting (sums to 131)
  dollars_millions  REAL    NOT NULL,
  public_speakers   INTEGER NOT NULL,
  notable_items     TEXT
);

CREATE TABLE board_members (
  member_id             TEXT PRIMARY KEY,   -- e.g. 'sciulli'
  name                  TEXT NOT NULL,
  role                  TEXT,
  meetings_active       INTEGER,
  questions_by_meeting  INTEGER,            -- per-meeting count (sums to 131)
  questions_by_resolution INTEGER          -- resolution-attributed count (sums to 96)
);

-- The 72 resolutions that drew at least one recorded question.
CREATE TABLE questioned_resolutions (
  resolution_no   TEXT PRIMARY KEY,        -- e.g. 'No. 74 of 2024'
  year            INTEGER NOT NULL,
  total_questions INTEGER NOT NULL
);

-- Normalized junction: who asked how many questions on which resolution (non-zero cells only).
CREATE TABLE resolution_questions (
  resolution_no  TEXT NOT NULL REFERENCES questioned_resolutions(resolution_no),
  member_id      TEXT NOT NULL REFERENCES board_members(member_id),
  question_count INTEGER NOT NULL CHECK (question_count > 0),
  PRIMARY KEY (resolution_no, member_id)
);
CREATE INDEX idx_rq_member ON resolution_questions(member_id);

CREATE TABLE peer_boards (
  utility          TEXT PRIMARY KEY,
  jurisdiction     TEXT,
  meetings_sampled INTEGER,
  sampling_method  TEXT,
  votes            INTEGER,
  unanimous        INTEGER,
  contested        INTEGER,
  abstentions      INTEGER,
  unanimity_pct    REAL,
  longest_meeting_min INTEGER,
  exemplar         TEXT
);

-- Headline figures, computed in SQL so a reader can see the arithmetic.
CREATE VIEW v_headline AS
SELECT
  (SELECT COUNT(*)                 FROM meetings)                     AS meetings,
  (SELECT SUM(total_resolutions)   FROM meetings)                     AS resolutions,
  (SELECT SUM(unanimous)           FROM meetings)                     AS unanimous,
  (SELECT SUM(split_votes)         FROM meetings)                     AS split_votes,
  (SELECT SUM(abstentions)         FROM meetings)                     AS abstentions,
  (SELECT ROUND(SUM(dollars_millions),2) FROM meetings)              AS dollars_millions,
  (SELECT SUM(public_speakers)     FROM meetings)                     AS public_speakers,
  (SELECT COUNT(*)                 FROM questioned_resolutions)       AS resolutions_questioned,
  (SELECT SUM(total_resolutions)   FROM meetings)
    - (SELECT COUNT(*)             FROM questioned_resolutions)       AS resolutions_unquestioned,
  (SELECT SUM(question_count)      FROM resolution_questions)         AS questions_attributed;

-- Recompute each member's resolution-attributed total from the junction table.
CREATE VIEW v_questions_by_member AS
SELECT bm.name, bm.role,
       COALESCE(SUM(rq.question_count), 0) AS questions_by_resolution
FROM board_members bm
LEFT JOIN resolution_questions rq ON rq.member_id = bm.member_id
GROUP BY bm.member_id
ORDER BY questions_by_resolution DESC;
