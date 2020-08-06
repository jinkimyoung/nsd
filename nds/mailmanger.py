#!/usr/bin/env python3

import os
import sys
import platform

import smtplib
from email.mime.text import MIMEText

class MailManager():
    def __init__(self, owner):
        self._host      = platform.uname()[1] + 'gjinki@gmail.com'
        self._owner     = owner
        self._rookie    = 'gjinki@gmail.com'
        self._cvs       = 'gjinki@gmail.com'

    def __del(self):
        if hasattr(self, '_conn'):
            pass

    def send_rookie(self, dir_csr, file_modemelf):
        if not os.path.exists(dir_csr):
            raise Exception(f'{dir_csr} is not present')
        
        if not dir_csr.endswith('CrashScope'):
            dir_csr = os.path.join(dir_csr, 'CrashScope') if os.path.exists(os.path.join(dir_csr, 'CrashScope')) else None

        if dir_csr is None:
            raise Exception('Dump Path is invalid')

        # fill the mail's content
        mailtext = "Hi Rookie,\n\nTrigger " + 'autoscopeipa' + ", dump="+dir_csr+";alt_elf="+file_modemelf

        msg = MIMEText(mailtext, 'plain')
        msg['Subject'] = 'Auto scope for ' + dir_csr
        msg['From'] = self._owner
        msg['to'] = self._rookie
        print ("Mail is sent to " + tomail + " from " + owneremail)

        server = smtplib.SMTP(stmpname)
        try:
            server.sendmail(self._owner, [tomail], msg.as_string())
        except:
            print("mail delivery failed. Check QSDA machine to permit current machine to use SMTP")
        server.quit()
        return

    def sendmail(self, subject, message, server = None):
        #owneremail = "gjinki@gmail.com"
        #tomail = "gjinki@gmail.com"
        #cclist = "gjinki@gmail.com"
        if not server:
            server = qsda_def.getsmtpsrv()

        msg = MIMEText(message,'plain')
        msg['Subject'] = subject
        msg['From'] = owneremail
        msg['to'] = tomail
        msg['cc'] = cclist

        try:
            server = smtplib.SMTP(server)
            server.sendmail(owneremail, [tomail]+[cclist], msg.as_string())
            server.quit()
        except:
            print("mail delivery failed. Check QSDA machine to permit current machine to use SMTP")


