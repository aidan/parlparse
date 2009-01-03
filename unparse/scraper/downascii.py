#!/usr/bin/python
# -*- coding: latin1 -*-

# !!!!!!  Shared with web2 !!!!!!!

# something else which might do this:
#import unicodedata
#return unicodedata.normalize('NFKD', unicode(string)).encode('ASCII', 'ignore')

# utility I wish was in the library
# is there a more efficient char substitution system?
def DownAscii(st):
    st = st.replace("à", "a")
    st = st.replace("á", "a")
    st = st.replace("â", "a")
    st = st.replace("ã", "a")
    st = st.replace("ä", "a")
    st = st.replace("å", "a")
    st = st.replace("Ü", "A")
    st = st.replace("ç", "c")
    st = st.replace("é", "e")
    st = st.replace("ë", "e")
    st = st.replace("ê", "e")
    st = st.replace("è", "e")
    st = st.replace("ï", "i")
    st = st.replace("í", "i")
    st = st.replace("î", "i")
    st = st.replace("ì", "i")
    st = st.replace("ô", "o")
    st = st.replace("ö", "o")
    st = st.replace("ó", "o")
    st = st.replace("õ", "o")
    st = st.replace("ø", "o")
    st = st.replace("ò", "o")
    st = st.replace("ð", "o")
    st = st.replace("ú", "u")
    st = st.replace("ü", "u")
    st = st.replace("ù", "u")
    st = st.replace("û", "u")
    st = st.replace("ñ", "n")
    st = st.replace("ý", "y")
    st = st.replace("æ", "ae")
    st = st.replace("¢", "c")

    st = st.replace("É", "e")
    st = st.replace("Ç", "c")
    st = st.replace("Á", "a")
    st = st.replace("Æ", "ae")
    st = st.replace("Ö", "o")
    st = st.replace("Ï", "i")
    st = st.replace("Ó", "o")
    st = st.replace("Î", "i")
    st = st.replace("Í", "i")

    st = st.replace("°", "")
    st = st.replace("¸", "")
    st = st.replace("¯", "")
    st = st.replace("´", "")

    st = st.replace("Í", "i")

    return st
# Anal
# Anal
