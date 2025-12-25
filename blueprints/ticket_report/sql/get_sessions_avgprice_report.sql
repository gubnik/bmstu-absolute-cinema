SELECT * FROM cinema.sessions_avgprice_reports sa
WHERE
    sa.report_year = %s 
    AND sa.report_month = %s
ORDER BY
    sa.created_at DESC;

