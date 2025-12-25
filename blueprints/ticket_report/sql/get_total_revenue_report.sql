SELECT * FROM cinema.total_revenue_reports tr
WHERE
    tr.report_year = %s 
    AND tr.report_month = %s
ORDER BY
    tr.created_at DESC;

