UPDATE cinema.tickets 
SET is_sold = 1, sold_datetime = NOW()
WHERE ticket_id = %s AND is_sold = 0;

