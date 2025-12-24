SELECT 
    t.ticket_id AS ticket_id,
    t.row_num AS row_num,
    t.seat_number AS seat_number,
    COALESCE(CONVERT(t.price USING utf8mb4), '') AS price,
    CASE
        WHEN t.is_sold = 0 THEN "false"
        ELSE "true"
    END AS is_sold
FROM
    cinema.tickets t
WHERE
    t.session_id = %s
ORDER BY
    t.row_num, t.seat_number;

