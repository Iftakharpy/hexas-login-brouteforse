CREATE TABLE IF NOT EXISTS exams (
    id TEXT,
	exam_id TEXT,
	exam_version INT,
    exam_score NUMERIC(4, 2),
	exam_date date,
	exam_type TEXT,
    exam_module TEXT
);
