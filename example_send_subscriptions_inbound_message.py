# -*- coding: utf-8 -*-

import pdb
import argparse

import sys as sys
import logging as logging
import time as time

import oneapi as oneapi
import oneapi.models as models
import oneapi.utils as mod_utils

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--server", help="Address of the server (default=https://oneapi.infobip.com)")
parser.add_argument("username", help="Login")
parser.add_argument("password", help="Password")
parser.add_argument("address", help="Destination address")
parser.add_argument("-p", "--port", help="local port for delivery notification")
parser.add_argument("-d", "--data_format", help="Type of data used in request, can be url or json (default=url)")
parser.add_argument("-a", "--accept", help="Type of data used for response, can be url or json (default=url)")
parser.add_argument("-l", "--is_legacy", help="Support pre 2013 OMA specifications for URI", action='store_true')
args = parser.parse_args()

data_format = "url"
if args.data_format:
    if (args.data_format == "json"):
        data_format = "json"

port = 7090
if args.port:
    port = int(args.port)

header = None
if 'accept' in locals():
    if args.accept:
        header = {"accept" : args.accept}

# example:initialize-sms-client
sms_client = oneapi.SmsClient(args.username, args.password, args.server)
# ----------------------------------------------------------------------------------------------------

# example:prepare-message-without-notify-url
sms = models.SMSRequest()
sms.address = args.address
sms.notify_url = 'http://{}:{}'.format('localhost', port)
sms.callback_data = 'Any string'
sms.filter_criteria = "py_test_"+mod_utils.get_random_alphanumeric_string()
# ----------------------------------------------------------------------------------------------------

# example:send-message
result = sms_client.subscribe_messages_sent_notification(sms, header, data_format, args.is_legacy)
# store client correlator because we can later query for the delivery status with it:
resource_url = result.resource_url
# ----------------------------------------------------------------------------------------------------

if not result.is_success():
    print 'Error sending message:', result.exception
    sys.exit(1)

print 'Is success = ', result.is_success()
print 'Resource URL = ', result.resource_url

server = dummyserver.DummyWebWerver(port)
server.start_wait_and_shutdown(15)

requests = server.get_requests()
if not requests:
    print 'No requests received'
    sys.exit(1)

for method, path, http_body in requests:
    inbound_notif = oneapi.SmsClient.unserialize_inbound_message(http_body)
    print inbound_notif

#Few seconds later we can delete the subscription
time.sleep(10)

sms_client = oneapi.SmsClient(args.username, args.password, args.server)
sms_client.delete_messages_sent_subscription(resource_url)
# ----------------------------------------------------------------------------------------------------
