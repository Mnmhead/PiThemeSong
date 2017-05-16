import re
import subprocess
import time

PLAY_CMD = "omxplayer -o hdmi ../Music/1-13-iwatodai-station.mp3"
NMAP_CMD = "sudo nmap -sP -n 10.0.0.0/24"

WYATT_ANDROID_MAC_ADDR = "ec:1f:72:1a:6a:b5"
ANTONY_ANDROID_MAC_ADDR = "94:65:2d:24:6c:53"

MAC_ADDRS = []
MAC_ADDRS.append(WYATT_ANDROID_MAC_ADDR)
MAC_ADDRS.append(ANTONY_ANDROID_MAC_ADDR)

# statuses
CONNECTED = "connected"
NOT_FOUND = "not found"

# a map from devices to status
STATUS = {}
STATUS[WYATT_ANDROID_MAC_ADDR] = NOT_FOUND
STATUS[ANTONY_ANDROID_MAC_ADDR] = NOT_FOUND

TIME_AWAY = {}
TIME_AWAY[WYATT_ANDROID_MAC_ADDR] = 15*60
TIME_AWAY[ANTONY_ANDROID_MAC_ADDR] = 15*60

def detect():
   playing = False

   while True:
      p = subprocess.Popen( "sudo arp-scan -l", 
                            stdout=subprocess.PIPE,
                            shell=True )
      (arp_output, err) = p.communicate()
      p_status = p.wait()

      # search arp traffic for the MAC addr of each device
      for mac in MAC_ADDRS:
         mac_regex = re.compile( mac )
         match = mac_regex.findall( arp_output )

         prev_status = STATUS[mac]
         # if device was previously connected and it is no longer
         # present in arp traffic, forget the device
         if prev_status == CONNECTED:
            if len(match) == 0:
               # register the device as disconnected
               STATUS[mac] = NOT_FOUND
               TIME_AWAY[mac] = 3
            else:
               TIME_AWAY[mac] = 0

         # If we find a device that was previously not found,
         # play their themesong!
         if prev_status == NOT_FOUND:
            if match:
               # register device as connected
               STATUS[mac] = CONNECTED
               if TIME_AWAY[mac] >= 15*60:
                  player = subprocess.Popen( PLAY_CMD, 
                                          stdout=subprocess.PIPE,
                                          stdin=subprocess.PIPE, 
                                          shell=True)
                  playing = True
                  time.sleep(3*60)
                  playing = False
                  
               TIME_AWAY[mac] = 0
            else:
               TIME_AWAY[mac] = TIME_AWAY[mac] + 3

      # sleep for a brief moment before scanning arp traffic again
      time.sleep(3) 

if __name__ == '__main__':
   detect()
