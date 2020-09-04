#!/usr/bin/python3
from evdev import InputDevice, categorize, ecodes, UInput
import sys
import yaml
import time
import threading
import subprocess
import shlex
import logging
import pprint
from logging.config import dictConfig

# set up logging
logging_config = dict(
    version = 1,
    formatters = {
        'f': {'format':
              '%(asctime)s %(levelname)-8s [%(funcName)s:%(lineno)d] %(message)s'}
    },
    handlers = {
        'c': {'class': 'logging.StreamHandler',
              'formatter': 'f',
              'level': logging.DEBUG,
              'stream': "ext://sys.stdout" },
        'f': {
              'class': 'logging.handlers.RotatingFileHandler',
              'formatter': 'f',
              'filename': '/var/log/antimicro-nonX.log',
              'maxBytes': 1000000,
              'backupCount': 4
        }
    },
    root = {
        'handlers': ['c','f'],
        'level': logging.DEBUG,
    },
)

dictConfig(logging_config)
logger = logging.getLogger(__name__)


def pressKeys(keylist):
    global ui
    logger.info("Pressing key combination: "+ " + ".join(keylist))
    for key in keylist:
        if key not in dir(ecodes):
            logger.error("Key "+key+" is not available for your keyboard, skipping")
            continue
        
        ui.write(ecodes.EV_KEY, ecodes.ecodes[key], 1)
    ui.syn()
    for key in keylist:
        if key not in dir(ecodes):
            logger.error("Key "+key+" is not available for your keyboard, skipping")
            continue
        
        ui.write(ecodes.EV_KEY, ecodes.ecodes[key], 0)
    ui.syn()


def runBGShell(command):
    logger.info("Executing "+ command)
    #split the command into an array
    subprocess.run(shlex.split(command), stdout=subprocess.PIPE, universal_newlines=True)

def keySequence(sequence):
    for item in sequence:
        pressKeys(item)
        time.sleep(0.5)

def getKeyName(number):
    if number not in ecodes.KEY:
        #look it up in ecodes.BTN
        if number not in ecodes.BTN:
            #must be invalid
            return None
        else:
            return ecodes.BTN[number]
    else:
        return ecodes.KEY[number]



""" Parse and load the configuration file """
conf = {}
def parseConfig(conffile):
    global conf
    with open(conffile, 'r') as stream:
        try:
            conf = yaml.load(stream, Loader=yaml.SafeLoader)
        except yaml.YAMLError as exc:
            logger.error(exc)
            logger.error("Unable to parse configuration file "+conffile)
            sys.exit(2)

if len(sys.argv) == 2:
    parseConfig(sys.argv[1])
else:
    logger.fatal("Usage: "+sys.argv[0]+" /path/to/config.yaml")
    sys.exit(1)

ui = None
#pprint.pprint(conf)


# build a dynamc keyboard capability based on what's configured
cap = {
    ecodes.EV_KEY : []
}
cap_unique = dict()
for key in conf['key_mapping']:
    # validate that it's an understood key code
    if key not in dir(ecodes):
            logger.error("Key "+key+" is not available for your keyboard, skipping")
            continue
    cap_unique[ecodes.ecodes[key]] = 1
    # add also the keys it needs to emit
    if type(conf['key_mapping'][key]) == str:
        # ignore, it's just running a command
        pass
    if type(conf['key_mapping'][key]) == list:
        logger.debug("key "+key+" -> list")
        if type(conf['key_mapping'][key][0]) == str:
            logger.debug("first item is str")
            for outkey in conf['key_mapping'][key]:
                if outkey not in dir(ecodes):
                    logger.error("Key "+outkey+" is not available for your keyboard, skipping")
                    continue
                cap_unique[ecodes.ecodes[outkey]] = 1
        if type(conf['key_mapping'][key][0]) == list:
            logger.debug("first item is list")
            for sequence in conf['key_mapping'][key]:
                for outkey in sequence:
                    if outkey not in dir(ecodes):
                        logger.error("Key "+outkey+" is not available for your keyboard, skipping")
                        continue
                    cap_unique[ecodes.ecodes[outkey]] = 1

for key in cap_unique.keys():
    cap[ecodes.EV_KEY].append(key)
#pprint.pprint(cap)

# keep trying opening the input device (in case it's intermittent)
while True:
    device = None
    
    try:
        device = InputDevice(conf['input_device'])
        logger.info("Opened "+str(device))
        #create the fake input device by cloning the original device
        ui = UInput(cap, name='antimicro-nonX-fake-input')
        #ui = UInput(name='antimicro-nonX-fake-input')
        logger.info("Created input device "+str(ui.device))
    except Exception as err:
        logger.error(str(err))
        time.sleep(2)
        continue

    # read all events
    for event in device.read_loop():
        logger.debug("Received event "+str(event))
        if event.type == ecodes.EV_KEY:

            # for now, ignore all hold down key events (value = 2)
            # by default react on key press, not release
            value = 1
            if(conf['react_on_release'] == True):
                value = 0

            if(event.value == value):
                # we could react to it
                # see if the key code was mapped to some action
                logger.debug("Checking if "+ str(event.code) + " is mapped")
                
                # skip if not mapped
                key_names = getKeyName(event.code)
                if key_names == None:
                    continue
                
                if type(key_names) == str:
                    #it's just one key. Fake key_names as a list of one
                    key_name = key_names
                    key_names = [key_name]

                for key_name in key_names:
                    if key_name in conf['key_mapping']:
                        logger.info("Handling "+key_name)
                        
                        # handling depends on yaml definition.
                        
                        # Is the value just a string? execute it as a command
                        if type(conf['key_mapping'][key_name]) == str:
                            logger.info(key_name+ " -> " + conf['key_mapping'][key_name] )
                            thread = threading.Thread(target=runBGShell, args=[conf['key_mapping'][key_name]])
                            thread.daemon = True   # Daemonize thread
                            thread.start()         # Start the execution
                        
                        # Is the value an array?
                        if type(conf['key_mapping'][key_name]) == list:

                            # Is the first element a string, or a list?
                            if type(conf['key_mapping'][key_name][0]) == str:
                                # this is a combination of keys that need to be pressed together
                                thread = threading.Thread(target=pressKeys, args=[conf['key_mapping'][key_name]])
                                thread.daemon = True   # Daemonize thread
                                thread.start()         # Start the execution


                            if type(conf['key_mapping'][key_name][0]) == list:
                                # this is a sequence of keys that need to be sent in succession
                                logger.info("Sending keys in succession...")
                                thread = threading.Thread(target=keySequence, args=[conf['key_mapping'][key_name]])
                                thread.daemon = True   # Daemonize thread
                                thread.start()         # Start the execution


                # else the key is silently ignored
