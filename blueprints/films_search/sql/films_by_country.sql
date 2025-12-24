SELECT 
    f.film_id AS film_id,
    COALESCE(ts.ts_title, f.title) AS title,
    COALESCE(ts.ts_country, f.country) AS country,
    f.year AS year,
    COALESCE(ts.ts_director, f.director) AS director,
    f.studio AS studio,
    CONCAT(f.duration, '') AS duration
FROM 
    cinema.films f
LEFT JOIN 
    cinema.films_ts ts ON f.film_id = ts.film_id AND ts.locale = %s
WHERE 
    COALESCE(ts.ts_country, f.country) LIKE %s
ORDER BY 
    f.year DESC, f.title;

