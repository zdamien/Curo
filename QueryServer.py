from Query import QueryEngine, QueryObject, Range
import http.server
import urllib.parse
import json

class QueryHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        print(self.path) #DEBUGGING
        # /?identifier=foo&left=10&right=15
        parse = urllib.parse.urlparse(self.path)
        querydict=urllib.parse.parse_qs(parse.query)
        # {'left': ['10'], 'right': ['15'], 'identifier': ['foo']}
        print(querydict) #DEBUGGING
        r = Range(int(querydict['left'][0]),int(querydict['right'][0]))
        print(r) #DEBUGGING
        resp = qe.retrieve(r)
        print(resp) #DEBUGGING
        self.wfile.write(bytes(resp, 'ASCII'))

    def do_POST(self):
        print("req ", self.requestline) #DEBUGGING
        print("path ",self.path) #DEBUGGING
        print("command ",self.command) #DEBUGGING
        print(self.headers) #DEBUGGING
        leng = int(self.headers["Content-Length"])
        print ("mess len is ", leng) #DEBUGGING
        print(self.close_connection) #DEBUGGING
        print('---') #DEBUGGING

        line = self.rfile.read(leng)
        self.send_response_only(202)
        self.end_headers()
        line = str(line,'utf-8')
        print(line) #DEBUGGING
        d = json.loads(line)
        print(d) #DEBUGGING
        qe.store(QueryObject.fromlist(d['identifier'],d['rangelist']))
        
def run(server_class=http.server.HTTPServer, handler_class=QueryHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()
            
qe = QueryEngine()
run()
