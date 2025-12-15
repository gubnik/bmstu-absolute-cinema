SELECT 
    s.session_id,
    CONCAT(f.title, ' | ', DATE_FORMAT(s.session_date, '%d.%m.%Y'), ' ', TIME_FORMAT(s.session_time, '%H:%i'), ' | ', h.name) as display_name
FROM
    cinema.sessions s
    JOIN cinema.films f ON s.film_id = f.film_id
    JOIN cinema.halls h ON s.hall_id = h.hall_id
WHERE
    s.session_date >= CURDATE()
ORDER BY
    s.session_date, s.session_time;

