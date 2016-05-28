import doctest

"""
Read instructions 15:26, did some HTTP and interval research
picked problem 3 15:50
coded Range and QueryObject and more 17:09
realized QueryObject.overlap() was wrong 17:15
fixed and tested newoverlap() by 17:55
QueryEngine by 18:35
 mix of networking and dinner
21:15: POST submits data, GET returns correct value
 but POST doesn't finish without a manual interrupt

 Blockage: my post function in queryPost doesn't return.

 21:50: almost done except for the networking problem.  can kill postQuery and run different versions to get multiple data in, and get correct results back.
 22:25 postQuery stops hanging, using Content-Length for read, but
 throws exceptions insead.
 22:35 finally found send_response and end_headers in http.server, which
 makes the client close happily.
 23:10  Further comments and some cleanup.
"""

"""Classes:  Possibly too many.  Helps for testing and type-checking,
though.  Usually I think of pure functions more than objects, I dunno what
came over me.

Range: a simple interval, plus overlap() for calculating overlap with a
given range

OverlapObject: identifier, a single range, and calculated overlap, plus
method to print all that nicely (which is the reason I made it.)

QueryObject: identifier and list of ranges
 newoverlap() returns a list of (range, ovelap) tuples  in response to a query
 range, giving the object's ranges that overlap with the query.
 The other overlap() and _test methods are from an earlier
 misunderstanding of the problem description.  I leave them as evidence
 of what I was up to.

IntervalContainer: contains each range, and the object it belongs to.
Currently query() does a linear search for intervals that contain a
point.  An tree would be faster but I'm so past time and tired.

QueryEngine: the top level class, that network code talks to.  Contains
dictionary of (identifier: objects) because that seemed natural, though
it never comes up here.
"""

class Range:
    """Range or interval objects.  Data is simply left and right, at
    least for now, inclusive.  Key thing is the overlap method, which
    computes the overlap, if any, between two ranges."""

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def fromlist(l):
        return Range(l[0],l[1])

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

class OverlapObject:
    def __init__(self, iden, rang, over):
        self._iden = iden
        self._range = rang
        self._overlap = over
    def __repr__(self):
        return '{"identifier":"'+self._iden+'","ranges":'+ str(self._range)+ ',"intersection":'+ str(self._overlap)+ '}'

    
class QueryObject:
    def __init__(self, iden, rangelist):
        """ rangelist should be a list of Range objects
>>> QueryObject("foo",[Range(3,4),Range(5,7)])
"foo":[[3, 4], [5, 7]]
        """
        self.iden = iden
        self.rangelist = rangelist

    def fromlist(iden, rangelist):
        """this takes a list of lists, like [[3,4]]
>>> QueryObject("foo",[Range(3,4),Range(5,7)])
"foo":[[3, 4], [5, 7]]
>>> QueryObject.fromlist("foo",[[3,4]])
"foo":[[3, 4]]
        """
        rl = []
        for r in rangelist:
            rl.append(Range.fromlist(r))
        return QueryObject(iden, rl)

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
'[{"identifier":"foo","ranges":[460, 800]"intersection":4}]'
"""
        objects = self.intervals.query(qrange.left) #set
        objects.update( self.intervals.query(qrange.right) )
        lobjects = list(objects)
        lobjects.sort(key = lambda o: o.iden)
        lov = []
        for obj in lobjects:
            retlist = obj.newoverlap(qrange)
            for r in retlist:
                ov = OverlapObject(obj.iden, r[0], r[1])
                lov.append(ov)
        return str(lov)


if __name__ == "__main__":
    doctest.testmod()
