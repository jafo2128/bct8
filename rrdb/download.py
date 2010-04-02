from suds.client import Client
import sqlite3
import simplejson as json
import sys

config = json.load(open('config.json', 'r'))
db = sqlite3.connect('radioreference.db')

client = Client('file:///home/synack/src/bct8/rrdb/service.wsdl')
rr = client.service

auth = client.factory.create('authInfo')
auth.username = config['username']
auth.password = config['password']
auth.appKey = config['appkey']
auth.version = 7

sys.stdout.write('Zip code: ')
sys.stdout.flush()
zipcode = sys.stdin.readline().strip(' \r\n')

tags = rr.getTag(authInfo=auth, id=0)
zipinfo = rr.getZipcodeInfo(authInfo=auth, zipcode=zipcode)
systems = rr.getCountyInfo(authInfo=auth, ctid=zipinfo.ctid).trsList

cur = db.cursor()
for system in systems:
    # system.sName, system.sid, system.sType
    print 'Updating system:', system.sName
    cur.execute('DELETE FROM trs_freq WHERE sid=?', (system.sid,))
    cur.execute('DELETE FROM trs_info WHERE sid=?', (system.sid,))
    #cur.execute('DELETE FROM trs_sites WHERE sid=?', (system.sid,))
    cur.execute('DELETE FROM trs_talkgroup WHERE sid=?', (system.sid,))
    cur.execute('INSERT INTO trs_info(sid, name, type, lastupdated) VALUES(?, ?, ?, ?)', (system.sid, system.sName, system.sType, system.lastUpdated))

    for site in rr.getTrsSites(authInfo=auth, sid=system.sid):
        print '  %s (%i frequencies)' % (site.siteDescr, len(site.siteFreqs))
        cur.execute('INSERT INTO trs_sites(id, sid, tone, description) VALUES(?, ?, ?, ?)', (site.siteId, system.sid, site.siteCt, site.siteDescr))

        for freq in site.siteFreqs:
            cur.execute('INSERT INTO trs_freq(sid, use, freq, site_id) VALUES(?, ?, ?, ?)', (system.sid, str(freq.use), str(freq.freq), site.siteId))

    groups = rr.getTrsTalkgroups(authInfo=auth, sid=system.sid, tgCid=0, tgTag=0, tgDec=0)
    for tg in groups:
        cur.execute('INSERT INTO trs_talkgroup(sid, decid, alpha, description, mode) VALUES(?, ?, ?, ?, ?)', (system.sid, tg.tgDec, tg.tgAlpha, tg.tgDescr, tg.tgMode))
    print '  %i talkgroups' % len(groups)

cur.close()
db.commit()
db.close()
