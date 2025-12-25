SELECT 
    tc.report_month,
    tc.report_year,
    COALESCE(tc.total_tickets_sold, 0) AS total_tickets_sold,
    COALESCE(tr.total_revenue, 0) AS total_revenue,
    COALESCE(sa.sessions_count, 0) AS sessions_count,
    COALESCE(sa.avg_ticket_price, 0) AS avg_ticket_price,
    NOW() AS created_at
FROM 
    cinema.ticket_count_reports tc
LEFT JOIN 
    cinema.total_revenue_reports tr ON tc.report_month = tr.report_month
    AND tc.report_year = tr.report_year
LEFT JOIN 
    cinema.sessions_avgprice_reports sa ON tc.report_month = sa.report_month
    AND tc.report_year = sa.report_year
WHERE 
    tc.report_year = %s AND tc.report_month = %s;
