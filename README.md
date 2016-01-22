smtpd-dual-delivery.py
=====
SMTP dual delivery relay (proxy) daemon.
Receive 1 message and deliver that to two different smtp servers, useful for testing two different mail backends.

smtpd-snoop-delivery.py
=====
SMTP relay (proxy) daemon with the ability to save all passing email into eml files, quite useful for debugging or snooping :)


Warning
=====

No queueing is implemented mail might get lost if one of the receiving servers is not handling the mail correctly.
