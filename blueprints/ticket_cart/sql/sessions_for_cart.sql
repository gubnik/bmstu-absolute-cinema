SELECT 
    s.session_id,
    f.title as film_title,
    h.name as hall_name,
    s.session_date,
    s.session_time,
    CONCAT(f.title, ' | ', DATE_FORMAT(s.session_date, '%d.%m.%Y'), ' ', TIME_FORMAT(s.session_time, '%H:%i'), ' | ', h.name) as display_name,
    (SELECT COUNT(*) FROM cinema.tickets t WHERE t.session_id = s.session_id AND t.is_sold = 0) as available_tickets
FROM
    cinema.sessions s
    JOIN cinema.films f ON s.film_id = f.film_id
    JOIN cinema.halls h ON s.hall_id = h.hall_id
WHERE
    s.session_date >= CURDATE()
HAVING
    available_tickets > 0
ORDER BY
    s.session_date, s.session_time;

