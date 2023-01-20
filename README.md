# RepRapFirmware Python API 

NOTE: THIS IS EARLY STATE OF PACKAGE - API SUBJECT OF CHANGES UNTIL 0.1.0 RELEASE

## Install

```
git clone https://github.com/Spiritdude/RepRapFirmwarePyAPI
cd RepRapFirmwarePyAPI
pip3 install .
```

## Introduction

Just a small wrapper to interact with a RepRapFirmware-based controller via HTTP/RestAPI:
```
import RepRapFirmwareAPI

rrf = RepRapFirmwareAPI.RRFRestAPI("192.168.0.12")

resp = rrf.gcode("M122")              # synchronous
# Note: type(resp) is either dict containing data, or str 

rrf.gcode("M122","async")             # asynchronous
resp = rrf.reply()

rrf.upload("test.gcode","/gcodes/test.gcode")
rrf.print("/gcodes/test.gcode")
rrf.print_status()
```

test it with (replace IP with your actual board):
```
python3 src/RepRapFirmwareAPI/__init__.py 192.168.0.12
```
it will produce a lot of output, as first `M122`, and then 
- retrieve full configuration (takes a couple of seconds), and then
- upload a test file (`tests/test.txt`), downloads its content, and delete again, and then
- upload `tests/test.gcode` .gcode file (single line) and starts printing it

## Methods

Note: All methods return either `dict` or `str` as data types.

### gcode
`gcode(gcode="M122",typ="sync",expect=None,force=False)`
> send single G-code line
  - `typ`: `"sync"` or `"async"` then use `reply()` to retrieve response
  - `expect`: string of a key you expect as part of dict response
  - `force`: enforce 'expect' key to be present in case of error, then it's `None`
> examples:
>> gcode("G28 X Y")
>> gcode("M122")

### reply
`reply(typ="sync")`
> if `gcode("...",typ="async")` was used, retrieve response separately, optionally the `reply("async")` returns non-blocking

### upload
`upload(fn,dest="")`
> upload file, for print jobs choose "/gcodes/" as folder, e.g. `upload("test.gcode","/gcodes/test.gcode")`

### print
`print(fn)`
> print uploaded file, e.g. `print("/gcodes/test.gcode")`

### print_status
`print_status()`
> retrieve printing status

### download
`download(fn)`
> download file, e.g. `download("/sys/config.g")`

### delete
`delete(fn)`
> delete file, e.g. `delete('/gcodes/test.gcode')`

### filelist
`filelist(dir)`
> detailed list of files of a directory

### files
`files(dir)`
> just the names of the files of a directory

### move
`move(old,new)`
> move/rename a file

### mkdir
`mkdir(name)`
> make a new directory

### fileinfo
`fileinfo(fn)`
> retrieve detailed information of a file (e.g. a gcode file)

### model
`model(key,flags="v")`
> retrieve low-level query of configuration

### config
`config(key=None)`
> retrieve comprehensive configuration (takes time to gather)
> if `key` is present, only a particular configuration is retrieved

### status
`status()`
> same as `config('state')`

## Caution
If you have the Web Console open with a browser, using this API can mix up responses to browser or this API.
Therefore best close any browser and only use this API layer to have reliable operations.

