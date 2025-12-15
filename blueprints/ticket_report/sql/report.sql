SELECT
    tr.report_id,
    tr.report_month,
    tr.report_year,
    tr.total_tickets_sold,
    tr.total_revenue,
    tr.sessions_count,
    tr.avg_ticket_price,
    tr.created_at
FROM
    cinema.ticket_reports tr
WHERE
    tr.report_year = %s 
    AND tr.report_month = %s
ORDER BY
    tr.created_at DESC;

