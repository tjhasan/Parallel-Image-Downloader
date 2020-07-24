import urllib.request
from glob import iglob
import shutil
import os
import sys
import threading
import time

url = sys.argv[1] #gets the arguments
parts = int(sys.argv[2])

d = g = urllib.request.urlopen(url) #gets the length of bits the file is
length = int(d.getheader('Content-Length'))

name = url[::-1] #gets the name of the file
name = name.split("/",1)[0]
name = name[::-1]

lastSegLength = 0
segLength = length/parts #divides up the length of the url content into parts
segLength = int(segLength)

if length%parts != 0: #if the length of the content doesn't divide evenly, then I add the remainder to a separate variable
    lastSegLength = lastSegLength + length % parts

filenames = [] #going to use this list to keep track of all the filenames
def download_image(currPart, i, filenames):
    if i == 1: #depending on the current thread count, a different portion of the image is downloaded
        headers = {'Range': 'bytes=' + str(0) + '-' + str(segLength)}
        req = urllib.request.Request(url, headers=headers)
        g = urllib.request.urlopen(req)
        with open(currPart, 'b+w') as f:
            f.write(g.read())
    elif i is parts:
        headers = {'Range': 'bytes=' + str((i-1) * segLength + 1) + '-' + str(i * segLength + lastSegLength)}
        req = urllib.request.Request(url, headers=headers)
        g = urllib.request.urlopen(req)
        with open(currPart, 'b+w') as f:
            f.write(g.read())
    else:
        headers = {'Range': 'bytes=' + str((i-1) * segLength+1) + '-' + str(i * segLength)}
        req = urllib.request.Request(url, headers=headers)
        g = urllib.request.urlopen(req)
        with open(currPart, 'b+w') as f:
            f.write(g.read())
    filenames.append(currPart) #adds to the list of files created

threads = []
for i in range(1, parts+1): #this loop will create a new thread until it hits the desired number of TCP connections
    currPart = 'part_' + str(i)
    tName = 't' + str(i)
    tName = threading.Thread(target=download_image, args=(currPart, i, filenames,))
    threads.append(tName)
    tName.start()
    time.sleep(.1) #need to slow the program down in order to prevent the threads from overlapping the image

for thread in threads:
    thread.join()
    time.sleep(.1) #need to slow the program down in order to prevent the threads from overlapping the image

destination = open(name, 'ab')
for i in filenames: #appends all of the files created together and puts it into a new file with the appropriate name
    for filename in iglob(os.path.join('./', i)):
        shutil.copyfileobj(open(filename, 'rb'), destination)
destination.close()
