#!/usr/bin/python
# -*- coding: latin1 -*-

# !!!!!!  Shared with web2 !!!!!!!

# something else which might do this:
#import unicodedata
#return unicodedata.normalize('NFKD', unicode(string)).encode('ASCII', 'ignore')

# utility I wish was in the library
# is there a more efficient char substitution system?
def DownAscii(st):
    st = st.replace("�", "a")
    st = st.replace("�", "a")
    st = st.replace("�", "a")
    st = st.replace("�", "a")
    st = st.replace("�", "a")
    st = st.replace("�", "a")
    st = st.replace("�", "A")
    st = st.replace("�", "c")
    st = st.replace("�", "e")
    st = st.replace("�", "e")
    st = st.replace("�", "e")
    st = st.replace("�", "e")
    st = st.replace("�", "i")
    st = st.replace("�", "i")
    st = st.replace("�", "i")
    st = st.replace("�", "i")
    st = st.replace("�", "o")
    st = st.replace("�", "o")
    st = st.replace("�", "o")
    st = st.replace("�", "o")
    st = st.replace("�", "o")
    st = st.replace("�", "o")
    st = st.replace("�", "o")
    st = st.replace("�", "u")
    st = st.replace("�", "u")
    st = st.replace("�", "u")
    st = st.replace("�", "u")
    st = st.replace("�", "n")
    st = st.replace("�", "y")
    st = st.replace("�", "ae")
    st = st.replace("�", "c")

    st = st.replace("�", "e")
    st = st.replace("�", "c")
    st = st.replace("�", "a")
    st = st.replace("�", "ae")
    st = st.replace("�", "o")
    st = st.replace("�", "i")
    st = st.replace("�", "o")
    st = st.replace("�", "i")
    st = st.replace("�", "i")

    st = st.replace("�", "")
    st = st.replace("�", "")
    st = st.replace("�", "")
    st = st.replace("�", "")

    st = st.replace("�", "i")

    return st
# Anal
# Anal
