db_query_for_max_connection = "SELECT COUNT(*) connections_awaiting_lock FROM pg_locks WHERE granted = false GROUP BY pid;"
db_query_for_blocking = "SELECT blocked_locks.pid AS blocked_pid, " \
                "blocked_activity.usename AS blocked_user, blocking_activity.query AS blocking_statement, " \
                "now() - blocking_activity.query_start AS blocking_duration, blocking_locks.pid AS blocking_pid, " \
                "blocking_activity.usename AS blocking_user, blocked_activity.query AS blocked_statement, " \
                "now() - blocked_activity.query_start AS blocked_duration FROM pg_catalog.pg_locks AS blocked_locks " \
                "JOIN pg_catalog.pg_stat_activity AS blocked_activity ON blocked_activity.pid = blocked_locks.pid " \
                "JOIN pg_catalog.pg_locks AS blocking_locks ON blocking_locks.locktype = blocked_locks.locktype " \
                "AND blocking_locks.DATABASE IS NOT DISTINCT FROM blocked_locks.DATABASE " \
                "AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation " \
                "AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page " \
                "AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple " \
                "AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid " \
                "AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid " \
                "AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid " \
                "AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid " \
                "AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid " \
                "AND blocking_locks.pid != blocked_locks.pid " \
                "JOIN pg_catalog.pg_stat_activity AS blocking_activity ON blocking_activity.pid = blocking_locks.pid " \
                "WHERE NOT blocked_locks.granted;"
db_query_for_deadlock_count = "SELECT deadlocks, datname FROM pg_stat_database WHERE datname = current_database();"
db_query_for_acquired_lock_modes = "SELECT virtualtransaction, relation::regclass, locktype, page, " \
                        "tuple, mode, granted, transactionid FROM pg_locks ORDER BY granted, virtualtransaction;"
db_query_for_long_running = "SELECT pid, now() - pg_stat_activity.query_start AS duration, left(query,100), state " \
                            "FROM pg_stat_activity WHERE (now() - pg_stat_activity.query_start) > interval '5 " \
                            "minutes' AND query NOT LIKE 'CLOSE CUR%' AND query NOT LIKE 'COMMIT' AND query NOT " \
                            "LIKE '%GetDate() LIMIT 1 OFFSET%' AND query not like 'autovacuum%' AND state != 'idle';"

#Testing using below query as >5 minutes queries were hard to find against test instance futureadvisor-rt-prod6-2
db_query_for_long_running_testing = "SELECT pid, now() - pg_stat_activity.query_start AS duration, left(query,100), " \
                                    "state FROM pg_stat_activity WHERE (now() - pg_stat_activity.query_start) < " \
                                    "interval '5 minutes' AND query NOT LIKE 'CLOSE CUR%' AND query NOT LIKE " \
                                    "'COMMIT' AND query NOT LIKE '%GetDate() LIMIT 1 OFFSET%' AND query not " \
                                    "like 'autovacuum%';"
