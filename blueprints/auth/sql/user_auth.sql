SELECT
    user_id,
    login,
    password,
    role
FROM
    cinema.users
WHERE
    login = %s AND password = %s;

