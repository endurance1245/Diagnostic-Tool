activate_this = "/root/diagtool/bin/activate_this.py"
with open(activate_this) as f:
        code = compile(f.read(), activate_this, 'exec')
        exec(code, dict(__file__=activate_this))

import logging
import psutil
from datetime import datetime, timedelta
from campaign_db_connection import PgConnection
from db_parameters import DbParameters
from cloudwatch_connection import CloudWatchConnection
from database_exceptions import DBParameterNotFoundException, DataBaseException
from db_queries import db_query_to_check_bloating, db_query_to_check_db_version, table_size_query
from performance_insights import PerformanceInsights
from rds_connection import RDSConnection
from aws_exceptions import PerformanceInsightsConnectionException, CloudWatchConnectionException
from db_constants import SQL_QUERIES_LIMIT_FOR_PERFORMANCE_INSIGHTS

class BloatingAnalyze:

    def __init__(self, campaign_host):
        self.campaign_host = campaign_host

    def get_bloating(self):
        params = self.get_db_params()
        if "error" in params:
            return params
        else:
            result = []
            db_connection_obj = PgConnection(logging, params)
            try:
                db_query_result = db_connection_obj.get_result_from_db(db_query_to_check_bloating)
            except DataBaseException as err:
                logging.error(err)
                error_message = dict()
                error_message["error"] = str(err)
                return error_message
            for row in db_query_result:
                indexes = []
                found_same_table = False
                for table in result:
                    if "tablename" in table and row[2]==table["tablename"]:
                        indexes = table["indexes_bloat"]
                        index_result = {}
                        index_result["index_name"] = row[5]
                        index_result["indexbloat"] = str(row[6])
                        index_result["wastedindexbytes"] = str(row[7])
                        indexes.append(index_result)
                        found_same_table = True
                        break
                if found_same_table == False:
                    dict_result = self.make_result_for_bloating(row, indexes)
                    result.append(dict_result)
            return result

    def get_query_analysis(self):
        params = self.get_db_params()
        if "error" in params:
            return params
        else:
            result = []
            campaign_db_name = params['dbendpoint'].split(".")[0]
            region = params['dbendpoint'].split(".")[2]
            db_connection_obj = PgConnection(logging, params)
            try:
                db_version = db_connection_obj.get_result_from_db(db_query_to_check_db_version)
            except DataBaseException as err:
                logging.error(err)
                error_message = dict()
                error_message["error"] = str(err)
                return error_message
            db_version = float(db_version[0][0])
            if db_version >= 11.0:
                metric_queries = [
                        {
                            'Metric': 'db.load.avg',
                            'GroupBy': {
                                'Group': 'db.sql',
                                'Limit': SQL_QUERIES_LIMIT_FOR_PERFORMANCE_INSIGHTS
                            }
                        }
                    ]
                current_time = datetime.utcnow()
                start_time = current_time - timedelta(hours = 4)
                end_time = current_time
                try:
                    pi_response = PerformanceInsights(region).get_pi_resource_metrices(metric_queries, campaign_db_name ,start_time, end_time)
                except PerformanceInsightsConnectionException as err:
                    logging.error(err)
                    error_message = dict()
                    error_message["error"] = str(err)
                    return error_message
                if 'MetricList' in pi_response:
                    for metric in pi_response['MetricList'][1:]:
                        if 'Key' in metric:
                            query_with_wait_value = self.make_result_for_analysis(metric)
                            result.append(query_with_wait_value)
                        else:
                            result = {}
                            result["Performane Insights Output"] = "No SQL Queries present in Performance Insights"
                            return result
                else:
                    result = {}
                    result["Performane Insights Output"] = "Performance Insights Metric doesn't present"
            else:
                start_time = datetime.now() - timedelta(hours = 4) #last 4 hours data
                end_time = datetime.now()
                interval = 3600 #in seconds
                dimension_name = 'DBInstanceIdentifier'
                metrics = ['FreeableMemory','CPUUtilization','BurstBalance']
                warn_values = [80.0, 0.70, 20]
                critical_values  = [90.0, 0.90, 10]
                total_ram = psutil.virtual_memory().total #in bytes
                for (metric, warn_value, critical_value) in zip(metrics, warn_values, critical_values):
                    response = dict()
                    try:
                        metric_stat = CloudWatchConnection(region).get_avg_metric_statistics(metric, 
                                        dimension_name, campaign_db_name, start_time, end_time, interval)
                    except CloudWatchConnectionException as err:
                        logging.error(err)
                        metric_stat = err
                    if 'Datapoints' in metric_stat:
                        if metric_stat['Datapoints'] == []:
                            response[metric] = "Data isn't present on cloudwatch for " + metric
                        else:
                            response[metric] = self.make_result_for_cloudwatch_data(metric_stat['Datapoints'],metric, warn_value, critical_value, total_ram)
                    else:
                        response["error"] = metric_stat
                    result.append(response)
        return result

    def get_table_size(self, tablename):
        params = self.get_db_params()
        if "error" in params:
            return params
        else:
            result = []
            db_connection_obj = PgConnection(logging, params)
            try:
                table_size = db_connection_obj.get_result_from_db(table_size_query.format(tablename)) #output example - [(2655 kB ,)] 
                table_size = int(table_size[0][0].split()[0]) 
            except DataBaseException as err:
                logging.error(err)
                error_message = dict()
                error_message["error"] = str(err)
                return error_message
            table_size = table_size/1024 #in MB
        return table_size

    def make_result_for_bloating(self, row, indexes):
        result = {}
        index_result = {}
        result["current_database"] = row[0]
        result["schemaname"] = row[1]
        result["tablename"] = row[2]
        result["tablebloat"] = str(row[3])
        result["wastedbytes"] = str(row[4])
        index_result["index_name"] = row[5]
        index_result["indexbloat"] = str(row[6])
        index_result["wastedindexbytes"] = str(row[7])
        indexes.append(index_result)
        result["indexes_bloat"] = indexes
        table_size = self.get_table_size(row[2])
        result["state"] = self.get_table_state(row[3], table_size)
        return result
    
    def get_table_state(self, bloat_percent, table_size):
        table_size_ranges = [0, 30720, 51200] #in MBs
        bloat_percents = [70.0, 60.0, 50.0]
        state = "Table isn't bloated"
        for i in range(0,2):
            if table_size >= table_size_ranges[i] and table_size < table_size_ranges[i+1] and bloat_percent >= bloat_percents[i]:
                state = "Table is bloated"
                return state
        if table_size > table_size_ranges[2] and bloat_percent >= bloat_percents[2]:
            state = "Table is bloated, go for vacuum"
        return state

    def make_result_for_cloudwatch_data(self, datapoints, metric, warn_value, critical_value, total_ram):
        result = []
        for points in datapoints:
            json_result = {}
            json_result["Timestamp"] = points["Timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            json_result["Average"]  = points["Average"]
            json_result["Unit"] = points["Unit"]
            value = points["Average"]
            if metric == 'FreeableMemory':
                value = (float(total_ram - value)/total_ram) * 100
            if metric == 'BurstBalance':
                json_result["state"] = self.get_state_for_burst_balance(value, warn_value, critical_value)
            else:
                json_result["state"] = self.get_state_for_metric(value, warn_value, critical_value)
            result.append(json_result)
        key_result = {}
        key_result["data for last 4 hours"] = result
        return key_result

    def get_state_for_burst_balance(self, value, warn_value, critical_value):
        state = "Ok"
        if value <= warn_value and value > critical_value:
            state = "Warning"
        elif value <= critical_value:
            state = "Critical"
        return state
    
    def get_state_for_metric(self, value, warn_value, critical_value):
        state = "Ok"
        if value >= warn_value and value < critical_value:
            state = "Warning"
        elif value >= critical_value:
            state = "Critical"
        return state

    def make_result_for_analysis(self, metric):
        result = {}
        result["query"] = metric["Key"]["Dimensions"]["db.sql.statement"]
        result["wait values in last 4 hours"] = self.make_result_for_wait_values(metric["DataPoints"])
        return result
    
    def make_result_for_wait_values(self, datapoints):
        result = []
        for points in datapoints:
            json_result = {}
            json_result["Timestamp"] = points["Timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            json_result["wait value"] = points["Value"]
            json_result["state"] = self.get_state_for_metric(points["Value"], 0.70, 0.90)
            result.append(json_result)
        return result

    def get_db_params(self):
        try:
            params_obj = DbParameters()
            params = params_obj.get_db_parameters()
            return params
        except DBParameterNotFoundException as err:
            logging.error(err)
            error_message = dict()
            error_message["error"] = str(err)
            return error_message
