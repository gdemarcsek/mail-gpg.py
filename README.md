mail-gpg.py
===========

Send GnuPG encrypted e-mails from the command line

A dead simple Python script that can be used to send GnuPG encrypted e-mails.
E-mail attachments are not supported yet. Tested on Mac OS X 10.9.4.

Usage:

gpgmail - Send encrypted and signed e-mails  
Copyright (C) György Demarcsek 2014  
usage: mail-gpg.py [-h] [--server SERVER] [--port PORT] [--ssl] [--sign]  
                   [--verbose]  

optional arguments:  
  -h, --help       show this help message and exit  
  --server SERVER  SMTP server address or hostname  
  --port PORT      SMTP server port  
  --ssl            Connect via SSL  
  --sign           Sign the message  
  --verbose        Verbose output e.g. for debugging  
