import boto3
import os
import json
import salt.client
import time
import datetime
import subprocess
import boto.utils


class SaltConsumer():
    def __init__(self):
        #Specify region from which message need to be consumed based on region in which saltmaster is in, below code is for calculating region automatically
        data = boto.utils.get_instance_identity()
        self.region_name = data['document']['region']
        os.environ['AWS_DEFAULT_REGION'] = self.region_name

        # Fetch SQS queue name
        self.client = boto3.client('sqs')
        self.queues = self.client.list_queues(QueueNamePrefix='diag_saltmaster')
        self.queue_url = self.queues['QueueUrls'][0]
        self.maxbatchmessages=3

    def consumefrom(self):
        while True:
            messages = self.client.receive_message(QueueUrl=self.queue_url,
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

                    #Acceptable result:
                    #('soh-mkt-stage2-1\n', None)

                    #Below condition is to first check if particular minion is added to particular saltmaster, in case of salt minion not part of saltmaster key we would get result as ('', None)
                    if saltkeyexist[0] == '':
                        # Deleting the message from queue as this instanceid doesn't belong to this saltmaster
                        self.client.delete_message(QueueUrl=self.queue_url, ReceiptHandle=message['ReceiptHandle'])
                    else:
                        #Fetch the campaign host ID and check for minion state
                        saltpingresult=self.saltping('*'+messagedict['instanceid']+'*')

                        #Check saltpingresult, in case of salt minion stopped we would get an empty dict in this case, or if its not responding it might give result like {'sparknz-mid-prod3-1': False}
                        if not bool(saltpingresult) or saltpingresult[saltpingresult.keys()[0]]==False:
                            output="There is some issue with salt minion, please check if its working fine."
                            self.sendemptyresponsetodynamo(messagedict['run_id'],messagedict['instanceid'],output)
                            # Deleting the message from queue once processed
                            self.client.delete_message(QueueUrl=self.queue_url, ReceiptHandle=message['ReceiptHandle'])

                        #Below condition on output {u'soh-mkt-stage2-1': True}
                        elif saltpingresult[saltpingresult.keys()[0]]==True:
                            messagedict['minionid']=saltpingresult.keys()[0]

                            #Check for Debian version as Debian8 version is unsupported
                            deb_version=self.saltgetosversion(messagedict['minionid'])
                            '''
                            print(deb_version)
                            {u'titan-mkt-stage1-2': u'9.11'}
                            (u'9.11', <type 'unicode'>)
                            '''

                            #Str to convert unicode to string '9.11', float to convert 9.11 to ignore ValueError: invalid literal for int() with base 10: '9.11', int to convert float value to itn
                            deb_version_int = int(float(str(deb_version[messagedict['minionid']])))
                            '''
                            print(deb_version_int,type(deb_version_int))
                            (9, < type 'int' >)
                            '''

                            if deb_version_int<9:
                                output="Campaign on Debian8 isn't supported as of now, for updates please follow https://wiki.corp.adobe.com/display/neolane/Diagnostic+tooling+working"
                                self.sendemptyresponsetodynamo(messagedict['run_id'], messagedict['instanceid'], output)
                                # Deleting the message from queue once processed
                                self.client.delete_message(QueueUrl=self.queue_url,ReceiptHandle=message['ReceiptHandle'])
                            else:
                                print(messagedict)
                                #Sending salt async command to minion
                                if 'workflow_name' in messagedict:
                                    workflow_name = messagedict['workflow_name']
                                else:
                                    workflow_name = None
                                saltasynccommand = self.saltcommand(messagedict['minionid'],messagedict['instanceid'],messagedict['module'],
                                                             messagedict['run_id'],messagedict['airflowproducingtime'],
                                                             messagedict['saltconsumingfromsqstime'],messagedict['build'],workflow_name)
                                # Deleting the message from queue once processed
                                self.client.delete_message(QueueUrl=self.queue_url, ReceiptHandle=message['ReceiptHandle'])
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

    def saltgetosversion(self,minionid):
        local = salt.client.LocalClient()
        osversion=local.cmd(minionid,'cmd.run',['sudo cat /etc/debian_version'])
        return osversion

    def saltcommand(self,minionid,instanceid,module,runid,airflowproduce,saltconsumesqs, build, workflow_name):
        local = salt.client.LocalClient()
        output = local.cmd_async(minionid, module, [airflowproduce, saltconsumesqs, str(datetime.datetime.utcnow()), instanceid, build, workflow_name], jid=runid, ret='test_timestamp')
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
