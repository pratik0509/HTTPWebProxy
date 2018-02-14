import os
import time
import datetime
import SocketServer
import SimpleHTTPServer

PORT = 20000

class HTTPCacheRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def send_head(self):
        if self.command != "POST" and self.headers.get('If-Modified-Since', None):
            print 'send'
            print self.path
            filename = self.path.strip("/")
            if os.path.isfile(filename):
                a = time.gmtime(os.path.getmtime(filename))
                b = time.strptime(self.headers.get('If-Modified-Since', None), "%a, %d %b %Y %H:%M:%S %Z")
                if a < b:
                    print "---------------->"
                    print "Sending 304 because already cached"
                    self.send_response(304)
                    self.end_headers()
                    return None
                else:
                    print "------------------->"
                    print "Resending 200"
        return SimpleHTTPServer.SimpleHTTPRequestHandler.send_head(self)

    def end_headers(self):
        filename = self.path.strip("/")
        print filename
        if filename == "2.binary":
            self.send_header('Cache-control', 'no-cache')
        else:
            self.send_header('Cache-control', 'must-revalidate')
        SimpleHTTPServer.SimpleHTTPRequestHandler.end_headers(self)

s = SocketServer.ThreadingTCPServer(("", PORT), HTTPCacheRequestHandler)
s.allow_reuse_address = True
print "Serving on port", PORT
s.serve_forever()
