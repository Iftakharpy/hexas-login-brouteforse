-- join the exams and credentials tables
SELECT credentials.id, exams.exam_score, exams.exam_date, exams.exam_module, UPPER(credentials.username) 
    FROM exams LEFT JOIN credentials ON exams.id=credentials.id 
    WHERE UPPER(credentials.username) LIKE '%IFTAKHAR%' ORDER BY exam_score DESC;

-- join exams and credentials tables and ORDER BY exam_score DESC, exam_date DESC
SELECT credentials.id, exams.exam_score, exams.exam_date, exams.exam_module, UPPER(credentials.username)
    FROM exams LEFT JOIN credentials ON exams.id=credentials.id
    WHERE UPPER(credentials.username) LIKE '%IFTAKHAR%' ORDER BY exam_score desc, exam_date desc;

-- see the number of tests students attended
SELECT exams.id, COUNT(*) occurrences, UPPER(credentials.username)
    FROM exams LEFT JOIN credentials ON exams.id=credentials.id 
    GROUP BY exams.id, UPPER(credentials.username)
    HAVING UPPER(credentials.username) LIKE '%IFTAKHAR%' ORDER BY occurrences DESC;

-- check if a user exists
SELECT id, pass, UPPER(username) AS username FROM credentials WHERE UPPER(username) LIKE '%IFTAKHAR%';

-- rename table
ALTER TABLE credentials RENAME TO old_credentials;
