SELECT 
    s.session_id,
    COALESCE(fts.ts_title, f.title) AS film_title,
    COALESCE(hts.ts_name, h.name) as hall_name,
    s.session_date,
    s.session_time,
    CONCAT(
        COALESCE(fts.ts_title, f.title),
        ' | ',
        DATE_FORMAT(s.session_date, '%%d.%%m.%%Y'),
        ' ',
        TIME_FORMAT(s.session_time, '%%H:%%i'),
        ' | ',
        COALESCE(hts.ts_name, h.name)
    ) as display_name,
    (SELECT COUNT(*) FROM cinema.tickets t WHERE t.session_id = s.session_id AND t.is_sold = 0) as available_tickets
FROM
    cinema.sessions s
LEFT JOIN cinema.films f ON s.film_id = f.film_id
LEFT JOIN cinema.films_ts fts ON s.film_id = fts.film_id AND fts.locale = %s
LEFT JOIN cinema.halls h ON s.hall_id = h.hall_id
LEFT JOIN cinema.halls_ts hts ON hts.hall_id = h.hall_id AND hts.locale = fts.locale
WHERE
    s.session_date >= CURDATE()
HAVING
    available_tickets > 0
ORDER BY
    s.session_date, s.session_time;

