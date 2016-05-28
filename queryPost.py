import urllib.request

"""Run to load the Query Server with some data."""

data1=b'{"rangelist": [[12, 34], [400, 410], [420, 425], [460, 800]], "identifier": "bar"}'
data2=b'{"rangelist": [[12, 34], [37, 440], [460, 800]], "identifier": "foo"}'

with urllib.request.urlopen("http://localhost:8000", timeout=1,data=data1) as conn:
    pass
with urllib.request.urlopen("http://localhost:8000", timeout=1,data=data2) as conn:
    pass
