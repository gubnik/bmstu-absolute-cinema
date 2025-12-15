SELECT 
    f.film_id AS 'ID',
    f.title AS 'Название',
    f.country AS 'Страна',
    f.year AS 'Год',
    f.director AS 'Режиссёр',
    f.studio AS 'Студия',
    CONCAT(f.duration, ' мин.') AS 'Длительность'
FROM
    cinema.films f
WHERE
    f.director LIKE %s
ORDER BY
    f.year DESC, f.title;

