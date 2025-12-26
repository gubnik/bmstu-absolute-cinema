SELECT 
    s.session_id AS session_id,
    CONCAT(
        COALESCE(fts.ts_title, f.title),
        ' | ',
        DATE_FORMAT(s.session_date, '%%d.%%m.%%Y'),
        ' ',
        TIME_FORMAT(s.session_time, '%%H:%%i'),
        ' | ',
        COALESCE(hts.ts_name, h.name)
    ) as display_name
FROM
    cinema.sessions s
LEFT JOIN cinema.films f ON f.film_id = s.film_id
LEFT JOIN cinema.films_ts fts ON s.film_id = fts.film_id AND fts.locale = %s
LEFT JOIN cinema.halls h ON h.hall_id = s.hall_id
LEFT JOIN cinema.halls_ts hts ON hts.hall_id = h.hall_id AND hts.locale = fts.locale
WHERE
    s.session_date >= CURDATE()
ORDER BY
    s.session_date, s.session_time;
