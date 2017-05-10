import subprocess
import time

PLAY_CMD = "omxplayer -o hdmi ../Music/1-13-iwatodai-station.mp3"

#WYATT_ANDROID_MAC_ADDR = "ec:1f:72:1a:6a:b5"
ANTONY_ANDROID_MAC_ADDR = "94:65:2d:24:6c:53"

# statuses
CONNECTED = "connected"
NOT_FOUND = "not found"

# a map from devices to status
STATUS = {}

def detect():
   playing = False

   while True:
      time.sleep(1)
      mac_regex = "\'" + ANTONY_ANDROID_MAC_ADDR + "\'"#+ "|" + WYATT_ANDROID_MAC_ADDR + "\'"
      p = subprocess.Popen( "sudo arp-scan -l | grep -E " + mac_regex, 
                            stdout=subprocess.PIPE,
                            shell=True )
      (output, err) = p.communicate()
      p_status = p.wait()
      if output and not playing:
         print( "Found a device!" )
         player = subprocess.Popen( PLAY_CMD, 
                                    stdout=subprocess.PIPE,
                                    stdin=subprocess.PIPE, 
                                    shell=True)
         playing = True
         time.sleep(3*60)
         playing = False
         #player.stdin.write("^C")
      else:
         print( "No op, no new device found" )

if __name__ == '__main__':
   detect()
