INSERT INTO `session` (session_id, u_id, valid_until)
   VALUES (%s, %s, TIMESTAMPADD(WEEK, 1, CURRENT_TIMESTAMP))
