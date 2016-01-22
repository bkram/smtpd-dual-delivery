#!/usr/bin/env python
# SMTP dual delivery relay proxy daemon
# (c) 2016 bkram, GPL see LICENSE file

import asyncore
import ConfigParser
import email
import smtpd
import smtplib
import time
import daemon
import syslog


def getconfig():
    Config = ConfigParser.ConfigParser()
    try:
        Config.read('smtpd-dual-delivery.cfg')
        bindip = Config.get('daemon', 'bindip')
        bindport = Config.get('daemon', 'bindport')
        destip_a = Config.get('destination_a', 'ip')
        destport_a = Config.get('destination_a', 'port')
        destip_b = Config.get('destination_b', 'ip')
        destport_b = Config.get('destination_b', 'port')
        return (bindip, bindport, destip_a, destport_a, destip_b, destport_b)
    except:
        exit('Configuration error, please check smtpd-dual-delivery.cfg')


def logtime():
    return time.strftime('%D %H:%M:%S')


def getmesid(data):
    mailbody = email.message_from_string(data)
    return mailbody['Message-Id']


def deliverto(ip, port, mailfrom, rcpttos, data, messageid):
    syslog.syslog('%s %s Relay mail to %s:%s' % (logtime(), messageid, ip, port))
    try:
        sendserver = smtplib.SMTP(ip, port)
    except:
        return 'Error: could not open connection to %s:%s' % (ip, port)
    try:
        sendserver.sendmail(mailfrom, rcpttos, data)
    except:
        return "Error: could not relay message to server %s:%s" % (ip, port)
    try:
        sendserver.quit()
    except:
        return "Error: could not close connection to server %s:%s" % (ip, port)
    return 'Message relayed to %s:%s' % (ip, port)


class CustomSMTPServer(smtpd.SMTPServer):
    def process_message(self, peer, mailfrom, rcpttos, data):
        messageid = getmesid(data)
        syslog.syslog('%s %s Start Proxy action' % (logtime(), messageid))
        syslog.syslog(
                '%s %s Message from %s to %s size %s via %s' % (
                    logtime(), messageid, mailfrom, rcpttos, len(data), peer))
        state_a = deliverto(destip_a, destport_a, mailfrom, rcpttos, data, messageid)
        syslog.syslog('%s %s %s' % (logtime(), messageid, state_a))
        state_b = deliverto(destip_b, destport_b, mailfrom, rcpttos, data, messageid)
        syslog.syslog('%s %s %s' % (logtime(), messageid, state_b))
        syslog.syslog('%s %s End Proxy action' % (logtime(), messageid))
        return


def main():
    with daemon.DaemonContext():
        server = CustomSMTPServer((bindip, int(bindport)), None)
        asyncore.loop()


if __name__ == "__main__":
    (bindip, bindport, destip_a, destport_a, destip_b, destport_b) = getconfig()
    main()
