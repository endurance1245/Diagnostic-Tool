from airflow.operators.bash_operator import BaseOperator
from airflow.utils.decorators import apply_defaults
import logging
import json, ast
import boto3
import os
import time
import datetime
logger = logging.getLogger(__name__)

class SaltOperator(BaseOperator):
    @apply_defaults
    def __init__(
            self,
            module_name: str,
            *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.module_name = module_name

    def execute(self,context):
        unique_id = context['dag_run'].run_id
        task_id = context['task_instance'].task_id
        task_instance = context['task_instance']
        minion_name = unique_id.split('&')[0]
        userldap = context['dag_run'].conf['userldap']
        build = context['dag_run'].conf['build']
        if 'workflow_name' in context['dag_run'].conf:
            workflow_name = context['dag_run'].conf['workflow_name']
        else:
            workflow_name = None
        #Produce message and get messageid
        result = self.producingmessage1(unique_id, task_id, minion_name,workflow_name,build)
        logger.info("Messageid returned after producing message to SQS queue for polling final output")
        logger.info("******")
        #Taking a break of 60 seconds to read message from SQS queue
        print("Starting sleep block")
        time.sleep(30)
        print("Ending sleep block")
        #Consume message with output from SQS queue on basis of messageid
        print("Consume message")
        msg = self.consumingmessagedynamo(unique_id, task_id)
        print("Message consumed")
        task_instance.xcom_push(key=unique_id, value=msg)

    #Producing message on SNS
    def producingmessage1(self, unique_id, task_id, minion_name, workflow_name, build):
        uniques_id = unique_id + '&' + task_id
        #"saltmaster":"10.89.98.165  
        if workflow_name is None:
            payload='{ "instanceid":"' + minion_name +'", "run_id":"'+uniques_id+'", "module":"'+self.module_name+'",' \
                        '"airflowproducingtime":"'+str(datetime.datetime.now())+'", "build":"' + build +'" }'
        else:
            payload='{ "instanceid":"' + minion_name +'", "run_id":"'+uniques_id+'", "module":"'+self.module_name+'",' \
                        '"airflowproducingtime":"'+str(datetime.datetime.now())+'", \
                        "build":"' + build + '", "workflow_name":"' + workflow_name + '" }'
        print(payload)
        # create a boto3 client
        client = boto3.client('sns', region_name='us-west-2')

        # Produce message to SNS
        response = client.publish(
            TopicArn='arn:aws:sns:us-west-2:483013340174:Diagnostic-Tooling',
            Message=payload
        )

    def consumingmessagedynamo(self, unique_id, task_id):
        uniques_id = unique_id + '&' + task_id
        # To fetch result from dynamodb
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
        # Get the service resource.
        dynamodb = boto3.resource('dynamodb')
        # Instantiate a table resource object without actually
        # creating a DynamoDB table. Note that the attributes of this table
        # are lazy-loaded: a request is not made nor are the attribute
        # values populated until the attributes
        # on the table resource are accessed or its load() method is called.
        table = dynamodb.Table('diagtool')
        while True:
            # Print out some data about the table.
            # This will cause a request to be made to DynamoDB and its attribute
            # values will be set based on the response.
            response = table.get_item(Key={'messageid': uniques_id})
            print(response)
            if 'Item' not in response:
                print("It seems messageid isn't populate yet {}", uniques_id)
                time.sleep(5)
            else:
                item = response['Item']
                item['airflowmessageconsume'] = str(datetime.datetime.now())
                print(item['output'])
                return(item['output'])
