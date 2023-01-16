# == RepRapFirmware Python RestAPI == written by Rene K. Mueller <spiritdude@gmail.com>
#
# Description:
#  See README.md
#
# History
# 2023/01/15: start coding

import sys, os, re, json, time, datetime
import requests, urllib
import logging

LIBNAME = "RepRapFirmware Python API"
VERSION = "0.0.1"

def req(u,type="GET",params=None,files=None):
   if type=="POST":
      r = requests.post(u,data=params,files=files)
   else:
      r = requests.get(u,params=params)
   if ('content-type' in r.headers and r.headers['content-type']=="application/json") or re.search('^{',r.text):
      # -- inconsistencies: some responses like M409 are text/plain but contain JSON encoded data ...
      d = r.json()
      logging.debug(f"{r.url} {datetime.datetime.now().isoformat()}: JSON: {d}")
      r = d
   else:
      logging.debug(f"{r.url} {datetime.datetime.now().isoformat()}: Text: {json.dumps(r.text)}")
      r = r.text
   return r
   
class RRFRestAPI():
   def __init__(self,host="localhost"):
      self.host = host
      self.url = f"http://{host}"
      self.throttle = 0.5        # -- used for config()
      #req(f"{self.url}/rr_connect")
   def gcode(self,gcode="M122",type="sync",expect=None,force=False):
      r = req(f"{self.url}/rr_gcode",params={"gcode":gcode})
      if type=="sync":
         e = self.reply()
         if expect:
            n = 0
            max_n = 3
            # -- 'expect' may contain a dict key, so we try to get it
            while e==None or e=="" and n<max_n:
            #while ((type(e)==dict and expect not in e) or type(e)!=dict) and n < max_n:
               if n > 0: time.sleep(0.5)
               e = self.reply()
               n += 1
            if n==max_n:
               logging.error(f"too many retries on '{gcode}' getting reply, failed to retrieve '{expect}'")
               if force:
                  e = { }
                  e[expect] = None
         return e
      return r
   def reply(self):
      return req(f"{self.url}/rr_reply")
   def upload(self,fn,dest=""):
      fh = open(fn,"rb")
      d = fh.read()
      if dest=="":
         dest = os.path.basename(fn)
      return req(f"{self.url}/rr_upload?name={urllib.parse.quote(dest)}",type="POST",params=d)
   def download(self,fn):
      return req(f"{self.url}/rr_download",params={"name":fn})
   def delete(self,fn):
      return req(f"{self.url}/rr_delete",params={"name":fn})
   def filelist(self,dir):
      return req(f"{self.url}/rr_filelist",params={"dir":dir})
   def files(self,dir):
      return req(f"{self.url}/rr_files",params={"dir":dir})
   def model(self,key,flags="v"):
      return req(f"{self.url}/rr_model",params={"key":key,"flags":flags})
   def move(self,old,new):
      return req(f"{self.url}/rr_move",params={"old":old,"new":new})
   def mkdir(self,name):
      return req(f"{self.url}/rr_mkdir",params={"name":name})
   def fileinfo(self,fn):
      return req(f"{self.url}/rr_fileinfo",params={"name":fn})
   def print(self,fn):
      return self.gcode(f"M32 \"{fn}\"")
   def print_status(self):
      return self.gcode(f"M27")
   def config(self,key=None):
      #return self.gcode("M115")
      #return self.gcode("M122")
      # -- let's try to be informative (but slow), we query entire model:
      status = { }
      if key==None:
         for key in self.gcode('M409')['result']:
            status[key] = self.gcode(f'M409 K"{key}" F"v"',expect='result')['result']
            # -- throttle a bit, otherwise we flood the controller too much (failed responses, if webgui is also open)
            time.sleep(self.throttle)            
      else:
         status[key] = self.gcode(f'M409 K"{key}" F"v"',expect='result')['result']
      return status
   def status(self):
      return self.config("state")['state']
      
if __name__ == "__main__":
   #logging.basicConfig(level=1)
   
   me = os.path.basename(sys.argv.pop(0))
   
   if len(sys.argv)!=1:
      print(f"USAGE: {me} <IP/hostname>")
      sys.exit(1)

   rrf = RRFRestAPI(sys.argv.pop(0))
   
   print(rrf.gcode())
   
   #print(rrf.filelist("/"))
   #print(rrf.files("/"))
   print(rrf.files("/sys"))
   print(rrf.files("/gcodes"))
   print(rrf.files("/jobs"))
   print(rrf.download("/sys/config.g"))

   print(rrf.upload("tests/test.txt",dest="/sys/test.txt"))
   print(rrf.download("/sys/test.txt"))
   print(rrf.delete("/sys/test.txt"))

   print(json.dumps(rrf.config(),indent=3))
   print(json.dumps(rrf.config('volumes'),indent=3))

   print(json.dumps(rrf.status(),indent=3))

   print(rrf.upload("tests/test.gcode",dest="/gcodes/test.gcode"))
   print(rrf.print("/gcodes/test.gcode"))
   print("status:",rrf.print_status())
   
