import boto3
import os
import json
import salt.client
import time
import datetime


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
                    
                    #Print message
                    print(messagedict)
                    messagedict['saltconsumingfromsqstime'] = str(datetime.datetime.utcnow())

                    #Fetch the campaign host ID and check for minion existence
                    saltpingresult=self.saltping(messagedict['instanceid'])

                    if saltpingresult[messagedict['instanceid']]==True:
                        #Sending salt async command to minion
                        saltasynccommand = self.saltcommand(messagedict['instanceid'],messagedict['module'],
                                                         message['MessageId'],messagedict['run_id'],messagedict['airflowproducingtime'],
                                                         messagedict['saltconsumingfromsqstime'])
                        # Deleting the message from queue once processed
                        self.client.delete_message(QueueUrl=queue_url, ReceiptHandle=message['ReceiptHandle'])

                    else:
                        # Deleting the message from queue once processed
                        self.client.delete_message(QueueUrl=queue_url, ReceiptHandle=message['ReceiptHandle'])
                        self.sendemptyresponsetodynamo()
            else:
                time.sleep(5)
                print("The queue is empty")

    def saltping(self,instanceid):
        local = salt.client.LocalClient()
        output = local.cmd(instanceid, 'test.ping')
        return output

    def saltcommand(self,instanceid,module,message,runid,airflowproduce,saltconsumesqs):
        local = salt.client.LocalClient()
        output = local.cmd_async(instanceid, module, [airflowproduce, saltconsumesqs, str(datetime.datetime.utcnow())], jid=runid, ret='test_timestamp')
        return output

    def sendemptyresponsetodynamo(self):
