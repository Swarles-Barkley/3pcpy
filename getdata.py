from __future__ import division
from __future__ import print_function
import sys
import re
trial_files = sys.argv[1:]
success = 0
failure = 0
time = 0.0
sent = 0
recv = 0

def extract(filename, s, pattern):
    m = re.search(pattern, s)
    if not m:
        print("warning: pattern not found in %s: %s" % (filename, pattern), file=sys.stderr)
        return "0"

    return m.group(1)

for filename in trial_files:
    with open(filename) as f:
        data = f.read()
    if 'success' in data:
        success += 1
    else:
        #assert 'aborted' in data or 'commit failed' in data
        failure += 1
    seconds = float(extract(filename, data, "took (.*) seconds"))
    time += seconds

    sent += int(extract(filename, data, r"\[server 0\] sent (.*) bytes"))
    recv += int(extract(filename, data, r"\[server 0\] received (.*) bytes"))

n = success+failure
#print ("success rate: {}".format(success / n))
#print ("average time: {}".format(time / n))
#print ("average sent: {}".format(sent / n))
#print ("average recv: {}".format(recv / n))

print("{},{},{},{}".format(success / n, time/n, sent/n, recv/n))


