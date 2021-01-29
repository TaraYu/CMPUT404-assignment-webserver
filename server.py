#  coding: utf-8 
import socketserver,os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        #Receive data from the client, 1024 bytes each time


        request_data = self.data.decode('utf-8')
        request_array = request_data.split('\r\n')[0]
        #print(request_data)
        request_method = request_data.split()[0]
        request_URI = request_data.split()[1]
 

        if request_method != 'GET':
            self.handle405status()
            return
        #check the ending and make sure there is not end with a file name in this situation
        elif request_URI[-1] != '/' and '.' not in request_URI.split('/')[-1]:
            self.handle301status(request_URI)
            return
        else:
            #surport css
            if 'css' in request_URI:
                MIMA_type = 'text/css'
            #surport html
            elif 'html' in request_URI:
                MIMA_type = 'text/html'
            #end with '/' and there is no filaname, correct it.
            #eg: http://127.0.0.1:8080/deep/ -->http://127.0.0.1:8080/deep/index.html
            elif request_URI[-1] == '/':
                request_URI += 'index.html'
                MIMA_type = 'text/html'
            else:
                self.handle404status()
                return


            filepath = 'www' + request_URI
            print(filepath)
            #check whether file exist:
            #https://stackoverflow.com/questions/82831/how-do-i-check-whether-a-file-exists-without-exceptions
            if os.path.exists(filepath):
                f = open(filepath, 'r')
                thedata = '\r\n\r\n'+f.read()
                print(thedata)
                f.close()
                self.sendResponse(MIMA_type, thedata)
                return
            else:
                self.handle404status()
                return
    
    
    #deal with string with encode():
    #https://stackoverflow.com/questions/9942594/unicodeencodeerror-ascii-codec-cant-encode-character-u-xa0-in-position-20

    def handle404status(self):
        response = "HTTP/1.1 404 Not Found\r\n404 Not Found"
        self.request.sendall(response.encode())

    def handle405status(self):
        response = "HTTP/1.1 405 Method Not Allowed\r\n405 Method Not Allowed"
        self.request.sendall(response.encode())

    def handle301status(self, request_URI):
        response = "HTTP/1.1 301 Moved Permanently\r\n"+ "Location:"+ request_URI+"/\r\n"
        self.request.sendall(response.encode())

    def sendResponse(self, MIMA_type, thedata):
        response = 'HTTP/1.1 200 OK\r\n'+ 'Content-type: '+ MIMA_type +'\r\n' + thedata
        self.request.sendall(response.encode())


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()