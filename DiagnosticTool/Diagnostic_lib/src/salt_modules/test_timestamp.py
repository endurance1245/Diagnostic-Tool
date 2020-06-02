#!/usr/bin/python
activate_this = "/root/diagtool/bin/activate_this.py"
with open(activate_this) as f:
    code = compile(f.read(), activate_this, 'exec')
    exec (code, dict(__file__=activate_this))

import boto3
import os
from boto3 import client
import json
import datetime


def returner(ret):
    messagedict = {}
    messagedict['messagekeyid'] = ret['jid']
    messagedict['output'] = ret['return']
    messagedict['instanceid'] = ret['id']

    #Create file for saving final output
    file_temp = "/tmp/output"+ret['fun']

    # Preserving this code for debugging sometimes
    f = open(file_temp, "w")
    f.write(str(ret))
    f.close()

    # Producing the data to dynamoDB
    producetodynamo(ret['id'], ret['jid'], ret['return'], ret['fun_args'][0], ret['fun_args'][1], ret['fun_args'][2])


def producetodynamo(instanceid, messageid, output, airflowproducingtime,
                    saltconsumingfromsqstime, saltrunningasynccommandtime):
    os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

    # Get the service resource.
    dynamodb = boto3.resource('dynamodb')

    # Instantiate a table resource object without actually
    # creating a DynamoDB table. Note that the attributes of this table
    # are lazy-loaded: a request is not made nor are the attribute
    # values populated until the attributes
    # on the table resource are accessed or its load() method is called.
    table = dynamodb.Table('diagtool')
    # To insert result in dynamodb
    table.put_item(
        Item={
            'messageid': messageid,
            'instanceid': instanceid,
            'output': output,
            'airflowproducingtime': airflowproducingtime,
            'saltconsumingfromsqstime': saltconsumingfromsqstime,
            'saltrunningasynccommandtime': saltrunningasynccommandtime,
            'saltasynccommandcompletetime': str(datetime.datetime.utcnow())
        }
    )
