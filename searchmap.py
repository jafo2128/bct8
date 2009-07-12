from optparse import OptionParser
import MySQLdb
import simplejson as json
import sys

config = {}
for k, v in json.load(file('/home/synack/src/bct8/db.conf', 'r')).items():
    config[str(k)] = str(v)

# Mission Bay
#bounds = (37.75979065676543, -122.4067497253418, 37.78357051884507, -122.37331867218016)

# San Francisco
bounds = (37.71926926474386, -122.50047683715822, 37.81439492742204, -122.3667526245117)

db = MySQLdb.connect(**config)
cur = db.cursor()

parser = OptionParser()
parser.add_option('-f', '--frequency', dest='frequency', default=None)
parser.add_option('-c', '--callsign', dest='callsign', default=None)
parser.add_option('-p', '--power', dest='power', default=None)
parser.add_option('-o', '--owner', dest='owner', default=None)
parser.add_option('-e', '--export', dest='export', default=None)
parser.add_option('-z', '--zerofill', dest='zerofill', action='store_true', default=False)

options, args = parser.parse_args()
queryargs = []

query = 'SELECT frequencies.callsign,frequencies.power,frequencies.erp,frequencies.frequency,entities.owner FROM frequencies, entities, locations WHERE '
if options.frequency:
    query += 'frequencies.frequency=%s AND '
    queryargs.append(options.frequency)
if options.callsign:
    query += 'frequencies.callsign=%s AND '
    queryargs.append(options.callsign)
if not options.callsign:
    query += 'locations.latitude > %s AND locations.longitude > %s AND locations.latitude < %s AND locations.longitude < %s AND '
    queryargs += bounds
if options.power:
    query += 'frequencies.power>=%s AND '
    queryargs.append(options.power)
if options.owner:
    query += 'entities.owner LIKE %s AND '
    queryargs.append(options.owner)
query += 'frequencies.callsign=entities.callsign AND frequencies.callsign=locations.callsign'

cur.execute(query, queryargs)

chan = 0
channels = {}
for callsign, power, erp, freq, owner in cur.fetchall():
    print '%s %f (%.02f PWR; %.02f ERP) %s' % (callsign, freq, power, erp, owner)
    freq = int(float(freq) * 10000.0)
    freq = str(freq).rjust(8, '0')

    if not freq in channels:
        chan += 1
        s_chan = str(chan).rjust(3, '0')
        channels[freq] = s_chan

if options.export:
    fd = file(options.export, 'w')

    channels = channels.items()
    channels.sort(key=lambda x: x[1])
    for freq, chan in channels:
        fd.write('PM%sT%s\n' % (chan, freq))
if options.zerofill:
    for i in range(int(chan) + 1, 250):
        fd.write('PM%03i 00000000\n' % i)
