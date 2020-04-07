# Wrapper to execute Salt Consumer using Multi-threading
import threading
import os
import sys
from consumer_sub_mthread import SaltConsumer


class ConsumerCaller(Exception):

    def __init__(self, thread_count):
        try:
            self.thread_count = int(thread_count)
        except ValueError as val_err:
            print("{0} is not an integer. Hint: Argument- {1}".format(thread_count, val_err))

    # Multi-threaded Salt Consumer execution Call
    def multi_thread_exe(self):
        try:
            # Creating threads
            threads = []
            for i in range(self.thread_count):
                sc = SaltConsumer()
                t = threading.Thread(name=i, target=sc.consumefrom)
                t.setDaemon(False)
                threads.append(t)
                t.start()
        except threading.ThreadError as th_err:
            print("Raised Exception: {0} \n Hint:{1}".format(sys.exc_info(), th_err))


if __name__ == "__main__":
    # Caller method
    mcl = ConsumerCaller(sys.argv[1])
    mcl.multi_thread_exe()

