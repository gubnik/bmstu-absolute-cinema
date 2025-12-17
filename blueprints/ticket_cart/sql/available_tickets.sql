SELECT 
    t.ticket_id,
    t.row_num,
    t.seat_number,
    t.price,
    t.is_sold,
    f.title as film_title,
    CONCAT(DATE_FORMAT(s.session_date, '%%d.%%m.%%Y'), ' ', TIME_FORMAT(s.session_time, '%%H:%%i')) as session_info
FROM
    cinema.tickets t
    JOIN cinema.sessions s ON t.session_id = s.session_id
    JOIN cinema.films f ON s.film_id = f.film_id
WHERE
    t.session_id = %s
ORDER BY
    t.row_num, t.seat_number;

