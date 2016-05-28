import http.server
import urllib.parse
import doctest

"""
Read instructions 15:26
picked problem 3 15:50
coded Range and QueryObject and more 17:09
realized QueryObject.overlap() was wrong 17:15
fixed and tested by 17:55
QueryEngine by 18:35
"""

class Range:
    """Range or interval objects.  Data is simply left and right, at
    least for now, inclusive.  Key thing is the overlap method, which
    computes the overlap, if any, between two ranges."""

    def __init__(self, left, right):
        self.left = left
        self.right = right
    def overlap(self, qrange):
        """Method for determining amount of overlap between two
        intervals.  I suspect this could be more concise, but under
        time pressure I'd rather be correct (even if simple and dumb)
        than chase cleverness that I might not find.

        [1,4], [5,8] = 0
        [1,6], [5,8] = 1
        [1,9], [5,8] = 3

        [9,10], [5,8] = 0

        [6,7], [5,8] = 1
        [6,9], [5,8] = 2

        [5,6], [5,8] = 1
        [6,8], [5,8] = 2

        """
        overlap = 0
        if self.left < qrange.left:
            if self.right < qrange.left:
                return 0
            elif self.right < qrange.right:
                overlap += self.right - qrange.left
            else:
                overlap += qrange.right - qrange.left
        elif self.left > qrange.right:
            return 0
        # qrange.left < self.left < qrange.right
        elif self.right < qrange.right:
            overlap += self.right - self.left
        else:
            overlap += qrange.right - self.left
        return overlap

    def _test(toprint=False):
        """Incporates the tests in the docstring for overlap()
        Normally I'd use the doctest module but that seemed less easy
        for some reason.
            
        _test(True) prints the test results.
        function returns True if all tests passed.
>>> Range._test()
True
        """
        passed = True
        qr = Range(5,8)
        sranges = [Range(1,4), Range(1,6), Range(1,9), Range(9,10),
            Range(6,7), Range(6,9), Range(5,6), Range(6,8)]
        results = [0,1,3,0,1,2,1,2]
        for i,r in enumerate(sranges):
            if toprint: print(r.overlap(qr), results[i])
            passed &= r.overlap(qr) == results[i]
        return passed
#    def __str__(self):
#        return str([self.left,self.right])
    def __repr__(self):
        """
>>> r=Range(3,4)
>>> repr(r)
'[3, 4]'
"""
        return str([self.left,self.right])

class QueryObject:
    def __init__(self, iden, rangelist):
        self.iden = iden
        self.rangelist = rangelist

    def __repr__(self):
        """
>>> print(QueryObject("foo",Range(3,5)))
"foo":[3, 5]
"""
        return '"'+self.iden + '":'+str(self.rangelist)

    def newoverlap(self,qrange):
        """Takes a Range object. Returns list of tuples of (self range
        that overlaps qrange, quantity of overlap)"""
        retvalues = []
        for r in self.rangelist:
            overlap = r.overlap(qrange)
            if overlap > 0:
                retvalues.append((r, overlap))
        return retvalues

    def overlap(self,qrange, retranges=False):
        """Expects a Range object as parameter.  Will sum up the overlap
        between qrange and each object range."""
        """ ERROR: after a couple hours work, I realized this isn't what
        we want."""
        totaloverlap = 0
        if retranges:
            ranges = []
        for r in self.rangelist:
            overlap = r.overlap(qrange)
            totaloverlap += overlap
            if overlap > 0 and retranges:
                ranges.append(r)
        if retranges:
            return totaloverlap, ranges
        else:
            return totaloverlap

    def _newovertest():
        """tests return of overlapping ranges
>>> QueryObject._newovertest()
[460, 800] 4
[37, 440] 5
[460, 800] 5
[12, 34] 22
[37, 440] 403
[460, 800] 340
"""
        testranges = [Range(450,464), Range(435,465), Range(0,800)]
        results = [4, 10, 34-12 + 440-37 + 800-460]
        qo = QueryObject("foo", [Range(12,34), Range(37,440), Range(460,800)])
        for i,r in enumerate(testranges):
            retlist = qo.newoverlap(r)
            for ret in retlist:
                print(ret[0], ret[1])


    def _test(toprint=False):
        """See Range._test
>>> QueryObject._test()
True
"""

        passed = True
        testranges = [Range(450,464), Range(435,465), Range(0,800)]
        results = [4, 10, 34-12 + 440-37 + 800-460]
        #q = QueryObject("foo", [[12,34],[37,440],[460,800]])
        qo = QueryObject("foo", [Range(12,34), Range(37,440), Range(460,800)])
        for i,r in enumerate(testranges):
            if toprint: print(qo.overlap(r), results[i], r)
            passed &= qo.overlap(r) == results[i]
        return passed

    def _test2(toprint=False):
        """tests return of overlapping ranges
>>> QueryObject._test2()
4 ['[460, 800]']
10 ['[37, 440]', '[460, 800]']
765 ['[12, 34]', '[37, 440]', '[460, 800]']
"""
        testranges = [Range(450,464), Range(435,465), Range(0,800)]
        results = [4, 10, 34-12 + 440-37 + 800-460]
        qo = QueryObject("foo", [Range(12,34), Range(37,440), Range(460,800)])
        for i,r in enumerate(testranges):
            overlap, retranges = qo.overlap(r,True)
            print(overlap, [str(r) for r in retranges])


class IntervalContainer:
    """ interval tree of centered intervals would be faster """
    def __init__(self):
        self._intervals={}        

    def add(self, r, obj):
        self._intervals[r] = obj

    def query(self, p):
        """ p is a point, not a range
>>> i = IntervalContainer()
>>> o1 = QueryObject("foo", Range(3,5))
>>> i.add(Range(3,5), o1)
>>> i.query(0)
set()
>>> i.query(4)
{"foo":[3, 5]}
>>> i.query(5)
{"foo":[3, 5]}
>>> i.query(6)
set()
        """
        lo = set()
        for i,o in self._intervals.items():
            if i.left <= p <= i.right:
                lo.add(o)
        return lo
        

class QueryEngine:
    def __init__(self):
        #store each object in a dictionary by name
        self.objects = dict()
        #store each range as a key, with the associated object as value
        self.intervals = IntervalContainer()

    def store(self, obj):
        self.objects[ obj.iden ] = obj
        for r in obj.rangelist:
            self.intervals.add(r, obj)

    def retrieve(self, qrange):
        """
>>> qe = QueryEngine()
>>> qe.store(QueryObject("foo",[Range(12,34), Range(37,440), Range(460,800)]))
>>> qe.retrieve(Range(450,464))
[{"identifier":"foo","ranges":[460, 800]"intersection":4}]
"""
        objects = self.intervals.query(qrange.left) #set
        objects.update( self.intervals.query(qrange.right) )
        lobjects = list(objects)
        lobjects.sort(key = lambda o: o.iden)
        response = "["
        for obj in lobjects:
            retlist = obj.newoverlap(qrange)
            for r in retlist:
                response += '{"identifier":"'+obj.iden+'","ranges":'+ str(r[0])+ '"intersection":'+ str(r[1])+ '}'
        response += ']'
        print(response)


#  Finally, the actual network stuff

class QueryHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        print(self.path)
        parse = urllib.parse.urlparse(self.path)
        querydict=urllib.parse.parse_qs(parse.query)
        print(querydict)
        #self.wfile.write(bytes(str(querydict), 'utf-8'))
        resp = qe.retrieve(Range(int(querydict['left'][0]),int(querydict['right'][0])))
        print(resp)
        self.wfile.write(bytes(resp, 'utf-8'))

    def do_POST(self):
        line = self.wfile.readline()
        line = str(line,'utf-8')
        d = json.loads(line)
        qe.store(QueryObject(d['identifier'],d['rangelist']))
        


def run(server_class=http.server.HTTPServer, handler_class=QueryHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()
            


if __name__ == "__main__":
    doctest.testmod()
    qe = QueryEngine()
    run()
