#!/usr/bin/python
import psycopg2
import sys

class Pgconnection(Exception):

    def __init__(self, logging, pgconnpram):
        self.longquery={}
        # Try to connect
        try:
            self.logging = logging
            myconn = "dbname=" + pgconnpram['dbconnname'] + " " + "user=" + pgconnpram['dbconnuser'] + " " + "host=" + pgconnpram['dbendpoint'] \
                     + " " + "port=" + pgconnpram['dbconnport'] + " " + "password=" + pgconnpram['dbconnpass']
            self.conn = psycopg2.connect(myconn)

        except StandardError:
            logging.error("I am unable to connect to the database. {0}".format(sys.exc_info()))
            exit(0)

    # Capturing long running query
    def longrunningquery(self):
        try:
            #query = "SELECT pid, now() - pg_stat_activity.query_start AS duration, left(query,50), state FROM pg_stat_activity " \
            #        "WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes' AND state != 'idle';"
            query = "SELECT pid, now() - pg_stat_activity.query_start AS duration, left(query,50), state FROM pg_stat_activity " \
                    "WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';"
            cur = self.conn.cursor()
            cur.execute(query)
            rows= cur.fetchall()
            for row in rows:
                # Now append fetched result of pid:longquery into dict
                self.longquery[row[0]] = row[2]

        except StandardError:
            self.logging.error("I am unable to connect to the database. {0}".format(sys.exc_info()))
            exit()
        except (Exception, psycopg2.Error) as error:
            self.logging.error("Error while fetching from PostgreSQL", error)
            exit()
        finally:
            # Closing database connection.
            cur.close()
            self.conn.close()
        #Returning here so that our cursor and connection are closed.
        return self.longquery