SELECT 
    h.hall_id AS 'ID',
    h.hall_number AS 'Номер зала',
    h.name AS 'Название',
    h.total_seats AS 'Всего мест',
    (SELECT COUNT(DISTINCT hs.row_num) FROM cinema.hall_schema hs WHERE hs.hall_id = h.hall_id) AS 'Рядов',
    CONCAT(
        (SELECT MIN(hs.base_price) FROM cinema.hall_schema hs WHERE hs.hall_id = h.hall_id),
        ' - ',
        (SELECT MAX(hs.base_price) FROM cinema.hall_schema hs WHERE hs.hall_id = h.hall_id),
        ' руб.'
    ) AS 'Диапазон цен'
FROM
    cinema.halls h
ORDER BY
    h.hall_number;

