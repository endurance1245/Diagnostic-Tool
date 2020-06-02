#!/usr/bin/python

activate_this = "/root/diagtool/bin/activate_this.py"
with open(activate_this) as f:
    code = compile(f.read(), activate_this, 'exec')
    exec (code, dict(__file__=activate_this))

import psycopg2
import sys


class PgConnection(Exception):

    def __init__(self, logging, pgconnpram):
        self.longquerylist = []
        self.logging = logging
        self.myconn = "dbname=" + pgconnpram['dbconnname'] + " " + "user=" + pgconnpram['dbconnuser'] + " " + "host=" + \
                      pgconnpram['dbendpoint'] \
                      + " " + "port=" + pgconnpram['dbconnport'] + " " + "password=" + pgconnpram['dbconnpass']

    def connecttodb(self):
        # Try to connect
        try:
            self.conn = psycopg2.connect(self.myconn)
        except StandardError:
            self.logging.error("I am unable to connect to the database. {0}".format(sys.exc_info()))
            return "Unable to connect to database"

    # Capturing long running query
    def longrunningquery(self):
        # Connection to database
        dbconnection = self.connecttodb()

        # Below condition to help return in case we are unable to connect to database
        if dbconnection == "Unable to connect to database":
            return dbconnection
        else:
            pass

        try:
            # Testing using below query as >5 minutes queries were hard to find against test instance futureadvisor-rt-prod6-2
            '''
            query = "SELECT pid, now() - pg_stat_activity.query_start AS duration, left(query,100), state FROM pg_stat_activity " \
                    "WHERE (now() - pg_stat_activity.query_start) < interval '5 minutes' AND query NOT LIKE 'CLOSE CUR%' AND" \
                    " query NOT LIKE 'COMMIT' AND query NOT LIKE '%GetDate() LIMIT 1 OFFSET%' AND query not like 'autovacuum%';"
            '''

            query = "SELECT pid, now() - pg_stat_activity.query_start AS duration, left(query,100), state FROM pg_stat_activity " \
                    "WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes' AND query NOT LIKE 'CLOSE CUR%' AND" \
                    " query NOT LIKE 'COMMIT' AND query NOT LIKE '%GetDate() LIMIT 1 OFFSET%';"
            cur = self.conn.cursor()
            cur.execute(query)
            rows = cur.fetchall()

            for row in rows:
                # Now append fetched result of pid:longquery into dict
                self.longquerydict = {}
                self.longquerydict["pid"] = row[0]
                self.longquerydict["Longrunningquery"] = row[2]
                self.longquerylist.append(self.longquerydict)
        except StandardError:
            self.logging.error("I am unable to connect to the database table. {0}".format(sys.exc_info()))
            return "UndefinedTable"
        except (Exception, psycopg2.Error) as error:
            self.logging.error("Error while fetching from PostgreSQL", error)
            return "Error while fetching from PostgreSQL"
        # Usecase for the else clause is to perform actions that must occur when no exception occurs and that do not occur when exceptions are handled.
        else:
            # Closing database connection.
            cur.close()
            self.conn.close()

            # Keeping for debugging sometimes
            f = open("/tmp/dboutput", "w")
            f.write(str(self.longquerylist))
            f.close()
            return self.longquerylist