#!/usr/bin/python

import xml.etree.ElementTree as ET
import urllib2
import sys
import spidev
import logging
import getpass
import sleekxmpp
from optparse import OptionParser
import time
import RPi.GPIO as io
import thread
import serial

UART = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=.25)

io.setmode(io.BCM)


# - Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    from sleekxmpp.util.misc_ops import setdefaultencoding
    setdefaultencoding('utf8')
else:
    raw_input = input

#######################################################

# UART function
def readlineCR(port):
	print 'ReadlineCR'

	"""
        ch = port.read()
        rv = ''
        n = 0
        while (ch!='!') & (ch!='\r'): # & (ch!=''):

                rv += ch
                ch = port.read()
                n = n + 1
        print  'rv: %s',rv
	"""
	rv = UART.readline()
        return rv




# xmpp send function
def xmpp_send(toAddr,myMsg,**key):
    type = 'Normal'
    if ('type' in key):
        type = key['type']
    if type == 'Normal':
        xmpp.send_message(
            mto=toAddr,mbody=myMsg,mtype='chat')
    elif type == 'All':
        toAddr = 'P21451'
        xmpp.send_message(
            mto=toAddr,mbody=myMsg,mtype='groupchat')
####################################################


def NCAPClientUnJoin(NCAP_ID):
        #print ServiceType
        #print NCAP_ID
        """
        Checks to see if user is registered.
        Registers the user if a request is recieved.
        Unsubcribes if reques is recieved.

        returns FALSE for unregistered, TRUE for registered.
        """
        OnRoster=0

        tree = ET.parse('roster.xml')

        root = tree.getroot()

        # We need to replace this name with the jid from an incoming message
       # print name

        # This message needs to be extracted from the sleekxmpp library
        #message = msg['body']
        #print message

        # Setting our list to an empty array
        jid = []

        #We need to find all of our users in our roster and then we can find the JID attribute
        for user in root.findall('user'):
            jid.append(user.find('jid').text)
            #print(jid)

        # Check to see if the jid is in our list. If it is, we will respond to the message.
        try:
            OnRoster = 1
            jid.index(NCAP_ID)
            #print position
        except:
            # The .index function throws an error if there is no match, so we will use this as
            #our non-subscribed option.
            OnRoster = -1

        if OnRoster >= 0:
            print('Unsubscription Request Recieved')
    #We need to find all of our users in our roster and then we can find the JID attribute
            for user in root.findall('user'):
                test12= (user.find('jid').text)
                if test12 == NCAP_ID:
                    root.remove(user)
                    unsub=1
            tree.write('roster.xml')

        return OnRoster

#####################################

def NCAPClientJoin(NCAP_ID):

    """
    Checks to see if user is registered.
    Registers the user if a request is recieved.
    Unsubcribes if reques is recieved.

    returns FALSE for unregistered, TRUE for registered.
    """
    OnRoster=0

    tree = ET.parse('roster.xml')

    root = tree.getroot()

    # We need to replace this name with the jid from an incoming message
   # print name

    # This message needs to be extracted from the sleekxmpp library
    #message = msg['body']
    #print message

    # Setting our list to an empty array
    jid = []

    #We need to find all of our users in our roster and then we can find the JID attribute
    for user in root.findall('user'):
        jid.append(user.find('jid').text)
        #print(jid)

    # Check to see if the jid is in our list. If it is, we will respond to the message.
    try:
        jid.index(NCAP_ID)
        OnRoster = 1
        #print position
    except:
        # The .index function throws an error if there is no match, so we will use this as
        #our non-subscribed option.
        OnRoster = -1
        #ServiceType=='7108':
        print('Subscription Request Recieved')
        newuser = ET.Element("user")
        newuser.text = '\n'
        root.append(newuser)
        newuser.set('subscription', 'true')
        jabber=ET.Element("jid")
        newuser.append(jabber)
        jabber.text='%s' %(NCAP_ID)
        tree.write('roster.xml')

    return (OnRoster)*-1
##############################################################


def RosterCheck(NCAP_ID):
	tree = ET.parse('roster.xml')
	root = tree.getroot()
	jid = []
	Permission = 0

	for user in root.findall('user'):
		jid.append(user.find('jid').text)

	try:
		jid.index(NCAP_ID)
		Permission = 1
	except:
		Permission = 0
	return(Permission)






# This is the workhorse of all the read functions in this section. Thie method
# takes in a channelId, a timeout value, and what samplingmode is needed. This function
# is called upon when a '7211' message is recieved from the client. It returns back
# a single point of data. This function would be the only one you need to change in terms
# of your own design.

def ReadTransducerSampleDataFromAChannelOfATIM(timId, channelId, timeout, samplingMode):
	# Since we have the DHT11, we have one sensor responsible for both temperature and humidity.
	print 'Read Transducer Sample Data'
	

	if timId == '1':
		if len(channelId)<2:
			channelId='00'+channelId
		if len(channelId)<3:
			channelId='0'+channelId
                UARTport.flushInput()
                print 'Flushed Input'
		print channelId
		UART.write('128,'+channelId+'\r')
	#	UART.write('128,001\r')
		data = readlineCR(UART)
		


	errorCode = '0'
	#data = '1'
        return{'errorCode':errorCode, 'data':data}




# This is the function which is called by the '7213' message. Unlike the single channel read, the
# channelId is actually a string containing ";" seperated channels.

def ReadTransducerSampleDataFromMultipleChannelsOfATIM(timId, channelId, timeout, samplingMode):
	ChannelIDS = channelId.split(";")
	
	# Initializing the data list
	data = ""
	n = 1
	# We have a flag which allows us to track whether or not the value in question is the first value found.
	FirstValue = 0
	for ChannelID in ChannelIDS:
		DATA = ReadTransducerSampleDataFromAChannelOfATIM(timId, ChannelID, timeout, samplingMode)
		# This chunk of logic keeps the resulting data looking very pretty.
		if FirstValue == 0:
			data = data + str(DATA['data'])
			FirstValue = 1
		elif n==len(ChannelIDS):
			data = data + ";" + str(DATA['data'])
		else:
			data = data + ";" + str(DATA['data'])
		n = n+1
		print data
	errorCode = 0
	return{'channelId':channelId, 'data':data, 'errorCode':errorCode}


# This function is called when a '7212' message is recieved.
def ReadTransducerBlockDataFromAChannelOfATIM(timId, channelId, timeout, numberOfSamples, sampleInterval, startTime):
	time.sleep(int(startTime))
	BlockData = ""
	samplingMode = '5'
	for num in range(0,int(numberOfSamples)):
		BlockData = BlockData + str(ReadTransducerSampleDataFromAChannelOfATIM(timId,channelId, timeout, samplingMode)['data']) + ';'
		time.sleep(int(sampleInterval))
	errorCode = 0
	return{'errorCode':errorCode, 'data':BlockData}


def ReadTransducerBlockDataFromMultipleChannelsOfATIM(timId, channelId, timeout, numberOfSamples, sampleInterval, startTime):
	channelIds = channelId.split(";")
	time.sleep(int(startTime))
	samplingMode = '5'
	BlockData = ['']*len(channelIds)
	for SampleNum in range(0,int(numberOfSamples)):
		for ChanNum in range(0,len(channelIds)):
		#	print ChanNum
			BlockData[ChanNum] = BlockData[ChanNum] + ";" + str(ReadTransducerSampleDataFromAChannelOfATIM(timId, channelIds[ChanNum], timeout, samplingMode)['data']) 
		
		time.sleep(int(sampleInterval))
	errorCode = 0
	data = ''
	for ChanNum in range(0,len(channelIds)):
		data = data + '{' + BlockData[ChanNum] + '}'
		
	print(data)
	return{'errorCode':errorCode, 'data':data}


"""
def ReadTransducerBlockDataFromMultipleChannelsOfMultipleTIMs(timIds, numberOfChannelsOfTIM, channelIds, timeout, numberOfSamples, sampleInterval, startTime)
    channelIds = channelIds.split(";")
    timIds = timIds.split(";")
    samplingMode = '5'
    
    
    

    return {'errorCode':errorCode, 'data':data}


"""




def WriteTransducerSampleDataToAChannelOfATIM(timId, channelId, timeout, samplingMode, dataValue):

        if len(channelId)<2:
	        channelId='00'+channelId
        if len(channelId)<3:
                channelId='0'+channelId
        
        UART.write('001,'+channelId+','+dataValue+',\r')
	errorCode = 'p'
	print('you wrote it')
	errorCode=readlineCR(UARTport)	
        return {'errorCode':errorCode}


def WriteTransducerBlockDataToAChannelOfATIM(timId, channelId, timeout, numberOfSamples, sampleInterval, startTime, dataValue):
	data = dataValue.split(":")
	time.sleep(int(startTime))
	samplingMode = '5'
	for num in range(0,int(numberOfSamples)):
		errorCode = str(WriteTransducerSampleDataToAChannelOfATIM(timId, channelId, timeout, samplingMode, data[num]))
		time.sleep(float(sampleInterval)/1000)
	print errorCode
	return{'errorCode':errorCode}


def WriteTransducerSampleDataToMultipleChannelsOfATIM(timId, channelId, timeout, samplingMode, dataValues):
        ChannelIDS = channelId.split(";")
        
	data = dataValues.split(":")
        n = 0
        # We have a flag which allows us to track whether or not the value in question is the first val$
        FirstValue = 0
        for ChannelID in ChannelIDS:
                errorCode = WriteTransducerSampleDataToAChannelOfATIM(timId, ChannelID, timeout, '5', data[n])
		n = n+1
		time.sleep(.1)
        return{'channelId':channelId, 'data':data, 'errorCode':errorCode}





#############################################################
#       EVENT NOTIFICATION SERVICES
#############################################################

"""
def SubscribeSensorAlertService(timId, channelId, minMaxThreshold, sensorAlertSubscriber, samplingRate):
    # We need to possibly have another xml which manages this.
    
    
    
    return{'
    
    

"""

#############################################################
# Threading Functions
#############################################################

def Thread7108(MSG_Tuple, SenderInfo):
	MSG = dict(map(None, MSG_Tuple))
	OnRoster = NCAPClientJoin(SenderInfo[1])
	response = MSG['functionId'] + ',' + str(OnRoster) + ',' + 'You have been registered'
	xmpp_send(str(SenderInfo[1]), response)

def Thread7109(MSG_Tuple, SenderInfo):
	MSG = dict(map(None, MSG_Tuple))
	OnRoster = NCAPClientUnJoin(SenderInfo[1])
	response = MSG['functionId'] + ',' + str(OnRoster) + ',' + 'You have been removed from the Roster'
	xmpp_send(str(SenderInfo[1]), response)	


def Thread7211(MSG_Tuple, SenderInfo): 
        MSG = dict(map(None, MSG_Tuple))
	print MSG
	if RosterCheck(SenderInfo[1]) == 1:
		SensorData = ReadTransducerSampleDataFromAChannelOfATIM(MSG['timId'],MSG['channelId'],MSG['timeout'],MSG['samplingMode'])
		response = MSG['functionId'] + ',' + str(SensorData['errorCode']) + ',' +MSG['ncapId'] + ',' + MSG['timId'] + ',' + MSG['channelId'] + ',' + str(SensorData['data'])
		xmpp_send(str(SenderInfo[1]), response)
	elif RosterCheck(SenderInfo[1]) == 0:
		xmpp_send(str(SenderInfo[1]), 'ERROR: Not a registered user')

def Thread7212(MSG_Tuple, SenderInfo):
        MSG = dict(map(None, MSG_Tuple))
    	SensorData = ReadTransducerBlockDataFromAChannelOfATIM(MSG['timId'],MSG['channelId'], MSG['timeout'], MSG['numberOfSamples'], MSG['sampleInterval'], MSG['startTime'])
        response = MSG['functionId'] + ',' + str(SensorData['errorCode']) + ',' + MSG['ncapId'] + ',' + MSG['timId'] + ',' + MSG['channelId'] + ',' + str(SensorData['data'])
    	xmpp_send(str(SenderInfo[1]), response)

def Thread7213(MSG_Tuple, SenderInfo):
	MSG = dict(map(None, MSG_Tuple))
        SensorData = ReadTransducerSampleDataFromMultipleChannelsOfATIM(MSG['timId'], MSG['channelId'], MSG['timeout'], MSG['samplingMode'])
        response =  MSG['functionId'] + ',' + str(SensorData['errorCode']) + ',' + MSG['ncapId'] + ',' + MSG['timId'] + ',' + MSG['channelId'] + ',' + str(SensorData['data'])
        xmpp_send(str(SenderInfo[1]), response)

def Thread7214(MSG_Tuple, SenderInfo):
	MSG = dict(map(None, MSG_Tuple))
        SensorData = ReadTransducerBlockDataFromMultipleChannelsOfATIM(MSG['timId'], MSG['channelId'], MSG['timeout'], MSG['numberOfSamples'], MSG['sampleInterval'], MSG['startTime'])
        response =  MSG['functionId'] +  ',' + MSG['ncapId'] + ',' + MSG['timId'] + ',' + MSG['channelId'] + ',' +  str(SensorData['data'])
        xmpp_send(str(SenderInfo[1]), response)

"""        
def Thread7216(MSG_Tuple, SenderInfo):
    	MSG =  dict(map(None, MSG_Tuple))
        SensorData = ReadTranducerBlockDataFromMultipleChannelsOfMultipleTIMs(MSG['timIds'],MSG['channelIds', MSG['timeout'], MSG['numberOfSamples'], MSG['sampleInterval'], MSG['startTime'] )
        response = str(ErrorCode['errorCode'])+ ',' + MSG['ncapId'] + ',' + MSG['timIds'] + MSG['numberOfChannelsOfTIM'] + ',' + MSG['channelIds'] + ',' + MSG['transducerBlockDatas']
        xmpp_send(str(SenderInfo[1]), response)
"""

def Thread7217(MSG_Tuple, SenderInfo):
	MSG = dict(map(None, MSG_Tuple))
        ErrorCode = WriteTransducerSampleDataToAChannelOfATIM(MSG['timId'], MSG['channelId'], MSG['timeout'], MSG['samplingMode'], MSG['dataValue'])
        response = MSG['functionId']+ ',' + str(ErrorCode['errorCode']) + ',' + MSG['ncapId'] + ',' + MSG['timId'] + ',' + MSG['channelId']
        xmpp_send(str(SenderInfo[1]), response)
	
def Thread7218(MSG_Tuple, SenderInfo):
	MSG = dict(map(None, MSG_Tuple))
        ErrorCode = WriteTransducerBlockDataToAChannelOfATIM(MSG['timId'], MSG['channelId'], MSG['timeout'], MSG['numberOfSamples'], MSG['sampleInterval'], MSG['startTime'], MSG['dataValue'])
        response = MSG['functionId']+ ',' + str(ErrorCode['errorCode']) + ',' + MSG['ncapId'] + ',' + MSG['timId'] + ',' + MSG['channelId']
        xmpp_send(str(SenderInfo[1]), response)

def Thread7219(MSG_Tuple, SenderInfo):
	MSG = dict(map(None, MSG_Tuple))
	ErrorCode = WriteTransducerSampleDataToMultipleChannelsOfATIM(MSG['timId'], MSG['channelId'], MSG['timeout'], MSG['samplingMode'], MSG['dataValue'])
	response = MSG['functionId'] + ',' + str(ErrorCode['errorCode']) + ',' + MSG['ncapId'] + ',' + MSG['timId'] + ',' + MSG['channelId']
	xmpp_send(str(SenderInfo[1]), response)







###
# Place the Thread here
#def Thread7431(MSP_Tuple, SenderInfo)
#    MSG = dict(map(MSG_Tuple))
#       Status = SubscribeSensorAlertService(MSG['timId'],MSG['channelId'],MSG['minMaxThreshold'],MSG['sensorAlertSubscriber'], MSG['samplingRate'])
#       response = MSG['status']+ ',' + MSG['sensorAlertPublisher']+ ',' + MSG['subscriptionId']
#       xmpp_send(str(SenderInfo[1],response))


##############################################################

def MessageParse(msg):
	stringy = str(msg['body'])
	parse = stringy.split(",")
	functionId = parse[0]
	print functionId
	if functionId == '7108' or functionId == '7109':
		return {'functionId':functionId}
	ncapId =  parse[1]
	timId =  parse[2]
	channelId =  parse[3]
#	if functionId == '7421':
#	    minMaxThreshold = parse[4]
#	    sensorAlertSubscriber = parse[5]
#       samplingRate=parse[6]
#       return {'functionId':functionId, 'ncapId':ncapId, 'timId':timId, 'channelId':channelId, 'minMaxThreshold':minMaxThreshold, 'sensorAlertSubscriber':sensorAlertSubscriber, 'samplingRate':samplingRate }
	timeout =  parse[4]
	if functionId == '7212' or functionId == '7214' or functionId == '7218':
		#print 'I am in the nested if statement'
		numberOfSamples = parse[5]
		sampleInterval = parse[6]
		startTime = parse[7]
		if functionId == '7218':
			dataValue = parse[8]
			return {'functionId':functionId, 'ncapId':ncapId, 'timId':timId, 'channelId':channelId, 'timeout':timeout, 'numberOfSamples':numberOfSamples, 'sampleInterval':sampleInterval, 'startTime':startTime, 'dataValue':dataValue}
		return {'functionId':functionId, 'ncapId':ncapId, 'timId':timId, 'channelId':channelId, 'timeout':timeout, 'numberOfSamples':numberOfSamples, 'sampleInterval':sampleInterval, 'startTime':startTime}
	samplingMode = parse[5]
	if functionId == '7217':
		dataValue = parse[6]
		return {'functionId':functionId, 'ncapId':ncapId, 'timId':timId, 'channelId':channelId, 'timeout':timeout, 'samplingMode':samplingMode, 'dataValue':dataValue}
        if functionId == '7219':
                dataValue = parse[6]
                return {'functionId':functionId, 'ncapId':ncapId, 'timId':timId, 'channelId':channelId, 'timeout':timeout, 'samplingMode':samplingMode, 'dataValue':dataValue}


	#errorCode = 1
	return {'functionId':functionId, 'ncapId':ncapId, 'timId':timId, 'channelId':channelId, 'timeout':timeout, 'samplingMode':samplingMode} 

################################################################


class EchoBot(sleekxmpp.ClientXMPP):

    """
    A simple SleekXMPP bot that will echo messages it
    receives, along with a short thank you message.
    """

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        # The session_start event will be triggered when
        # the bot establishes its connection with the server
        # and the XML streams are ready for use. We want to
        # listen for this event so that we we can initialize
        # our roster.
        self.add_event_handler("session_start", self.start)

        # The message event is triggered whenever a message
        # stanza is received. Be aware that that includes
        # MUC messages and error messages.
        self.add_event_handler("message", self.message)

    def start(self, event):
        """
        Process the session_start event.
        Typical actions for the session_start event are
        requesting the roster and broadcasting an initial
        presence stanza.
        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
       
	self.send_presence()
        self.get_roster()

	global UARTport
	UARTport = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=0.25)


    def message(self, msg):
        """
        Process incoming message stanzas. Be aware that this also
        includes MUC messages and error messages. It is usually
        a good idea to check the messages's type before processing
        or sending replies.
        Arguments:
            msg -- The received message stanza. See the documentation
                   for stanza objects and the Message stanza to see
                   how it may be used.
        """
        if msg['type'] in ('chat', 'normal'):
	   print 'Recieved Message'
        MSG = MessageParse(msg)
	   #jabberid=msg['from']
	   #RC=RosterCheck(ncapId)
       # if(RC==0):
       #     xmpp_send(str(SenderInfo[1]), response)
	   
	if MSG['functionId']=='7108':
		print 'Recieved a 7108 message'
		thread.start_new_thread(Thread7108, (tuple(MSG.items()), ('from', msg['from'])))

        if MSG['functionId']=='7109':
                print 'Recieved a 7109 message'
                thread.start_new_thread(Thread7109, (tuple(MSG.items()), ('from', msg['from'])))
	

	if MSG['functionId'] == '7211':
		print 'Recieved a 7211 Message'
	        thread.start_new_thread(Thread7211, (tuple(MSG.items()), ('from', msg['from'])))

	if MSG['functionId'] == '7212':
		thread.start_new_thread(Thread7212, (tuple(MSG.items()), ('from', msg['from'])))

	if MSG['functionId'] == '7213':
		thread.start_new_thread(Thread7213, (tuple(MSG.items()), ('from', msg['from'])))

	if MSG['functionId'] == '7214':
		thread.start_new_thread(Thread7214, (tuple(MSG.items()), ('from', msg['from'])))


        if MSG['functionId'] == '7217':
                thread.start_new_thread(Thread7217, (tuple(MSG.items()), ('from', msg['from'])))

	if MSG['functionId'] == '7218':
		thread.start_new_thread(Thread7218, (tuple(MSG.items()), ('from', msg['from'])))

	if MSG['functionId'] == '7219':
		thread.start_new_thread(Thread7219, (tuple(MSG.items()), ('from', msg['from'])))

if __name__ == '__main__':
    # Setup the command line arguments.
    optp = OptionParser()

    # Output verbosity options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    # JID and password options.
    optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")
    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    if opts.jid is None:
        opts.jid = 'ncap@jahschwa.com'
    if opts.password is None:
        opts.password = 'password'

    # Setup the EchoBot and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    xmpp = EchoBot(opts.jid, opts.password)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0004') # Data Forms
    xmpp.register_plugin('xep_0060') # PubSub
    xmpp.register_plugin('xep_0199') # XMPP Ping

     # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect():
        # If you do not have the dnspython library installed, you will need
        # to manually specify the name of the server if it does not match
        # the one in the JID. For example, to use Google Talk you would
        # need to use:
        #
        # if xmpp.connect(('talk.google.com', 5222)):
        #     ...
        xmpp.process(block=True)
        print("Done")
    else:
        print("Unable to connect.")
