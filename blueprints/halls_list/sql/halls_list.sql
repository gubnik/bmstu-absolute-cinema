SELECT 
    h.hall_id AS hall_id,
    h.hall_number AS hall_number,
    COALESCE(ts.ts_name, h.name) AS name,
    h.total_seats AS total_seats,
    (SELECT COUNT(DISTINCT hs.row_num) FROM cinema.hall_schema hs WHERE hs.hall_id = h.hall_id) AS row_count,
    CONCAT(
        (SELECT MIN(hs.base_price) FROM cinema.hall_schema hs WHERE hs.hall_id = h.hall_id),
        ' - ',
        (SELECT MAX(hs.base_price) FROM cinema.hall_schema hs WHERE hs.hall_id = h.hall_id)
    ) AS price_range
FROM
    cinema.halls h
LEFT JOIN
    cinema.halls_ts ts ON h.hall_id = ts.hall_id AND ts.locale = %s
ORDER BY
    h.hall_number;
