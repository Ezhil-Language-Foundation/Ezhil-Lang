##This Python file uses the following encoding: utf-8
##
# (C) 2007, 2008 Muthiah Annamalai <gnumuthu@user.sf.net>
## Licensed under GPL Version 3

from curses.ascii import *
import codecs 
import unicodedata

## constants
TA_ACCENT_LEN = 13 #12 + 1
TA_AYUDHA_LEN = 1
TA_UYIR_LEN = 12
TA_MEI_LEN = 18
TA_AGARAM_LEN = 18
TA_SANSKRIT_LEN = 4
TA_UYIRMEI_LEN = 216 # 18*12

# List of letters you can use
uyir_letters = [u"அ",u"ஆ",u"இ", 
	u"ஈ",u"உ",u"ஊ",u"எ",u"ஏ",u"ஐ",u"ஒ",u"ஓ",u"ஔ"]

ayudha_letter = u"ஃ"

mei_letters = [u"க்",u"ச்",u"ட்",u"த்",u"ப்",u"ற்",
                                       u"ஞ்",u"ங்",u"ண்",u"ந்",u"ம்",u"ன்",
                                        u"ய்",u"ர்",u"ல்",u"வ்",u"ழ்",u"ள்" ]

accent_symbols = [u"",u"ா",u"ி",u"ீ",u"ு",u"ூ",
			u"ெ",u"ே",u"ை",u"ொ",u"ோ",u"ௌ",u"ஃ"]

agaram_letters = [u"க",u"ச",u"ட",u"த",u"ப",u"ற",
		     u"ஞ",u"ங",u"ண",u"ந",u"ம",u"ன",
		     u"ய",u"ர",u"ல",u"வ",u"ழ",u"ள"]

sanskrit_letters = [u"ஜ",u"ஷ", u"ஸ",u"ஹ"]
sanskrit_mei_letters =[u"ஜ்",u"ஷ்", u"ஸ்",u"ஹ்"]

uyirmei_letters = [
 u"க"  ,u"கா"  ,u"கி"  ,u"கீ"  ,u"கு"  ,u"கூ"  ,u"கெ"  ,u"கே"  ,u"கை"  ,u"கொ"  ,u"கோ"  ,u"கௌ"  ,
u"ச"  ,u"சா"  ,u"சி"  ,u"சீ"  ,u"சு"  ,u"சூ"  ,u"செ"  ,u"சே"  ,u"சை"  ,u"சொ"  ,u"சோ"  ,u"சௌ" , 
 u"ட"  ,u"டா"  ,u"டி"  ,u"டீ"  ,u"டு"  ,u"டூ"  ,u"டெ"  ,u"டே"  ,u"டை"  ,u"டொ"  ,u"டோ"  ,u"டௌ", 
u"த"  ,u"தா"  ,u"தி"  ,u"தீ"  ,u"து"  ,u"தூ"  ,u"தெ"  ,u"தே"  ,u"தை"  ,u"தொ"  ,u"தோ"  ,u"தௌ", 
u"ப"  ,u"பா"  ,u"பி"  ,u"பீ"  ,u"பு"  ,u"பூ"  ,u"பெ"  ,u"பே"  ,u"பை"  ,u"பொ"  ,u"போ"  ,u"பௌ" , 
u"ற"  ,u"றா"  ,u"றி"  ,u"றீ"  ,u"று"  ,u"றூ"  ,u"றெ"  ,u"றே"  ,u"றை"  ,u"றொ"  ,u"றோ"  ,u"றௌ", 
u"ஞ"  ,u"ஞா"  ,u"ஞி"  ,u"ஞீ"  ,u"ஞு"  ,u"ஞூ"  ,u"ஞெ"  ,u"ஞே"  ,u"ஞை"  ,u"ஞொ"  ,u"ஞோ"  ,u"ஞௌ"  ,
u"ங"  ,u"ஙா"  ,u"ஙி"  ,u"ஙீ"  ,u"ஙு"  ,u"ஙூ"  ,u"ஙெ"  ,u"ஙே"  ,u"ஙை"  ,u"ஙொ"  ,u"ஙோ"  ,u"ஙௌ"  ,
u"ண"  ,u"ணா"  ,u"ணி"  ,u"ணீ"  ,u"ணு"  ,u"ணூ"  ,u"ணெ"  ,u"ணே"  ,u"ணை"  ,u"ணொ"  ,u"ணோ"  ,u"ணௌ"  ,
u"ந"  ,u"நா"  ,u"நி"  ,u"நீ"  ,u"நு"  ,u"நூ"  ,u"நெ"  ,u"நே"  ,u"நை"  ,u"நொ"  ,u"நோ"  ,u"நௌ"  ,
u"ம"  ,u"மா"  ,u"மி"  ,u"மீ"  ,u"மு"  ,u"மூ"  ,u"மெ"  ,u"மே"  ,u"மை"  ,u"மொ"  ,u"மோ"  ,u"மௌ" , 
u"ன"  ,u"னா"  ,u"னி"  ,u"னீ"  ,u"னு"  ,u"னூ"  ,u"னெ"  ,u"னே"  ,u"னை"  ,u"னொ"  ,u"னோ"  ,u"னௌ", 
u"ய"  ,u"யா"  ,u"யி"  ,u"யீ"  ,u"யு"  ,u"யூ"  ,u"யெ"  ,u"யே"  ,u"யை"  ,u"யொ"  ,u"யோ"  ,u"யௌ", 
u"ர"  ,u"ரா"  ,u"ரி"  ,u"ரீ"  ,u"ரு"  ,u"ரூ"  ,u"ரெ"  ,u"ரே"  ,u"ரை"  ,u"ரொ"  ,u"ரோ"  ,u"ரௌ", 
u"ல"  ,u"லா"  ,u"லி"  ,u"லீ"  ,u"லு"  ,u"லூ"  ,u"லெ"  ,u"லே"  ,u"லை"  ,u"லொ"  ,u"லோ"  ,u"லௌ" , 
u"வ"  ,u"வா"  ,u"வி"  ,u"வீ"  ,u"வு"  ,u"வூ"  ,u"வெ"  ,u"வே"  ,u"வை"  ,u"வொ"  ,u"வோ"  ,u"வௌ" , 
u"ழ"  ,u"ழா"  ,u"ழி"  ,u"ழீ"  ,u"ழு"  ,u"ழூ"  ,u"ழெ"  ,u"ழே"  ,u"ழை"  ,u"ழொ"  ,u"ழோ"  ,u"ழௌ" , 
u"ள"  ,u"ளா"  ,u"ளி"  ,u"ளீ"  ,u"ளு"  ,u"ளூ"  ,u"ளெ"  ,u"ளே"  ,u"ளை"  ,u"ளொ"  ,u"ளோ"  ,u"ளௌ" ]

## total tamil letters in use, including sanskrit letters
tamil_letters = [
	
## /* Uyir */
u"அ",u"ஆ",u"இ", u"ஈ",u"உ",u"ஊ",u"எ",u"ஏ",u"ஐ",u"ஒ",u"ஓ",u"ஔ",

##/* Ayuda Ezhuthu */
u"ஃ",
	
## /* Mei */	
 u"க்",u"ச்",u"ட்",u"த்",u"ப்",u"ற்",u"ஞ்",u"ங்",u"ண்",u"ந்",u"ம்",u"ன்",u"ய்",u"ர்",u"ல்",u"வ்",u"ழ்",u"ள்",

## /* Agaram */
u"க",u"ச",u"ட",u"த",u"ப",u"ற",u"ஞ",u"ங",u"ண",u"ந",u"ம",u"ன",u"ய",u"ர",u"ல",u"வ",u"ழ",u"ள",
	
## /* Sanskrit (Vada Mozhi) */
u"ஜ",u"ஷ", u"ஸ",u"ஹ",

##/* Sanskrit (Mei) */
u"ஜ்",u"ஷ்", u"ஸ்",u"ஹ்",
	
## /* Uyir Mei */
 u"க"  ,u"கா"  ,u"கி"  ,u"கீ"  ,u"கு"  ,u"கூ"  ,u"கெ"  ,u"கே"  ,u"கை"  ,u"கொ"  ,u"கோ"  ,u"கௌ" 
 ,u"ச"  ,u"சா"  ,u"சி"  ,u"சீ"  ,u"சு"  ,u"சூ"  ,u"செ"  ,u"சே"  ,u"சை"  ,u"சொ"  ,u"சோ"  ,u"சௌ" 
 ,u"ட"  ,u"டா"  ,u"டி"  ,u"டீ"  ,u"டு"  ,u"டூ"  ,u"டெ"  ,u"டே"  ,u"டை"  ,u"டொ"  ,u"டோ"  ,u"டௌ" 
 ,u"த"  ,u"தா"  ,u"தி"  ,u"தீ"  ,u"து"  ,u"தூ"  ,u"தெ"  ,u"தே"  ,u"தை"  ,u"தொ"  ,u"தோ"  ,u"தௌ" 
 ,u"ப"  ,u"பா"  ,u"பி"  ,u"பீ"  ,u"பு"  ,u"பூ"  ,u"பெ"  ,u"பே"  ,u"பை"  ,u"பொ"  ,u"போ"  ,u"பௌ" 
 ,u"ற"  ,u"றா"  ,u"றி"  ,u"றீ"  ,u"று"  ,u"றூ"  ,u"றெ"  ,u"றே"  ,u"றை"  ,u"றொ"  ,u"றோ"  ,u"றௌ" 
 ,u"ஞ"  ,u"ஞா"  ,u"ஞி"  ,u"ஞீ"  ,u"ஞு"  ,u"ஞூ"  ,u"ஞெ"  ,u"ஞே"  ,u"ஞை"  ,u"ஞொ"  ,u"ஞோ"  ,u"ஞௌ" 
 ,u"ங"  ,u"ஙா"  ,u"ஙி"  ,u"ஙீ"  ,u"ஙு"  ,u"ஙூ"  ,u"ஙெ"  ,u"ஙே"  ,u"ஙை"  ,u"ஙொ"  ,u"ஙோ"  ,u"ஙௌ" 
 ,u"ண"  ,u"ணா"  ,u"ணி"  ,u"ணீ"  ,u"ணு"  ,u"ணூ"  ,u"ணெ"  ,u"ணே"  ,u"ணை"  ,u"ணொ"  ,u"ணோ"  ,u"ணௌ" 
 ,u"ந"  ,u"நா"  ,u"நி"  ,u"நீ"  ,u"நு"  ,u"நூ"  ,u"நெ"  ,u"நே"  ,u"நை"  ,u"நொ"  ,u"நோ"  ,u"நௌ" 
 ,u"ம"  ,u"மா"  ,u"மி"  ,u"மீ"  ,u"மு"  ,u"மூ"  ,u"மெ"  ,u"மே"  ,u"மை"  ,u"மொ"  ,u"மோ"  ,u"மௌ" 
 ,u"ன"  ,u"னா"  ,u"னி"  ,u"னீ"  ,u"னு"  ,u"னூ"  ,u"னெ"  ,u"னே"  ,u"னை"  ,u"னொ"  ,u"னோ"  ,u"னௌ" 
 ,u"ய"  ,u"யா"  ,u"யி"  ,u"யீ"  ,u"யு"  ,u"யூ"  ,u"யெ"  ,u"யே"  ,u"யை"  ,u"யொ"  ,u"யோ"  ,u"யௌ" 
 ,u"ர"  ,u"ரா"  ,u"ரி"  ,u"ரீ"  ,u"ரு"  ,u"ரூ"  ,u"ரெ"  ,u"ரே"  ,u"ரை"  ,u"ரொ"  ,u"ரோ"  ,u"ரௌ" 
 ,u"ல"  ,u"லா"  ,u"லி"  ,u"லீ"  ,u"லு"  ,u"லூ"  ,u"லெ"  ,u"லே"  ,u"லை"  ,u"லொ"  ,u"லோ"  ,u"லௌ" 
 ,u"வ"  ,u"வா"  ,u"வி"  ,u"வீ"  ,u"வு"  ,u"வூ"  ,u"வெ"  ,u"வே"  ,u"வை"  ,u"வொ"  ,u"வோ"  ,u"வௌ" 
 ,u"ழ"  ,u"ழா"  ,u"ழி"  ,u"ழீ"  ,u"ழு"  ,u"ழூ"  ,u"ழெ"  ,u"ழே"  ,u"ழை"  ,u"ழொ"  ,u"ழோ"  ,u"ழௌ" 
 ,u"ள"  ,u"ளா"  ,u"ளி"  ,u"ளீ"  ,u"ளு"  ,u"ளூ"  ,u"ளெ"  ,u"ளே"  ,u"ளை"  ,u"ளொ"  ,u"ளோ"  ,u"ளௌ" 
 
 ##/* Sanskrit Uyir-Mei */
  ,u"ஜ"  ,u"ஜா"  ,u"ஜி"  ,u"ஜீ"  ,u"ஜு"  ,u"ஜூ"  ,u"ஜெ"  ,u"ஜே"  ,u"ஜை"  ,u"ஜொ"  ,u"ஜோ"  ,u"ஜௌ" 
 ,u"ஷ"  ,u"ஷா"  ,u"ஷி"  ,u"ஷீ"  ,u"ஷு"  ,u"ஷூ"  ,u"ஷெ"  ,u"ஷே"  ,u"ஷை"  ,u"ஷொ"  ,u"ஷோ"  ,u"ஷௌ" 
 ,u"ஸ"  ,u"ஸா"  ,u"ஸி"  ,u"ஸீ"  ,u"ஸு"  ,u"ஸூ"  ,u"ஸெ"  ,u"ஸே"  ,u"ஸை"  ,u"ஸொ"  ,u"ஸோ"  ,u"ஸௌ" 
 ,u"ஹ"  ,u"ஹா"  ,u"ஹி"  ,u"ஹீ"  ,u"ஹு"  ,u"ஹூ"  ,u"ஹெ"  ,u"ஹே"  ,u"ஹை"  ,u"ஹொ"  ,u"ஹோ"  ,u"ஹௌ" ]

## some assertions, languages dont change fast.
assert ( TA_ACCENT_LEN == len(accent_symbols) )
assert ( TA_AYUDHA_LEN == 1 )
assert ( TA_UYIR_LEN == len( uyir_letters ) )
assert ( TA_MEI_LEN == len( mei_letters ) )
assert ( TA_AGARAM_LEN == len( agaram_letters ) )
assert ( TA_SANSKRIT_LEN == len( sanskrit_letters )) 
assert ( TA_UYIRMEI_LEN == len( uyirmei_letters ) )

## length of the definitions
def accent_len( ):
        return TA_ACCENT_LEN ## 13 = 12 + 1

def ayudha_len( ):
        return TA_AYUDHA_LEN ## 1 

def uyir_len( ):
        return TA_UYIR_LEN ##12

def mei_len( ):
        return TA_MEI_LEN ##18

def agaram_len( ):
        return TA_AGARAM_LEN ##18

def uyirmei_len( ):
        return TA_UYIRMEI_LEN ##216

def tamil_len( ):
        return len();

## access the letters
def uyir( idx ):
        assert ( idx >= 0 and idx < uyir_len() )
        return uyir_letters[idx]

def agaram( idx ):
       assert ( idx >= 0 and idx < agaram_len() )
       return agaram_letters[idx]

def mei( idx ):
       assert ( idx >= 0 and idx < mei_len() )
       return mei_letters[idx]

def uyirmei( idx ):
       assert( idx >= 0 and idx < uyirmei_len() )
       return uyirmei_letters[idx]

def uyirmei( mei_idx, uyir_idx):
       idx = mei_idx; idy = uyir_idx;
       assert ( idy >= 0 and idy < uyir_len() )
       assert ( idx >= 0 and idx < mei_len() )
       return agaram_letters[mei_idx]+accent_symbols[uyir_idx]

def tamil( idx ):
        assert ( idx >= 0 and idx < tamil_len() )
        return tamil_letters[idx]

## useful part of the API:
def istamil_prefix( word ):
        """ check if the given word has a tamil prefix. Returns
        either a True/False flag """
        if ( isalpha(word) ): return False
        for letters in tamil_letters:
                if ( word.find(letters) == 0 ):
                        return True
        return False

def has_tamil( word ):
        """check if the word has any occurance of any tamil letter """
        for letters in tamil_letters:
                if ( word.find(letters) >= 0 ):
                        return True
        return False

def istamil ( tchar ):
        """ check if the letter tchar is prefix of 
        any of tamil-letter. It suggests we have a tamil identifier"""
        if ( isalpha(tchar) ): return False
        for letters in tamil_letters:
                if ( letters.find( tchar ) == 0 ):
                        return True
        return False

def istamil_alnum( tchar ):
        """ check if the character is alphanumeric, or tamil.
        This saves time from running through istamil() check. """
        if ( isalnum( tchar ) ):
                return True
        if ( istamil( tchar ) ):
                return True
        return False

##
## hard problems are to split a tamil-character stream into
## tamil characters (individuals).
##
def get_letters( word ):
        """ splits the word into a character-list of tamil/english
        characters present in the stream """
        raise Exception("Not Implemented")

## get a list of Tamil letters in one string
def getall_Tamil_letters():
        #print u"".join(uyirmei_letters+uyir_letters+mei_letters+[ayudha_letter]+agaram_letters+sanskrit_letters)
        #return
        return u"".join(uyirmei_letters+agaram_letters+sanskrit_letters+sanskrit_mei_letters+mei_letters+[ayudha_letter]+uyir_letters)

if __name__ == '__main__':
    print getall_Tamil_letters()
