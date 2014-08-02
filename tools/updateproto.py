'''
Created on Aug 2, 2014

@author: Chris
'''
import sys, os, subprocess, shutil
import fileinput

if len(sys.argv) <= 2:
    print "usage: updateproto.py client.dll outputfolder"
    sys.exit(-1)
    
client_location = sys.argv[1]
output = sys.argv[2]

shutil.rmtree("./proto/")
os.mkdir("./proto/")

subprocess.call(["ProtobufDumper.exe", client_location, "./proto/"])

#cheaply patch netmessages.proto
for line in fileinput.FileInput("./proto/netmessages.proto", inplace=1):
    if "MSG_SPLITSCREEN_TYPE_BITS" in line:
        print line.replace("1", "2"),
    else:
        print line,

for root, subFolders, files in os.walk("./proto/"):
    for filename in files:
        file_combined = os.path.join(root, filename)
        print "Copied %s to %s" % (filename, output)
        subprocess.call(["protoc", "--proto_path=./proto/", "--proto_path=C:\protobuf-2.5.0\src", "--python_out=%s" % output, file_combined])
        
if not os.path.exists(os.path.join(output, "__init__.py")):
    open(os.path.join(output, "__init__.py"), 'w')