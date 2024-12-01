INSERT INTO `session` (session_id, ext_u_id, int_u_id, valid_until)
   VALUES (%s, %s, %s, TIMESTAMPADD(WEEK, 1, CURRENT_TIMESTAMP))
