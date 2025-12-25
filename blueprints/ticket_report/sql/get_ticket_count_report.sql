SELECT * FROM cinema.ticket_count_reports tr
WHERE
    tr.report_year = %s 
    AND tr.report_month = %s
ORDER BY
    tr.created_at DESC;

