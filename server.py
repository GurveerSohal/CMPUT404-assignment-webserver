#  coding: utf-8 
import socketserver
import os
import mimetypes

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Copyright 2023 Gurveer Singh Sohal
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
        lines = self.data.decode().split('\r\n')
        method, path, protocol = lines[0].split()

        if method == "GET":
            self.handleGET(path)
        else:
            self.handleOthers(path)

    def handleOthers(self, path):
            status = "HTTP/1.1 405 Method Not Allowed"
            response = [
                status,
                f"Allow:\tGET",
                ""
            ]


            response = "\r\n".join(response)
            response += "\r\n"

            self.request.sendall(response.encode("utf-8"))

            return

    def handleGET(self, path):
        # print("Handling get for path: ", path)
        statusCode, response = self.handlePath(path)


        self.request.sendall(response.encode("utf-8"))
        
        return

    def handlePath(self, path):
        path = f"./www{path}"
        abspath = os.path.abspath(path)
        curdir = os.path.abspath("./www/")

        if (abspath.find(curdir) == -1) or (not os.path.exists(path)):
            status = "HTTP/1.1 404 Not Found!"

            response = [
                status
            ]

            response = "\r\n".join(response)
            response += "\r\n"

            return 404, response

        if os.path.isdir(path):
            if path[-1] != '/':
                # send 301 status
                status = "HTTP/1.1 301 Moved Permanently"
                location = path[5:] + '/'
                response = [
                    status,
                    f"Location:\t{location}",
                    ""
                ]


                response = "\r\n".join(response)
                response += "\r\n"

                return 301, response

            path += "index.html"

        if os.path.isfile(path):
            status = "HTTP/1.1 200 OK"
            contentType, encoding = mimetypes.guess_type(path)
            body = ""
            with open(path, "r") as f:
                body = f.read()
            contentLength = str(len(body))

            # print("contentType: ", contentType)
            # print("contentLength: ", contentLength)
            # print("body: ", body)

            response = [
                status,
                f"Content-Type:\t{contentType}",
                f"Content-Length:\t{contentLength}",
                "",
                body
            ]

            response = "\r\n".join(response)
            response += "\r\n"
            return 200, response
        else:
            raise RuntimeError("It's not supposed to reach this else statement")

            return





if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
