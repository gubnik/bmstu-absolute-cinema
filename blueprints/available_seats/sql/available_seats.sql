SELECT 
    t.ticket_id AS 'ID билета',
    t.row_num AS 'Ряд',
    t.seat_number AS 'Место',
    CONCAT(t.price, ' руб.') AS 'Цена',
    CASE 
        WHEN t.is_sold = 0 THEN '✅ Свободно'
        ELSE '❌ Продано'
    END AS 'Статус'
FROM
    cinema.tickets t
WHERE
    t.session_id = %s
    AND t.is_sold = 0
ORDER BY
    t.row_num, t.seat_number;

