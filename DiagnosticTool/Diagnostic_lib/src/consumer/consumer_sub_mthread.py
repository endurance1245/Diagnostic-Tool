import boto3
import os
import json
import salt.client
import time
import datetime
import subprocess


class SaltConsumer():
    def __init__(self):
        #Specify region from which message need to be consumed based on region in which saltmaster is in
        os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'
        # create a boto3 client
        self.client = boto3.client('sqs')
        self.queuename='diag_saltmaster_us-west-2'
        self.maxbatchmessages=3

    def consumefrom(self):
        # get a list of queues, we get back a dict with 'QueueUrls' as a key with a list of queue URLs
        queues = self.client.list_queues(QueueNamePrefix=self.queuename)
        queue_url = queues['QueueUrls'][0]

        while True:
            messages = self.client.receive_message(QueueUrl=queue_url,
                                          MaxNumberOfMessages = self.maxbatchmessages)  # adjust MaxNumberOfMessages if needed
            if 'Messages' in messages:  # when the queue is exhausted, the response dict contains no 'Messages' key
                for message in messages['Messages']:  # 'Messages' is a list
                    #To check what message body we have consumed from SQS
                    # print(message['Body'])

                    # process the messages
                    messagedictencoded=json.loads(message['Body'])['Message']
                    #Remove encoding from messagedict
                    messagedict=json.loads(messagedictencoded.encode('ascii'))

                    #Print message downloaded from SQS queue
                    print(messagedict)
                    messagedict['saltconsumingfromsqstime'] = str(datetime.datetime.utcnow())

                    #Verify if salt minion key is added in saltmaster
                    saltkeyexist=self.saltkey(messagedict['instanceid'])
                    #Below condition is to first check if particular minion is added to particular saltmaster, in case of salt minion not part of saltmaster key we would get result as ('', None)
                    if saltkeyexist[0] == '':
                        # Deleting the message from queue as this instanceid doesn't belong to this saltmaster
                        self.client.delete_message(QueueUrl=queue_url, ReceiptHandle=message['ReceiptHandle'])
                    else:
                        #Fetch the campaign host ID and check for minion state
                        saltpingresult=self.saltping(messagedict['instanceid'])

                        #Check saltpingresult, in case of salt minion stopped we would get an empty dict in this case
                        if not bool(saltpingresult):
                            output="There is some issue with salt minion, please check if its working fine."
                            self.sendemptyresponsetodynamo(messagedict['run_id'],messagedict['instanceid'],output)
                            # Deleting the message from queue once processed
                            self.client.delete_message(QueueUrl=queue_url, ReceiptHandle=message['ReceiptHandle'])

                        elif saltpingresult[messagedict['instanceid']]==True:
                            #Sending salt async command to minion
                            saltasynccommand = self.saltcommand(messagedict['instanceid'],messagedict['module'],
                                                         messagedict['run_id'],messagedict['airflowproducingtime'],
                                                         messagedict['saltconsumingfromsqstime'])
                            # Deleting the message from queue once processed
                            self.client.delete_message(QueueUrl=queue_url, ReceiptHandle=message['ReceiptHandle'])
            else:
                time.sleep(5)
                print("The queue is empty")

    def saltkey(self,instanceid):
        p1 = subprocess.Popen(['salt-key', '-L'], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(['grep', instanceid], stdin=p1.stdout, stdout=subprocess.PIPE)
        p3 = p2.communicate()
        return p3


    def saltping(self,instanceid):
        local = salt.client.LocalClient()
        output = local.cmd(instanceid, 'test.ping')
        return output

    def saltcommand(self,instanceid,module,runid,airflowproduce,saltconsumesqs):
        local = salt.client.LocalClient()
        output = local.cmd_async(instanceid, module, [airflowproduce, saltconsumesqs, str(datetime.datetime.utcnow())], jid=runid, ret='test_timestamp')
        return output

    def sendemptyresponsetodynamo(self,messageid,instanceid,output):
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
                'output': output
            }
        )