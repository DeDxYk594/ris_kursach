DELETE FROM `session`
WHERE session_id=% OR valid_until<NOW();
