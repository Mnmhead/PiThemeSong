# Copyright Gyorgy Wyatt Muntean 2018
#
# This program takes in a file which serves as a map of MAC addresses
# to file paths of Mp3s.  This program then monitors the nextwork using ARP
# to determine when it is appropriate to play each device's themesong.
#
# The filename is hardcoded into this program, maybe later I can improve that.

import re, sys
import subprocess, shlex
import time


def parseFile( filename ):
   # If the file gets abnormally large, then this is pretty gross
   # because we hold the entire file in memory
   lines = [ line.strip( '\n' ) for line in open( filename ) ]
   if( len( lines ) % 2 == 1 ):
      print "Improper macs.txt format"
      sys.exit( 1 ) 

   # convert the list into a dictionary such that even indexes are keys
   # and odd indexes are values
   macMap = {}
   macMap = dict( zip( lines[::2], lines[1::2] ) )
   return macMap 

class DeviceStatus( object ):
   # static Class variables
   connected = "connected"
   notFound = "not found"
  
   def __init__( self, filepath ):
      self.status = DeviceStatus.notFound
      self.timeAway = 60 * 10 + 1  # TODO: this is arbitrary
      self.filepath = filepath


#------initial setup should be in a class or some shit---------#
# state variables
connected_ = "connected"
notFound_ = "not found"

# parse the file to get a mapping of MAC addresses to filepaths of songs
macAddrFile = 'macs.txt'
macAddrMap = parseFile( macAddrFile )

playCmd = "/usr/bin/omxplayer --no-keys -o hdmi"
arpCmd = "sudo arp-scan -l"

macStatus = {}
for mac, filepath in macAddrMap.iteritems():
   macStatus[ mac ] = DeviceStatus( filepath )
#--------------------------------------------------------------#


def log( msg ):
   f = open( "/var/log/themesong.log", "a+" )
   f.write( msg )
   f.close()

def detect():
   while True:
      p = subprocess.Popen( shlex.split( arpCmd ), 
                            stdout=subprocess.PIPE )
      ( arpOutput, err ) = p.communicate()
      pStatus = p.wait()

      # search arp traffic for the MAC addr of each device
      for mac, _ in macStatus.iteritems():
         log( "iterating...mac" )
         macRegex = re.compile( mac )
         match = macRegex.findall( arpOutput )
           
         devStatus = macStatus[ mac ]

         # if device was previously connected and it is no longer
         # present in arp traffic, forget the device
         if( devStatus.status == DeviceStatus.connected ):
            log( "Device is connected: " + mac + ", prev status: " + devStatus.status )

            if( len( match ) ):
               # MAC addr is appearing on the network, set timeAway to now
               devStatus.timeAway = 0
            else:
               # No match, register the device as disconnected
               devStatus.status = DeviceStatus.notFound
               devStatus.timeAway = 3

         # If we find a device that was previously not found,
         # play its themesong!
         elif( devStatus.status == DeviceStatus.notFound ):
            log( "non connected: " + mac )
            if match:
               # register device as connected
               macStatus[ mac ].status = DeviceStatus.connected

               if( devStatus.timeAway >= 60 * 10 ):
                  playSongCmd = playCmd + ' ' + devStatus.filepath
                  player = subprocess.Popen( shlex.split( playSongCmd ),
                                             stdout=subprocess.PIPE,
                                             stdin=subprocess.PIPE )
                  # TODO: sleep until the song is over...which could be more than 3min
                  time.sleep( 3 * 60 )
                  
               devStatus.timeAway = 0
               log( "Finished waiting for song to end: " mac )

            else:
               log( "Mac addr not present and no match on recent arpScan: " + mac )
               devStatus.timeAway += 3

         else:
            log( "Unrecognized device status" )
            sys.exit( 1 )

      # sleep for a brief moment before scanning arp traffic again
      time.sleep(3) 


if __name__ == '__main__':
   detect()
