#!/usr/bin/env python
#
##### EMAIL2FILE v1.666 BETA
##### AUTHOR: vvn < vvn @ notworth dot it >
##### VERSION RELEASE: May 28, 2015
#####
##### SAVE EMAIL LISTS AS PLAIN TEXT format in script directory with one address per line.
##### you can include the password, if known, as a base64-encoded string separated by
##### a comma. just use "email@addy.com, encoded_password" on each line instead.
#####
##### if there are only a few email addresses, you can easily generate the file:
##### open a terminal or MS-DOS window to the script directory, then enter:
##### echo "your@email.com" >> emails.txt
##### repeat entering the above command for each email you want to use.
##### when prompted to enter the email list file name, enter "emails.txt".
##### PASSWORD LISTS SHOULD BE ONLY ONE WORD PER LINE. they can also be base64-encoded.
##### 
##### ENCRYPTION NOW FULLY WORKING FOR PASSWORD LISTS!
##### the feature has not been fully integrated in the main script!
##### use the encrypt feature to safely store your password lists,
##### and decrypt them for use with the script. it is highly recommended
##### that you delete the plaintext files after script completes.
#####
##### TO RUN SCRIPT: open terminal to script directory and enter "python email2file.py"
##### PLEASE USE PYTHON 2.7.X AND NOT PYTHON 3 OR YOU WILL GET SYNTAX ERRORS!
#####
##### works best on OSX and linux systems, but you can try it on windows.
##### i even tried to remove ANSI codes for you windows users, so you'd better use it!
#####
##### even better, if you are on windows, install the colorama or ansiterm module for
##### python to support ANSI colors.
##### if you have setuptools or pip installed, you can easily get it with:
##### "sudo pip install colorama"
##### you can get pip by entering: "sudo easy_install pip"
##### each inbox message is saved as a TXT or HTM file, depending on the text encoding
##### of the original email message. the files can be found in their respective account's
##### subfolder within the 'email-output' folder in your user HOME directory
##### (or the currently configured $HOME env path)
##### for example, a message from sender@email.com with subject "test"
##### in rich text format received at your@email.com will output to:
##### ~/email-output/your_email.com/your-01-"sender" <sender@email.com> .htm
##### where ~ is your HOME directory path
#####
##### a file of all mail headers is also saved in the 'email-output' directory.
##### it should be called example@email.com-headerlist-yyyy-mm-dd.txt
#####
##### attachments are saved either in account folder or 'attachments' subfolder.
#####
##### ****KNOWN BUGS:****
##### socket.error "[Errno 54] Connection reset by peer"
##### will interrupt the script execution. in case that it happens,
##### just start the script again:
##### python email2file.py or chmod +x *.py && ./email2file.py
##### if you run tor and proxychains, you can run the script within proxychains:
##### proxychains python email2file.py
#####
##### questions? bugs? suggestions? contact vvn at: vvn@notworth.it
#####
##### latest release should be found on github:
##### http://github.com/eudemonics/email2file
##### git clone https://github.com/eudemonics/email2file.git email2file
##################################################
##################################################
##### USER LICENSE AGREEMENT & DISCLAIMER
##### copyright, copyleft (C) 2014-2015  vvn < vvn @ notworth . it >
#####
##### This program is FREE software: you can use it, redistribute it and/or modify
##### it as you wish. Copying and distribution of this file, with or without modification,
##### are permitted in any medium without royalty provided the copyright
##### notice and this notice are preserved. This program is offered AS-IS,
##### WITHOUT ANY WARRANTY; without even the implied warranty of
##### MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##### GNU General Public License for more details.
##################################################
##################################################
##### getting credited for my work is nice. so are donations.
##### BTC: 1M511j1CHR8x7RYgakNdw1iF3ike2KehXh
##### https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=26PWMPCNKN28L
##### but to really show your appreciation, you should buy my EP instead!
##### you can stream and purchase it at: dreamcorp.bandcamp.com
##### (you might even enjoy listening to it)
##### questions, comments, feedback, bugs, complaints, death threats, marriage proposals?
##### contact me at:
##### vvn (at) notworth (dot) it
##### there be only about a thousand lines of code after this -->

from __future__ import print_function
import email, base64, getpass, imaplib, threading
import re, sys, os, os.path, datetime, socket, time, traceback, logging
from threading import Thread, Timer
from Crypto.Cipher import AES
from Crypto import Random
from Crypto.Util import Counter
from ansilist import ac

colorintro = '''
\033[34m=====================================\033[33m
---------\033[36m EMAIL2FILE v1.666 \033[33m---------
-------------------------------------
-----------\033[35m author : vvn \033[33m------------
----------\033[32m vvn@notworth.it \033[33m----------
\033[34m=====================================\033[33m
----\033[37m support my work: buy my EP! \033[33m----
---\033[37m http://dreamcorp.bandcamp.com \033[33m---
---\033[37m facebook.com/dreamcorporation \033[33m---
------\033[32m thanks for the support! \033[33m------
\033[34m=====================================\n\033[0m
'''

cleanintro = '''
=====================================
--------- EMAIL2FILE v1.666 ---------
-------------------------------------
----------- author : vvn ------------
---------- vvn@notworth.it ----------
=====================================
---- support my work: buy my EP! ----
--- http://dreamcorp.bandcamp.com ---
--- facebook.com/dreamcorporation ---
------ thanks for the support! ------
=====================================
'''

global usecolor

if os.name == 'nt' or sys.platform == 'win32':
   os.system('icacls encryptlist.py /grant %USERNAME%:F')
   os.system('icacls encodelist.py /grant %USERNAME%:F')
   try:
      import colorama
      colorama.init()
      usecolor = "color"
      progintro = colorintro
   except:
      try:
         import tendo.ansiterm
         usecolor = "color"
         progintro = colorintro
      except:
         usecolor = "clean"
         progintro = cleanintro
         pass
else:
   usecolor = "color"
   progintro = colorintro

print(progintro)

time.sleep(0.9)

# CHECK IF SINGLE EMAIL (1) OR LIST OF MULTIPLE EMAIL ADDRESSES IS USED (2)
print('''\033[34;1mSINGLE EMAIL ADDRESS OR LIST OF MULTIPLE EMAIL ADDRESSES?\033[0m
list of multiple email addresses must be in text format
with one email address per line. PASSWORD LIST with one
password per line in plain text or base64 encoded format
supported. ENCRYPTION MODULE provided in current release
and will be fully implemented in a future release. To
encrypt password list, run \033[36;1mpython encryptlist.py\033[0m.
***ALSO SUPPORTS EMAIL AND PASSWORD IN A SINGLE FILE:***
one email address and one password per line separated
by a comma (example@domain.com, password)
''')
qtyemail = raw_input('enter 1 for single email or 2 for multiple emails --> ')

while not re.search(r'^[12]$', qtyemail):
   qtyemail = raw_input('invalid entry. enter 1 for a single email address, or enter 2 to specify a list of multiple email addresses in text format --> ')

usewordlist = raw_input('do you want to use a word list rather than supply a password? enter Y/N --> ')

while not re.search(r'^[nyNY]$', usewordlist):
   usewordlist = raw_input('invalid entry. enter Y to use word list or N to supply password --> ')

usesslcheck = raw_input('use SSL? Y/N --> ')

while not re.search(r'^[nyNY]$', usesslcheck):
   usesslcheck = raw_input('invalid selection. please enter Y for SSL or N for unencrypted connection. -->')

sslcon = 'yes'

if usesslcheck.lower() == 'n':
   sslcon = 'no'

else:
   sslcon = 'yes'

# FUNCTION TO CHECK LOGIN CREDENTIALS
def checklogin(emailaddr, emailpass, imap_server, sslcon):

   global checkresp
   efmatch = re.search(r'^[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*(\.[a-zA-Z]{2,9})$', emailaddr)
   while not efmatch:
      emailaddr = raw_input('invalid email format. enter a valid email address --> ')
   
   imap_port = 993

   if 'no' in sslcon:
      imap_port = 143

      if 'gmail.com' in emaildomain:
         imap_port = 587

   if 'yes' in sslcon:
      server = imaplib.IMAP4_SSL(imap_server, imap_port)

   else:
      server = imaplib.IMAP4(imap_server, imap_port)

   checkresp = 'preconnect'
   if usecolor == 'color':
      print('\nattempting to log onto: ' + ac.GREEN + emailaddr + ac.CLEAR)
   else:
      print('\nattempting to log onto: %s' % emailaddr)
   print('\n')
   
   logging.info('INFO: attempting to connect to IMAP server to check login credentials for account %s' % emailaddr)

   try:

      loginstatus, logindata = server.login(emailaddr, emailpass)

      if 'OK' in loginstatus:
         if usecolor == 'color':
            print(ac.BEIGEBOLD + 'LOGIN SUCCESSFUL: ' + ac.PINKBOLD + emailaddr + ac.CLEAR)
         else:
            print('LOGIN SUCCESSFUL: %s' % emailaddr)
         logging.info('INFO: LOGIN successful for account %s' % emailaddr)
         checkresp = 'OK'

      elif 'AUTHENTICATIONFAILED' in loginstatus:
         loginmsg = 'LOGIN FAILED: %s with %s' % (loginstatus, logindata)
         print(loginmsg)
         logging.error('ERROR: %s' % loginmsg)
         checkresp = 'AUTHENFAIL'

      elif 'PRIVACYREQUIRED' in loginstatus:
         loginmsg = 'LOGIN FAILED: %s with %s' % (loginstatus, logindata)
         print(loginmsg)
         logging.error('ERROR: %s' % loginmsg)
         checkresp = 'PRIVACYREQ'

      elif 'UNAVAILABLE' in loginstatus:
         loginmsg = 'LOGIN FAILED: %s with %s' % (loginstatus, logindata)
         print(loginmsg)
         logging.error('ERROR: %s' % loginmsg)
         checkresp = 'UNAVAIL'

      elif 'AUTHORIZATIONFAILED' in loginstatus:
         loginmsg = 'LOGIN FAILED: %s with %s' % (loginstatus, logindata)
         print(loginmsg)
         logging.error('ERROR: %s' % loginmsg)
         checkresp = 'AUTHORFAIL'

      elif 'EXPIRED' in loginstatus:
         loginmsg = 'LOGIN FAILED: %s with %s' % (loginstatus, logindata)
         print(loginmsg)
         logging.error('ERROR: %s' % loginmsg)
         checkresp = 'EXPIRED'

      elif 'CONTACTADMIN' in loginstatus:
         loginmsg = 'LOGIN FAILED: %s' % loginstatus
         print(loginmsg)
         logging.error('ERROR: %s' % loginmsg)
         checkresp = 'ADMINREQ'

      else:
         print('Unable to connect: %s' % emailaddr)
         logging.error('ERROR: %s' % loginstatus)
         checkresp = 'UNKNOWN'
         
   except IOError as e:
      pass
      logging.error('IO ERROR: %s' % str(e))
      checkresp = 'IOERROR'
   
   except socket.error as e:
      pass
      logging.error('SOCKET ERROR: %s' % str(e))
      checkresp = 'SOCKETERROR'

   except server.error as e:
      pass
      logging.error('IMAPLIB ERROR: %s' % str(e))
      checkresp = 'IMAPERROR'

      if 'BAD' in str(e):
         checkresp = 'BAD'
      else:
         checkresp = 'ERROR'

   except socket.timeout as e:
      pass
      print('Socket timeout: %s' % str(e))
      logging.error('ERROR: Socket timeout')
      checkresp = 'TIMEOUT'

   except:
      pass
      checkimap = raw_input('error logging onto ' + imap_server + '. to use a different IMAP server, enter it here. else, press ENTER to continue --> ')
      if len(checkimap) > 0:
         while not re.search(r'^[_a-zA-Z0-9-]+(\.[_a-zA-Z0-9-]+)*(\.[a-zA-Z0-9-]+)*(\.[a-zA-Z]{2,9})$', checkimap):
            checkimap = raw_input('invalid format. please enter a valid IMAP server --> ')
         imap_server = checkimap
      checkresp = 'OTHERERROR'
      checklogin(emailaddr, emailpass, imap_server, sslcon)
      
   return checkresp
# END OF FUNCTION checklogin()

# FUNCTION TO CHECK FOR EMAIL FORMAT ERRORS BEFORE SUBMITTING TO SERVER
def checkformat(emailaddr):

   # START WHILE LOOP TO CHECK EMAIL FORMAT FOR ERRORS BEFORE ATTEMPTING LOGIN
   match = re.search(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,9})$', emailaddr)
   while not match:
      emailformat = 'bad'
      if usecolor == 'color':
         print('\033[31m invalid email format \033[0m\n')
      else:
         print('invalid email format')
      emailaddr = raw_input('please enter email again --> ')
      emailpass = getpass.getpass('please enter password --> ')

   emailformat = 'good'
   return emailformat
# END OF FUNCTION checkformat()

# FUNCTION TO DECODE EMAIL BODY AND ATTACHMENTS
def decode_email(msgbody):

   msg = email.message_from_string(msgbody)

   if msg is None:
      decoded = msg

   decoded = msg
   text = ""
   att = False

   if msg.is_multipart():
      html = None

      for part in msg.get_payload():

         print("\033[31m%s, %s\033[0m" % (part.get_content_type(), part.get_content_charset()))

         if part.get_content_charset() is None:
            text = part.get_payload(decode=True)
            continue

         charset = part.get_content_charset()

         if part.get_content_type() == 'text/plain':
            text = unicode(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')
            enc = part['Content-Transfer-Encoding']
            if enc == "base64":
               text = part.get_payload()
               text = base64.decodestring(text)

         if part.get_content_type() == 'text/html':
            html = unicode(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')

         if part.get_content_maintype() == 'multipart':
            continue

         elif part.get('Content-Disposition') is None:
            continue

         elif part.get_content_type() == "multipart/alternative":
            text = part.get_payload(decode=True)
            enc = part['Content-Transfer-Encoding']
            if part.get_content_type() == "text/plain":
                text = part.get_payload()
                if enc == "base64":
                    text = base64.decodestring(text)

         filename = part.get_filename()

         if bool(filename):

            homedir = os.path.expanduser("~")

            rootdir = os.path.join(homedir, 'email-output')

            if not os.path.exists(rootdir):
               os.makedirs(rootdir, 0755)

            atdomain = re.search("@.*", emailaddr).group()
            emaildomain = atdomain[1:]
            i = len(emailaddr) - len(atdomain)
            user_savename = emailaddr[:i]
            # user_savename = emailaddr.rstrip(atdomain)
            subdir = user_savename+"_"+emaildomain

            detach_dir = os.path.join(rootdir, subdir)

            if not os.path.exists(detach_dir):
               os.makedirs(detach_dir, 0755)

            att_path = os.path.join(detach_dir, 'attachments', filename)

            if 'attachments' not in os.listdir(detach_dir):
               os.makedirs(detach_dir + '/attachments', 0755)

            att = True

            if not os.path.isfile(att_path):
               attfile = open(att_path, 'wb+')
               attfile.write(part.get_payload(decode=True))
               attfile.close()
               decoded = attfile

      if att is False:
         decoded = msg

         if html is None and text is not None:
            decoded = text.strip()

         elif html is None and text is None:
            decoded = msg

         else:
            decoded = html.strip()

   else:
      decoded = msg

   return decoded
# END OF FUNCTION decode_email()

# FUNCTION TO LOG ONTO IMAP SERVER FOR SINGLE EMAIL ADDRESS
def getimap(emailaddr, emailpass, imap_server, sslcon):

   imap_port = 993
   server = imaplib.IMAP4_SSL(imap_server, imap_port)

   if 'no' in sslcon:
      imap_port = 143
      server = imaplib.IMAP4(imap_server, imap_port)

   if 'gmail.com' in emailaddr and 'no' in sslcon:
      imap_port = 587

   attempts = 20

   while True and attempts > 0:

      try:

         loginstatus, logindata = server.login(emailaddr, emailpass)

         if loginstatus == 'OK':

            select_info = server.select('INBOX')
            status, unseen = server.search(None, 'UNSEEN')
            typ, listdata = server.list()
            countunseen = len(unseen)

            if usecolor == 'color':

               print("\n\033[35m%d UNREAD MESSAGES\033[0m" % len(unseen))
               print()
               print('Response code: \n\033[32m', typ)
               print('\033[0m\nFOLDERS:\n\033[33m', listdata)
               print('\033[34m\nlogin successful, fetching emails.. \033[0m\n')

            else:

               print("%d UNREAD MESSAGES" % len(unseen))
               print()
               print('Response code: \n', typ)
               print('\nFOLDERS:\n', listdata)
               print('\nlogin successful, fetching emails.. \n')

            logging.info('INFO: LOGIN successful for %s.' % emailaddr)
            logging.info('INFO: %d unread messages.' % countunseen)
            logging.info('INFO: fetching all messages...')

            # server.list()

            server.select()

            result, msgs = server.search(None, 'ALL')

            ids = msgs[0]
            id_list = ids.split()

            print(id_list)

            if usecolor == 'color':

               print('\033[37m------------------------------------------------------------\n\033[0m')

            else:

               print('------------------------------------------------------------')


            homedir = os.path.expanduser("~")

            rootdir = os.path.join(homedir, 'email-output')

            if not os.path.exists(rootdir):
               os.makedirs(rootdir, 0755)

            printdate = str(datetime.date.today())

            prev_file_name = emailaddr+"-headerlist-"+printdate+".txt"
            prev_complete_name = os.path.join(rootdir, prev_file_name)

            for email_uid in id_list:

               result, rawdata = server.fetch(email_uid, '(RFC822)')

               rawbody = rawdata[0][1]

               m = email.message_from_string(rawbody)

               msgfrom = m['From'].replace('/', '-')

               body = decode_email(rawbody)

               emaildomain = atdomain[1:]
               j = len(emailaddr) - len(atdomain)
               user_save = emailaddr[:j]

               subdir =  user_save + "_" + emaildomain
               save_path = os.path.join(rootdir, subdir)

               if not os.path.exists(save_path):
                  os.makedirs(save_path)

               mbody = email.message_from_string(rawbody)

               if mbody.is_multipart():

                  ext = ".txt"

                  for mpart in mbody.get_payload():

                     if 'text' in mpart.get_content_type():
                        ext = ".txt"
                        isattach = False

                        if mpart.get_content_type() == 'text/html':
                           ext = ".htm"
                           isattach = False

                     else:
                        file_name = mpart.get_filename()
                        isattach = True

               else:
                  isattach = False
                  ext = ".txt"

               if isattach is False:
                  file_name = user_save + "-" + email_uid + "-" + msgfrom[:35] + ext

               if file_name is None:
                  file_name = user_save + "-" + msgfrom[:35] + "-" + email_uid + ext

               complete_name = os.path.join(save_path, file_name)

               dtnow = datetime.datetime.now()
               dtyr = str(dtnow.year)
               dtmo = str(dtnow.month)
               dtday = str(dtnow.day)
               dthr = str(dtnow.hour)
               dtmin = str(dtnow.minute)

               dtdate = str(dtyr + "-" + dtmo + "-" + dtday)
               dttime = str(dthr + "." + dtmin)

               if os.path.isfile(complete_name):

                  print('\n\033[33m' + complete_name + '\033[0m already exists, skipping.. \n')

               else:

                  if type(body) is str or type(body) is buffer and isattach is True:
                     print('\n\033[34mdownloading file: \033[33m' + str(file_name) + '\033[0m\n')
                     bodyfile = open(complete_name, 'wb+')
                     # bodyfile.seek(0)
                     bodyfile.write(body)
                     bodyfile.close()

                  else:
                     bodyfile = open(complete_name, 'wb+')
                     bodyfile.write("SENDER: \n")
                     bodyfile.write(msgfrom)
                     bodyfile.write('\n')
                     # bodyfile.write('Decoded:\n')
                     bodyfile.write(str(body))
                     bodyfile.write('\nRAW MESSAGE DATA:\n')
                     bodyfile.write(rawbody)
                     bodyfile.write('\n')
                     bodyfile.write('file saved: ' + dtdate + ', ' + dttime)
                     bodyfile.write('\n')
                     bodyfile.close()

                  if usecolor == 'color':

                     print('\033[36m\033[1mmessage data saved to new file: \033[35m' + complete_name + '\033[0m\n')

                  else:

                     print('message data saved to new file: ' + complete_name)

               if usecolor == 'color':

                  print('\033[37m------------------------------------------------------------\033[0m\n')

                  resp, data = server.fetch(email_uid, '(UID FLAGS BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])')
                  print('\033[35m' + email_uid + '\033[0m\n')

               else:

                  print('------------------------------------------------------------\n')

                  resp, data = server.fetch(email_uid, '(UID FLAGS BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])')
                  print(email_uid)

               print(data[0][1] + '\n')
               msgpreview = data[0][1]

               if not os.path.isfile(prev_complete_name):
                  prevfile = open(prev_complete_name, 'wb+')
               #   prevfile.write('Email headers for: ' + emailaddr + '\n')
                  prevfile.write(email_uid)
                  prevfile.write("\n")
                  prevfile.write(msgpreview)
                  prevfile.write("\n")
                  prevfile.close()

            if usecolor == 'color':

               print('\033[32minbox contents successfully saved to file. YAY! \033[0m\n')

            else:

               print('inbox contents successfully saved to file. YAY!')

         if usecolor == 'color':

            print('list of message previews saved as: \033[31m' + prev_complete_name + '\033[0m \n')

         else:

            print('list of message previews saved as: ', prev_complete_name)

         print('logging out..\n')

         server.logout()

         print('logout successful.\n')
         # EXIT LOOP IF SUCCESSFULLY AUTHENTICATED
         attempts = -1
         break

      except server.error as e:
         pass
         logging.error('IMAPLIB ERROR: %s' % str(e))
         checkresp = 'ERROR'

         if usecolor == 'color':
            print('\033[32mconnection failed to IMAP server.\033[0m\n')
            print('\033[36mIMAPLIB ERROR: \033[33m' + str(e) + '\033[0m\n')

         else:

            print('connection failed to IMAP server.\n')
            print('IMAPLIB ERROR: ' + str(e) + '\n')

         if qtyemail == '1' and attempts >= 1:

            attempts =- 1
            emailaddr = raw_input('please enter email again --> ')
            emailpass = getpass.getpass('please enter password --> ')

            matchaddy = re.search(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,9})$', emailaddr)

            while not matchaddy and attempts > 1:
               print('\033[31m invalid email format \033[0m\n')
               attempts = attempts - 1
               
            
            atdomain = re.search("@.*", emailaddr).group()
            emaildomain = atdomain[1:]

            imap_server = 'imap.' + emaildomain
            imap_port = 993
            
            getimap(emailaddr, emailpass, imap_server, sslcon)

   if attempts is 0:
      print('too many logon failures. unable to log onto IMAP server. quitting..')
      sys.exit(1)
# END OF FUNCTION getimap(emailaddr, emailpass, imap_server, sslcon)

# FUNCTION FOR IMAP CONNECTION USING MULTIPLE ADDRESSES
def getimapmulti(emailaddr, emailpass, imap_server, sslcon):

   imap_port = 993
   server = imaplib.IMAP4_SSL(imap_server, imap_port)
   
   if 'no' in sslcon:
      imap_port = 143

      if 'gmail.com' in emailaddr:
         imap_port = 587
      
      server = imaplib.IMAP4(imap_server, imap_port)

   loginstatus, logindata = server.login(emailaddr, emailpass)

   attempts = 0

   while attempts <= 20:

      try:
         attempts += 1
         select_info = server.select('INBOX')
         status, unseen = server.search(None, 'UNSEEN')

         typ, listdata = server.list()

         countunseen = len(unseen)

         if usecolor == 'color':

            print("\n\033[35m%d UNREAD MESSAGES\033[0m" % len(unseen))
            print()
            print('Response code: \n\033[32m', typ)
            print('\033[0m\nFOLDERS:\n\033[33m', listdata)
            print('\033[34m\nlogin successful, fetching emails.. \033[0m\n')

         else:

            print("%d UNREAD MESSAGES" % len(unseen))
            print()
            print('Response code: \n', typ)
            print('\nFOLDERS:\n', listdata)
            print('\nlogin successful, fetching emails.. \n')

         server.select()
         result, msgs = server.search(None, 'ALL')

         ids = msgs[0]
         id_list = ids.split()

         print(id_list)

         if usecolor == 'color':

            print('\033[37m------------------------------------------------------------\n\033[0m')

         else:

            print('------------------------------------------------------------')

         homedir = os.path.expanduser("~")

         rootdir = os.path.join(homedir, 'email-output')

         if not os.path.exists(rootdir):
            os.makedirs(rootdir, 0755)

         printdate = str(datetime.date.today())

         prev_file_name = emailaddr+"-headerlist-"+printdate+".txt"
         prev_complete_name = os.path.join(rootdir, prev_file_name)

         for email_uid in id_list:

            result, rawdata = server.fetch(email_uid, '(RFC822)')

            rawbody = rawdata[0][1]

            m = email.message_from_string(rawbody)

            msgfrom = m['From'].replace('/', '-')

            body = decode_email(rawbody)

            emaildomain = atdomain[1:]
            j = len(emailaddr) - len(atdomain)
            user_save = emailaddr[:j]

            subdir =  user_save + "_" + emaildomain
            save_path = os.path.join(rootdir, subdir)

            if not os.path.exists(save_path):
               os.makedirs(save_path)

            mbody = email.message_from_string(rawbody)

            if mbody.is_multipart():

               ext = ".txt"

               for mpart in mbody.get_payload():

                  if 'text' in mpart.get_content_type():
                     ext = ".txt"
                     isattach = False

                     if mpart.get_content_type() == 'text/html':
                        ext = ".htm"
                        isattach = False

                  else:
                     file_name = mpart.get_filename()
                     isattach = True

            else:
               isattach = False
               ext = ".txt"

            if isattach is False:
               file_name = user_save + "-" + email_uid + "-" + msgfrom[:25] + ext

            if file_name is None:
               file_name = user_save + "-" + msgfrom[:25] + "-" + email_uid + ext

            complete_name = os.path.join(save_path, file_name)

            dtnow = datetime.datetime.now()
            dtyr = str(dtnow.year)
            dtmo = str(dtnow.month)
            dtday = str(dtnow.day)
            dthr = str(dtnow.hour)
            dtmin = str(dtnow.minute)

            dtdate = str(dtyr + "-" + dtmo + "-" + dtday)
            dttime = str(dthr + "." + dtmin)

            if os.path.isfile(complete_name):

               if usecolor == 'color':

                  print('\n\033[33m' + complete_name + '\033[0m already exists, skipping.. \n')

               else:

                  print(complete_name + 'already exists, skipping.. \n')
            
            # PRINT MESSAGE DATA TO FILE
            else:

               if type(body) is str or type(body) is buffer and isattach is True:

                  if usecolor == 'color':
                     print('\n\033[34mdownloading file: \033[33m' + str(file_name) + '\033[0m\n')

                  else:
                     print('downloading file: ' + str(file_name))

                  bodyfile = open(complete_name, 'wb+')
                  # bodyfile.seek(0)
                  bodyfile.write(body)
                  bodyfile.close()

               else:
                  bodyfile = open(complete_name, 'wb+')
                  bodyfile.write("SENDER: \n")
                  bodyfile.write(msgfrom)
                  bodyfile.write('\n')
                  # bodyfile.write('Decoded:\n')
                  bodyfile.write(str(body))
                  bodyfile.write('\nRAW MESSAGE DATA:\n')
                  bodyfile.write(rawbody)
                  bodyfile.write('\n')
                  bodyfile.write('file saved: ' + dtdate + ', ' + dttime)
                  bodyfile.write('\n')
                  bodyfile.close()

               if usecolor == 'color':

                  print('\033[36m\033[1mmessage data saved to new file: \033[35m' + complete_name + '\033[0m\n')

               else:

                  print('message data saved to new file: ' + complete_name)

            if usecolor == 'color':

               print('\033[37m------------------------------------------------------------\033[0m\n')

               resp, data = server.fetch(email_uid, '(UID FLAGS BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])')
               print('\033[35m' + email_uid + '\033[0m\n')

            else:

               print('------------------------------------------------------------\n')

               resp, data = server.fetch(email_uid, '(UID FLAGS BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])')
               print(email_uid)

            print(data[0][1] + '\n')
            msgpreview = data[0][1]

            if not os.path.isfile(prev_complete_name):
               prevfile = open(prev_complete_name, 'wb+')
               prevfile.write(email_uid)
               prevfile.write("\n")
               prevfile.write(msgpreview)
               prevfile.write("\n")
               prevfile.close()

         if usecolor == 'color':

            print('\033[32minbox contents successfully saved to file. YAY! \033[0m\n')

         else:

            print('inbox contents successfully saved to file. YAY!')

         if usecolor == 'color':
            print('list of message previews saved as: \033[31m' + prev_complete_name + '\033[0m \n')
         else:
            print('list of message previews saved as: %s' % prev_complete_name)

         logging.info('INFO: inbox contents saved to file with preview file %s' % prev_complete_name)
         print('logging out..\n')
         logging.info('INFO: logging off IMAP server.')
         server.logout()
         if usecolor == 'color':
            print('logout successful for \033[38m%s.\033[0m\n' % emailaddr)
            print('\033[34m------------------------------------------------------------\033[0m\n')
         else:
            print('logout successful for %s.\n' % emailaddr)
            print('------------------------------------------------------------\n')
         logging.info('INFO: logout successful for %s.' % emailaddr)
         checkresp = 'OK'
         attempts = 100
         break
         
      except IOError as e:
         pass
         print("IO SOCKET ERROR: %s" % str(e))
         logging.error('IO SOCKET ERROR: %s' % str(e))
         traceback.print_exc()
         checkresp = 'IOERROR'
         attempts += 1
         
      except socket.error as e:
         pass
         print("SOCKET ERROR: %s" % str(e))
         traceback.print_exc()
         logging.error('SOCKET ERROR: %s' % str(e))
         checkresp = 'SOCKETERROR'
         attempts += 1
      
      except socket.timeout as e:
         pass
         print('Socket timeout: %s, retrying connection..' % str(e))
         time.sleep(5.0)
         checkresp = 'TIMEOUT'
         attempts += 1
      
      except TypeError as e:
         pass
         print("TYPE ERROR: %s" % e)
         logging.error('TYPE ERROR: %s' % e)
         checkresp = 'TYPEERROR'
         attempts += 1

      except server.error as e:
         pass
         logging.error('SERVER ERROR: %s' % e)
         checkresp = 'SERVERERROR'
         attempts += 1
         
         if re.search(r'socket error: EOF$', str(e)):
            checkresp = 'EOF'
            if usecolor == 'color':
               print(ac.OKBLUE + '\nsocket reporting EOF error. trying again after 10 seconds..\n' + ac.CLEAR)
            else:
               print('\nsocket reporting EOF error. trying again after 10 seconds.. \n')
            time.sleep(10)
         else:
            if usecolor == 'color':
               print('\033[35mfailed to connect to IMAP server.\033[0m\n')
               print(ac.ORANGEBOLD + 'ERROR: ' + ac.OKAQUA + str(e) + ' \033[0m\n')
            else:
               print('failed connecting to IMAP server.\n')
               print('ERROR: ' + str(e) + '\n')
            
         if qtyemail == '1' and 'OK' not in checkresp:
            while True and attempts <= 20:
               loginok = checklogin(emailaddr, emailpass, imap_server, sslcon)
               if 'OK' in loginok:
                  getimap(emailaddr, emailpass, imap_server, sslcon)
                  break
               else:
                  emailaddr = raw_input('please enter email again --> ')
                  emailpass = getpass.getpass('please enter password --> ')
               attempts += 1
               logging.info('INFO: trying again with user-supplied email %s' % emailaddr)
               print('RETRYING with %s..' % emailaddr)
            
      except:
         pass
         
         # start with a socket at 30-second timeout
         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         sock.settimeout(30.0)
 
         # check and turn on TCP Keepalive
         x = sock.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)
         if( x == 0):
            print('Socket KEEPALIVE off, turning on')
            x = sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            logging.info('INFO: setsockopt=', x)
         else:
            print('Socket Keepalive already on')
            logging.info('INFO: Socket KEEPALIVE already on')

         try:
            sock.connect(imap_server, imap_port)
            attempts += 1

         except socket.error:
            pass
            print('Socket connection failed')
            traceback.print_exc()
            time.sleep(5.0)
            attempts += 1
            continue
         
         except sock.error as e:
            pass
            if usecolor == 'color':
               print(ac.BEIGEBOLD + 'ERROR: %s' + ac.CLEAR) % str(e)
            else:
               print('ERROR: %s') % str(e)
            traceback.print_exc()
            time.sleep(5.0)
            attempts += 1
            continue
         
         except:
            pass
            attempts += 1

         print('Socket connection established!')

         while 1:
            try:
               req = sock.recv(6)

            except socket.timeout:
               pass
               print('Socket timeout, retrying connection..')
               time.sleep( 5.0)
               attempts += 1
               continue
               # traceback.print_exc()

            except:
               pass
               traceback.print_exc()
               print('Other Socket error. Trying to recreate socket..')
               attempts += 1
               # break from loop
               break

            print('RECEIVED SOCKET: ', req)
            continue

         try:
            sock.close()
         except:
            pass
         continue
      
      return checkresp
# END OF FUNCTION getimapmulti(emailaddr, emailpass, imap_server, sslcon)

# MULTIPLE EMAIL ADDRESSES
if qtyemail == '2':
   emaillistfile = raw_input('please copy the email list file to the script directory, then enter filename --> ')
   while not os.path.isfile(emaillistfile):
      emaillistfile = raw_input('the file path specified does not exist or is not accessible. please check the file and enter again --> ')

   ef = open(emaillistfile, "r")
   emailfile = ef.readlines()
   eflen = len(emailfile)

   # USING PASSWORD LIST
   if usewordlist.lower() == 'y':
      pwlistfile = raw_input('please make sure password list is in the script directory, then enter the filename --> ')
      while not os.path.isfile(pwlistfile):
         pwlistfile = raw_input('the path to the word list file you entered is not valid. please check the file and enter again --> ')

      encryptsel = raw_input('is the word list encrypted using encryptlist.py? Y/N --> ')      
      while not re.search(r'^[nNyY]$', encryptsel):
         encryptsel = raw_input('invalid selection. enter Y if word list was encrypted using encryptlist.py or N if not encrypted --> ')
      
      # IF PASSWORD LIST IS ENCRYPTED  
      if encryptsel.lower() == 'y':
      
         if os.path.isfile('secret.key'):
            if usecolor == 'color':
               keycheck = raw_input('base64-encoded key generated by encryptlist.py found at ' + ac.GREEN + 'secret.key' + ac.CLEAR + '. \nis the password list encrypted using this key? enter Y/N --> ')
            else:
               keycheck = raw_input('base64-encoded key generated by encryptlist.py found at secret.key. \nis the password list encrypted using this key? Y/N --> ')
            while not re.match(r'^[nNyY]$', keycheck):
               keycheck = raw_input('invalid selection. enter Y to use secret.key or N to enter another key file --> ')
            secretkey = 'secret.key'
            if keycheck.lower() == 'n':
               secretkey = raw_input('please enter filename for the key used to encrypt your password list --> ')
               while not os.path.isfile(secretkey):
                  secretkey = raw_input('file not found. please check the filename and enter again --> ')
            encpass = getpass.getpass('please enter the secret passphrase used to generate the encrypted file --> ')
            AES_Dec = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip('&')
            cryptfile = open(secretkey, 'r')
            a = cryptfile.readline()
            cryptkey = base64.b64decode(a)
            cryptfile.close()

            secretpadlen = 16 - (len(encpass) % 16)
            secret = encpass + ('&' * secretpadlen)
            cipher = AES.new(cryptkey, AES.MODE_CBC, secret)
            print('\nusing encryption key: ')
            if usecolor == 'color':
               print(ac.PINKBOLD + a + ac.CLEAR)
            else:
               print(a)
            print('')
      
      # IF PASSWORD LIST NOT ENCRYPTED
      else:
      
         b64sel = raw_input('is the word list base64-encoded using encodelist.py? Y/N --> ')
         while not re.search(r'^[nNyY]$', b64sel):
            b64sel = raw_input('invalid selection. enter Y if word list is base64-encoded or N if plain text --> ')

         if b64sel.lower() == 'n':         
            gotoencsel = raw_input('storing passwords in plaintext is a security risk. \nenter 1 to encrypt the contents of your password list. \nenter 2 to use base-64 encoding. enter 3 to continue with a plaintext password list. --> ')
            while not re.search(r'^[1-3]$', gotoencsel):
               gotoencsel = raw_input('invalid selection. enter 1 to run script to encrypt your password list. \nenter 2 to base64-encode it. or enter 3 to continue with plaintext list --> ')
            if gotoencsel == '1':
               print("launching encryptlist.py..")
               os.system('chmod +x encryptlist.py')
               os.system('python encryptlist.py')
            elif gotoencsel == '2':
               print("launching encodelist.py..")
               os.system('chmod +x encodelist.py')
               os.system('python encodelist.py')
            else:
               print('*** to encrypt your list in the future, run \'python encryptlist.py\'. to  base64-encode your list in the future, run \'python encodelist.py\' ***')
               
      
      print("\nusing word list: ")
      if usecolor == 'color':
         print(ac.YELLOWBOLD + pwlistfile + ac.CLEAR)
      else:
         print(pwlistfile)
      print('')

      lnemail = ''
      lnpass = ''
 
      if usecolor == 'color':
         print("\n\033[31mEMAIL ADDRESSES IN FILE:\033[0m %s \n" % str(eflen))
      else:
         print("EMAIL ADDRESSES IN FILE: %s \n" % str(eflen))

      efcount = 1
      lenfile = len(emailfile)
      countdown = lenfile
      
      for index,line in enumerate(emailfile):
      
         emindex = index + 1
         
         countdown -= 1
         
         empercent = float(emindex) / float(lenfile)
         empercent2 = empercent - .05
         pr2 = int(empercent2 * 100)
         pr = int(empercent * 100)
         
         progress = lambda a: str(a) + "%"
         
         if usecolor == 'color':
            print("PROGRESS:\033[36;1m %s \033[0m" % str(emindex))
            print("TOTAL EMAIL ADDRESSES:\033[36;1m %s \033[0m\n" % str(lenfile))
            print("PERCENT COMPLETE:\033[36;1m %s \033[0m\n" % progress(pr2))
         
         else:
            print("PROGRESS: %s" % str(emindex))
            print("TOTAL EMAIL ADDRESSES: %s \n" % str(lenfile))
            print("PERCENT COMPLETE: %s \n" % progress(pr2))
         
         # WITH EMAIL AND PASSWORD IN SAME FILE
         if re.search(r'^[\,]$', line):

            line = line.strip()
            linevals = line.split(",")

            lnemail = linevals[0]
            lnemail = str(lnemail.strip())
            lnpass = linevals[1]
            
            if b64sel.lower() == 'y':
               lnpass = base64.b64decode(lnpass)

            lnpass = lnpass.strip()
            lnpass = lnpass.replace("\n","")
            lnpass = str(lnpass)

            if usecolor == 'color':
               print('\033[36mUSING EMAIL ADDRESS: \033[34;1m' + lnemail + ac.CLEAR)
            
            else:
               print('USING EMAIL ADDRESS: ' + lnemail)
            
            atdomain = re.search("@.*", lnemail).group()
            emaildomain = atdomain[1:]

            imap_server = 'imap.' + emaildomain
            imap_port = 993
                  
            loginok = checklogin(lnemail, lnpass, imap_server, sslcon)

            if 'OK' not in loginok:
               print('login failure. skipping to next entry in list...')
               logging.debug('DEBUG: LOGIN to %s failed' % emailaddr)
               continue
               
            else:
               logging.info('INFO: LOGIN to %s successful' % emailaddr)
               getimapmulti(lnemail, lnpass, imap_server, sslcon)
         
         # EMAIL AND PASSWORD IN SEPARATE FILES
         else:

            atdomain = re.search("@.*", line).group()
            emaildomain = atdomain[1:]

            imap_server = 'imap.' + emaildomain
            imap_port = 993
         
            if usecolor == 'color':
                     print('\n\033[34m------------------------------------------------------------\033[0m\n')
                     print('\n\033[36mUSING EMAIL ADDRESS: \033[34;1m' + line + ac.CLEAR)
                     print('\n\033[34m------------------------------------------------------------\033[0m\n')
            
            else:
               print('\n------------------------------------------------------------\n')
               print('\nusing email address: ' + line)
               print('\n------------------------------------------------------------\n')
            
            pf = open(pwlistfile, "r+")
            wordlist = pf.readlines()
            listlen = len(wordlist)

            tries = 0
            lnemail = line.strip()
            lnemail = lnemail.replace("\n","")

            for lnpass in wordlist:
            
               if encryptsel.lower() == 'y':
                  lnpass = AES_Dec(cipher, lnpass)

               elif b64sel.lower() == 'y':
                  lnpass = base64.b64decode(lnpass)
                  
               lnpass = lnpass.strip()
               lnpass = lnpass.replace("\n","")
               lnpass = str(lnpass)
               loginok = checklogin(lnemail, lnpass, imap_server, sslcon)
               tries += 1

               if 'OK' not in loginok and tries <= listlen:
                  #print('tried: %s') % str(lnpass)
                  if usecolor == 'color':
                     print('\n\033[31mLOGIN FAILED. \033[34;1mtrying next entry...\033[0m\n')
                     print('\033[33mtries: \033[35m' + str(tries) + '\033[33m out of \033[35m %s \033[0m' % str(listlen))
                     print('\n\033[34m------------------------------------------------------------\033[0m\n')
                  else:
                     print('\nLOGIN FAILURE. trying next entry...\n')
                     print('tries: ' + str(tries) + ' out of ' + str(listlen))
                     print('\n------------------------------------------------------------\n')
                  continue

               else:
                  print('\ngetting mailbox contents...\n')
                  logging.info('INFO: LOGIN to %s successful! getting mailbox contents...' % lnemail)
                  getimapmulti(lnemail, lnpass.strip(), imap_server, sslcon)
                  tries = 100
                  break

            if tries >= listlen and tries < 100:
               if usecolor == 'color':
                  print('\n\033[35mexhausted all entries in password list for:\033[33m %s.\n\033[0m' % lnemail)
               else:
                  print('\nexhausted all entries in password list for %s.\n' % lnemail)
         
         efcount += 1
         
         if usecolor == 'color':
            print("remaining email addresses to process:\033[32;1m %s \033[0m\n" % str(countdown))
            print("PERCENT COMPLETE:\033[36;1m %s \033[0m\n" % progress(pr))
            print('\n\033[34m------------------------------------------------------------\033[0m\n')
         else:
            print("PERCENT COMPLETE: %s \n" % progress(pr))
               
         if countdown <= 0 and efcount >= lenfile:
            if usecolor == 'color':
               print('\033[41;1m\033[33mfinished processing all email addresses and passwords.\033[0m\n')
            else:
               print('finished processing all email addresses and passwords.\n')
            break
            
   # NOT USING PASSWORD LIST
   else:
   
      efcount = 1
      
      while efcount <= eflen:
         for line in ef.readlines():

            # WITH EMAIL AND PASSWORD IN SAME FILE
            if re.search(r'^[\,]$', line):

               line = line.strip()
               linevals = line.split(",")

               lnemail = linevals[0]
               lnemail = str(lnemail.strip())
               lnpass = linevals[1]
               lnpass = str(lnpass.strip())
               lnpass = lnpass.replace("\n","")
               if not filter(lambda x: x>'\x7f', lnpass):
                  lnpass = base64.b64decode(lnpass)
               print('using email address: ' + lnemail)

            else:
               lnemail = line.strip()
               print('using email address: ' + lnemail)
               lnpass = getpass.getpass('please enter password for above account --> ')
            atdomain = re.search("@.*", emailaddr).group()
            emaildomain = atdomain[1:]

            imap_server = 'imap.' + emaildomain
            imap_port = 993
            
            if usecolor == 'color':
               print(ac.YELLOW + 'based on email address, using IMAP server: ' + ac.PINKBOLD + imap_server + ac.CLEAR)
            else:
               print('based on email address, using IMAP server: %s') % imap_server
            
            loginok = checklogin(lnemail, lnpass, imap_server, sslcon)
            print(loginok)

            while 'OK' not in loginok:
               lnpass = getpass.getpass('login failure. please check password and enter again --> ')
               loginok = checklogin(lnemail, lnpass, imap_server, sslcon)
               print(loginok)
               if 'OK' in loginok:
                  break
               else:
                  print('login failure. trying next entry..')
                  continue

            efcount += 1

            logging.info('INFO: LOGIN to %s successful' % lnemail)
            getimapmulti(lnemail, lnpass, imap_server, sslcon)

      if efcount > eflen:
         print("all emails and passwords have been processed.")
         sys.exit(0)

# SINGLE EMAIL ADDRESS
else:

   emailaddr = raw_input('please enter email address --> ')

   #VALIDATE EMAIL USING REGEX
   match = re.search(r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,9})$', emailaddr)

   if match:
      if usecolor == 'color':
         print('\033[32m\nemail is valid\033[0m\n')

      else:
         print('email is valid\n')
      
      atdomain = re.search("@.*", emailaddr).group()
      emaildomain = atdomain[1:]

      imap_server = 'imap.' + emaildomain
      imap_port = 993
      
   else:
      tries = 5

      while tries > 0:

         if usecolor == 'color':
            print('\033[31minvalid email format\033[0m\n')
            print('bad attempts: \033[33m' + str(6 - tries) + '\033[0m\n')
            print('\033[36myou have ' + str(tries) + ' attempts remaining.\033[0m\n')

         else:
            print('invalid email format')
            print('bad attempts: ' + str(6 - tries))
            print('you have ' + str(tries) + 'attempts remaining.')

         emailaddr = raw_input('please enter email again --> ')

         if match:
            tries = -1
            break

         else:
            tries = tries - 1

      if tries == 0:
         if usecolor == 'color':
            print('\033[31m too many bad attempts using invalid format! \033[0m\n')
         else:
            print('too many bad attempts using invalid format!')

         logging.info('INFO: too many bad attempts using unproperly formatted email string. aborting program.')
         print('aborting..')
         sys.exit(1)
      
      elif tries == -1:
         if usecolor == 'color':
            print('\n\033[32m email is valid \033[0m')
         else:
            print('email is valid')

      else:
         if usecolor == 'color':
            print('\033[31mERROR: unhandled exception. aborting..\033[0m\n')
         else:
            print('ERROR: unhandled exception. aborting..\n')
         logging.error('ERROR: unhandled exception. aborting program.')
         sys.exit(1)

   # USING PASSWORD LIST
   if usewordlist.lower() == 'y':
   
      pwlistfile = raw_input('please make sure password list is in the script directory, then enter the filename --> ')
      while not os.path.isfile(pwlistfile):
         pwlistfile = raw_input('the path to the word list file you entered is not valid. please check the file and enter again --> ')

      encryptsel = raw_input('is the word list encrypted using encryptlist.py? Y/N --> ')      
      while not re.search(r'^[nNyY]$', encryptsel):
         encryptsel = raw_input('invalid selection. enter Y if word list was encrypted using encryptlist.py or N if not encrypted --> ')
      
      # IF PASSWORD LIST NOT ENCRYPTED  
      if encryptsel.lower() == 'n':
      
         b64sel = raw_input('is the word list base64-encoded using encodelist.py? Y/N --> ')
         while not re.search(r'^[nNyY]$', b64sel):
            b64sel = raw_input('invalid selection. enter Y if word list is base64-encoded or N if plain text --> ')

         if b64sel.lower() == 'n':         
            gotoencsel = raw_input('storing passwords in plaintext is a security risk. \nenter 1 to encrypt the contents of your password list. \nenter 2 to use base-64 encoding. enter 3 to continue with a plaintext password list. --> ')
            while not re.search(r'^[1-3]$', gotoencsel):
               gotoencsel = raw_input('invalid selection. enter 1 to run script to encrypt your password list. \nenter 2 to base64-encode it. or enter 3 to continue with plaintext list --> ')
            if gotoencsel == '1':
               print("launching encryptlist.py..")
               os.system('chmod +x encryptlist.py')
               os.system('python encryptlist.py')
            elif gotoencsel == '2':
               print("launching encodelist.py..")
               os.system('chmod +x encodelist.py')
               os.system('python encodelist.py')
            else:
               print('*** to encrypt your list in the future, run \'python encryptlist.py\'. to  base64-encode your list in the future, run \'python encodelist.py\' ***')
      
      # USING ENCRYPTED LIST  
      else:
         secretkey = 'secret.key'
         if os.path.isfile('secret.key'):
            if usecolor == 'color':
               print('base64-encoded key generated by encryptlist.py found at ' + ac.GREEN + 'secret.key' + ac.CLEAR + '.')
            else:
               print('base64-encoded key generated by encryptlist.py found at secret.key.')
            keycheck = raw_input('press ENTER to use secret.key or enter the filename of your encryption key --> ')
            if len(keycheck) > 1:
               while not os.path.isfile(keycheck):
                  keycheck = raw_input('file not found. please check the filename and enter again --> ')
               secretkey = keycheck
            else:
               secretkey = 'secret.key'
         
         else:
            secretkey = raw_input('secret.key not found. please enter the filename of your encryption key --> ')
            while not os.path.isfile(secretkey):
               secretkey = raw_input('file not found. please check filename and enter again --> ')

         encpass = getpass.getpass('please enter the secret passphrase used to generate the encrypted file --> ')
         AES_Dec = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip('&')
         cryptfile = open(secretkey, 'r')
         a = cryptfile.readline()
         cryptkey = base64.b64decode(a)
         cryptfile.close()

         secretpadlen = 16 - (len(encpass) % 16)
         secret = encpass + ('&' * secretpadlen)
         cipher = AES.new(cryptkey, AES.MODE_CBC, secret)
         print('using encryption key: ')
         if usecolor == 'color':
            print(ac.ORANGE + a + ac.CLEAR)
         else:
            print(a)
      
      print("\nusing word list: ")
      if usecolor == 'color':
         print(ac.OKAQUA + pwlistfile + ac.CLEAR)
      else:
         print(pwlistfile)
      
      pf = open(pwlistfile, "r+")
      wordlist = pf.readlines()
      listlen = len(wordlist)

      count = 0

      for emailpass in wordlist:
      
         if encryptsel.lower() == 'y':
            emailpass = AES_Dec(cipher, emailpass)

         elif b64sel.lower() == 'y':
            emailpass = base64.b64decode(emailpass)
                              
         emailpass = emailpass.strip()
         emailpass = emailpass.replace("\n","")
         emailpass = str(emailpass)
         loginok = checklogin(emailaddr, emailpass, imap_server, sslcon)
         count += 1
         
         # WRONG PASSWORD
         if 'AUTHEN' in loginok:
            print("Wrong login credentials supplied for %s. Skipping to next password..." % emailaddr)
            logging.info('INFO: invalid password for %s. skipping to next password.' % emailaddr)
            continue

         # PASSWORD NOT CORRECTLY FORMATTED
         elif 'BAD' in loginok:
            emailpass = emailpass.strip()
            print("password format error. trying again..\n")
            loginok = checklogin(emailaddr, emailpass, imap_server, sslcon)
            loginok = str(loginok)
            if 'OK' in loginok:
               logging.info('INFO: LOGIN to %s successful' % emailaddr)
               getimapmulti(emailaddr, emailpass, imap_server, sslcon)
               print("inbox contents have been saved to file for email: " + ac.OKAQUA + emailaddr + ac.CLEAR)
               count = 100
            continue

         if 'OK' not in loginok and count <= listlen:
            #print('tried: %s') % str(lnpass)
            if usecolor == 'color':
               print('\n\033[31mLOGIN FAILED. \033[34;1mtrying next entry...\033[0m\n')
               print('\033[33mtries: \033[35m' + str(count) + '\033[33m out of \033[35m %s \033[0m' % str(listlen))
            else:
               print('\nLOGIN FAILED. trying next entry...\n')
               print('tries: ' + str(count) + ' out of ' + str(listlen))
            print('\n')
            continue

         else:
            logging.info('INFO: LOGIN to %s successful!' % emailaddr)
            getimapmulti(emailaddr, emailpass.strip(), imap_server, sslcon)
            count = 100
            homedir = os.path.expanduser("~")
            rootdir = os.path.join(homedir, 'email-output')
            print("inbox contents saved to directory: %s" % rootdir)
            print("\nexiting program..\n")
            sys.exit(0)
            break

      if count >= listlen and count < 100:
         if usecolor == 'color':
            print('\n\033[35mexhausted all entries in password list for:\033[33m %s.\n\033[0m' % emailaddr)
         else:
            print('\nexhausted all entries in password list for %s.\n' % emailaddr)
         print('exiting program..\n')
         sys.exit(1)

   else:

      emailpass = getpass.getpass('please enter password --> ')
      getimap(emailaddr, emailpass, imap_server, sslcon)

print("thanks for using EMAIL2FILE! \nexiting program..\n")
sys.exit(0)
