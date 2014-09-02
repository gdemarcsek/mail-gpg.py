#!/usr/bin/env python
#encoding: utf-8

# gpgmail - Send GnuPG encrypted and signed e-mails
# Copyright (C) 2014 György Demarcsek
# License: MIT

import getpass
import sys
import argparse

try:
  import gnupg
except ImportError:
  print("Error importing gnupg: python-gnupg is required to use this tool")
  print("You can download it from here: https://pythonhosted.org/python-gnupg/ or try pip install python-gnupg")
  print("Also, for most implementations, GnuPG must be installed on your computer")
  sys.exit(1)

try:
  import smtplib
except ImportError:
  print("Error importing smtplib: install a newer version of Python")
  sys.exit(2)

class FingerprintError(Exception):
  pass

def prompt(prompt):
  return raw_input(prompt).strip()

banner = ["gpgmail - Send encrypted and signed e-mails\n",
          "Copyright (C) György Demarcsek 2014\n"]

sys.stdout.writelines(banner)

parser = argparse.ArgumentParser()

parser.add_argument('--server', type=str,
                    help="SMTP server address or hostname",
                    default='smtp.gmail.com')
parser.add_argument('--port', type=int,
                    help="SMTP server port", default=587)
parser.add_argument('--ssl', action='store_true', help='Connect via SSL')
parser.add_argument('--sign', action='store_true', help='Sign the message')
parser.add_argument('--verbose', action='store_true',
                    help='Verbose output e.g. for debugging')

args = parser.parse_args()

print "Sending mail via %s:%d" % (args.server, args.port)
fromaddr = prompt("Message From: ")
sys.stdout.write("Mailbox ")
sys.stdout.flush()
password = getpass.getpass()
toaddrs  = prompt("Message To: ").split()

print "Enter message, end with ^D (Unix) or ^Z (Windows):"

# Add the From: and To: headers at the start!
msg = ("From: %s\r\nTo: %s\r\n\r\n"
       % (fromaddr, ", ".join(toaddrs)))
while 1:
    try:
        line = raw_input()
    except EOFError:
        break
    if not line:
        break
    msg = msg + line

print "Message length is " + repr(len(msg))

try:
  gpg = gnupg.GPG(verbose=args.verbose)
except ValueError:
  sys.stdout("GnuPG executable cannot be found in $PATH")
  sys.exit(15)

try:
  gpg.encoding = 'utf-8'
  public_keys = gpg.list_keys()
  recipent_fingerprints = []
  sender_fingerprint = None

  for key in public_keys:
    curr_fp = key['fingerprint']
    for uid in key['uids']:
      if fromaddr == uid.split()[-1][1:-1]:
        sender_fingerprint = curr_fp
      for recipent in toaddrs:
        if recipent == uid.split()[-1][1:-1]:
          recipent_fingerprints.append(curr_fp)

  if sender_fingerprint is None or len(recipent_fingerprints) == 0:
    raise FingerprintError

  keyring_pass = None
  if args.sign:
    sys.stdout.write("Keyring ")
    sys.stdout.flush()
    keyring_pass = getpass.getpass()

  sign_message = False
  if args.sign:
    sign_message = sender_fingerprint

  msg = str(gpg.encrypt(msg, recipent_fingerprints, sign=sign_message, passphrase=keyring_pass))

  server = smtplib.SMTP(args.server, args.port)
  server.set_debuglevel(1 if args.verbose else 0)
  server.ehlo()
  if args.ssl:
    server.starttls()
  server.ehlo()
  server.login(fromaddr, password)
  password = ""
  server.sendmail(fromaddr, toaddrs, msg)
  server.quit()

except FingerprintError:
  print("Sender or recipent fingerprint could not be found in local keychain/trustdb")
  sys.exit(3)
except SMTPConnectError:
  print("Unable to establish SMTP connection")
  sys.exit(4)
except SMTPHeloError:
  print("The server didn’t reply properly to the HELO greeting")
  sys.exit(5)
except SMTPAuthenticationError:
  print("The server didn’t accept the username/password combination")
  sys.exit(6)
except SMTPSenderRefused:
  print("The server didn’t accept the sender's address")
  sys.exit(7)
except SMTPResponseException:
  print("Invalid response")
  sys.exit(8)
except SMTPRecipientsRefused:
  print("Invalid recipent address")
  sys.exit(9)
except SMTPDataError:
  print("The server replied with an unexpected error code (other than a refusal of a recipient)")
  sys.exit(10)
except SMTPException:
  print("The server does not support the STARTTLS extension or no suitable authentication method was found")
  sys.exit(11)
except RuntimeError:
  print("SSL/TLS support is not available to your Python interpreter")
  sys.exit(12)
except:
  print("Unexpected error: %s" % sys.exc_info()[0])
  sys.exit(13)

print("Message sent")
sys.exit(0)
