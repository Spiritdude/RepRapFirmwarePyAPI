# == RepRapFirmware Python RestAPI == written by Rene K. Mueller <spiritdude@gmail.com>
#
# Description:
#  See README.md
#
# History:
# 2023/01/20: 0.0.3: using sessions to increase reliability
# 2023/01/16: 0.0.2: published, not yet as stable as wanted, but working somewhat
# 2023/01/15: 0.0.1: barefy functional
# 2023/01/15: start coding

import sys, os, re, json, time, datetime
import requests, urllib
import logging

LIBNAME = "RepRapFirmware Python API"
VERSION = "0.0.3"

class RRFRestAPI():
   req = requests.Session()
   req.verify = True
   def _req(self,u,type="GET",params=None,files=None):
      if type=="POST":
         r = self.req.post(u,data=params,files=files)
      else:
         r = self.req.get(u,params=params)
      if ('content-type' in r.headers and r.headers['content-type']=="application/json") or re.search('^{',r.text):
         # -- inconsistencies: some responses like M409 are text/plain but contain JSON encoded data ...
         d = r.json()
         logging.debug(f"{r.url} {datetime.datetime.now().isoformat()}: JSON: {d}")
         r = d
      else:
         logging.debug(f"{r.url} {datetime.datetime.now().isoformat()}: Text: {json.dumps(r.text)}")
         r = r.text
      return r
   
   def __init__(self,host="localhost",password=None):
      self.host = host
      self.url = f"http://{host}"
      self.throttle = 1/5        # -- [s] used for config(), use fraction of 1/n
      self.password = password
      #_req(f"{self.url}/rr_connect")

   def gcode(self,gcode="M122",typ="sync",expect=None,force=False):
      r = self._req(f"{self.url}/rr_gcode",params={"gcode":gcode})
      if typ=="sync":
         e = self.reply(typ="sync",timeout=1.0)
         if len(e)==0:
            logging.error(f"timeout on '{gcode}' getting reply"+(f", failed to retrieve '{expect}'" if expect else ""))
            if force:
               e = { }
               e[expect] = None
         return e
      return r

   def reply(self,typ="async",timeout=60):      # -- our default is async, get a reply even if command isn't finished yet
      if typ=="sync":                           # -- expect something for sure (within reason)
         st = time.time()
         n = 0
         while time.time()-st < timeout:        # -- consider timeout
            e = self._req(f"{self.url}/rr_reply")
            if type(e)==str:
               if len(e)>0:
                  break
            elif type(e)==dict:
               break
            time.sleep(self.throttle)
            n += 1
         return e
      else:
         return self._req(f"{self.url}/rr_reply")     # -- may return something or nothing

   def upload(self,fn,dest=""):
      fh = open(fn,"rb")
      d = fh.read()
      if dest=="":
         dest = os.path.basename(fn)
      return self._req(f"{self.url}/rr_upload?name={urllib.parse.quote(dest)}",type="POST",params=d)

   def download(self,fn):
      return self._req(f"{self.url}/rr_download",params={"name":fn})

   def delete(self,fn):
      return self._req(f"{self.url}/rr_delete",params={"name":fn})

   def filelist(self,dir):
      return self._req(f"{self.url}/rr_filelist",params={"dir":dir})

   def files(self,dir):
      return self._req(f"{self.url}/rr_files",params={"dir":dir})

   def model(self,key,flags="v"):
      return self._req(f"{self.url}/rr_model",params={"key":key,"flags":flags})

   def move(self,old,new):
      return self._req(f"{self.url}/rr_move",params={"old":old,"new":new})

   def mkdir(self,name):
      return self._req(f"{self.url}/rr_mkdir",params={"name":name})

   def fileinfo(self,fn):
      return self._req(f"{self.url}/rr_fileinfo",params={"name":fn})

   def print(self,fn):
      return self.gcode(f"M32 \"{fn}\"")

   def print_status(self):
      return self.gcode(f"M27")

   def config(self,key=None):
      status = { }
      if key==None:
         # -- let's try to be informative (but slow), we query entire model:
         for key in self.gcode('M409',expect='result')['result']:
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
   
