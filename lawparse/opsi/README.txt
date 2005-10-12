lawparse - turns UK Acts and Satutory Instruments into XML
==========================================================

OPSI Scripts
------------

fulldepage.py - download HTML of acts, top and tail and concatenate
sidepage.py   - as fulldepage.py, but for Statutory Instruments
actparse.py   - parses acts from HTML into XML files
parsetest.py  - parses every act that has already been parsed

OPSI Modules
------------

analyser.py   - bulk of the act parsing engine
parsefun.py   - utility functions for parser
parsehead.py  - parsing of the head of acts
patches.py    - special patches to particular acts

General Modules
---------------

legis.py      - law object model, stores logical structure of act, emits XML
miscfun.py    - where files are kept


