INSERT INTO `session` (session_id, user_id, valid_until)
VALUES %s, %s, TIMESTAMP_ADD(WEEK, 1, NOW());
