<? xml version="1.0" encoding="utf-8" ?>
<?php
/*************************************************************************************
 * Author: Muthu Annamalai (muthuspost@gmail.com)
 * Copyright: (c) 2013 Muthu Annamalai
 * 
 * Derived from the file, python.php from GenSHi
 * ----------------------------------
 * Ref: http://sourceforge.net/p/geshi/code/2590/tree/branches/RELEASE_1_0_X_STABLE/geshi-1.0.X/src/geshi/python.php
 * Author: Roberto Rossi (rsoftware@altervista.org)
 * Copyright: (c) 2004 Roberto Rossi (http://rsoftware.altervista.org), Nigel McNie (http://qbnz.com/highlighter)
 * Release Version: 1.0.8.11
 * Date Started: 2004/08/30
 *
 * Ezhil language file for GeSHi.
 *
 *
 *************************************************************************************
 *
 *     This file is part of GeSHi.
 *
 *   GeSHi is free software; you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation; either version 2 of the License, or
 *   (at your option) any later version.
 *
 *   GeSHi is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with GeSHi; if not, write to the Free Software
 *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 ************************************************************************************/

$language_data = array (
    'LANG_NAME' => 'Ezhil',
    'COMMENT_SINGLE' => array(1 => '#'),
    'COMMENT_MULTI' => array(),
    'CASE_KEYWORDS' => GESHI_CAPS_NO_CHANGE,
    //Longest quotemarks ALWAYS first
    'QUOTEMARKS' => array('"""', "'''", '"', "'"),
    'ESCAPE_CHAR' => '\\',
    'NUMBERS' =>
        GESHI_NUMBER_INT_BASIC | GESHI_NUMBER_BIN_PREFIX_0B |
        GESHI_NUMBER_OCT_PREFIX_0O | GESHI_NUMBER_HEX_PREFIX |
        GESHI_NUMBER_FLT_NONSCI | GESHI_NUMBER_FLT_NONSCI_F |
        GESHI_NUMBER_FLT_SCI_SHORT | GESHI_NUMBER_FLT_SCI_ZERO,
    'KEYWORDS' => array(

        /*
        ** Set 1: reserved words
        ** 
        */
        1 => array(
		    'ஆனால்', 'ஏதேனில்', 'தேர்வு', 'பதிப்பி', 'தேர்ந்தெடு', 'இல்லைஆனால்', 'ஆக', 'இல்லை',
			'வரை', 'செய்', 'பின்கொடு', 'முடியேனில்', 'முடி', 'நிரல்பாகம்', 'தொடர்', 'நிறுத்து', 'இல்',
			'ஒவ்வொன்றாக',
            ),

        /*
        ** Set 2: builtins
        ** 
        */
        2 => array(
           'float', 'int', 'string','None', 'True', 'False','abs',
		   'acos', 'len', 'assert', 'seed', 'exit', 'randint', 'choice', 'random'
            ),

        /*
        ** Set 3: standard library
        ** http://python.org/doc/current/lib/modindex.html
        */
        3 => array(            
            ),

        /*
        ** Set 4: special methods
        ** http://python.org/doc/current/ref/specialnames.html
        */
        4 => array(            
            )
        ),
    'SYMBOLS' => array(
        '<', '>', '=', '!', '<=', '>=',             //·comparison·operators
        '~', '@',                                   //·unary·operators
        ';', ','                                    //·statement·separator
        ),
    'CASE_SENSITIVE' => array(
        GESHI_COMMENTS => false,
        1 => true,
        2 => true,
        3 => true,
        4 => true
        ),
    'STYLES' => array(
        'KEYWORDS' => array(
            1 => 'color: #ff7700;font-weight:bold;',    // Reserved
            2 => 'color: #008000;',                        // Built-ins + self
            3 => 'color: #dc143c;',                        // Standard lib
            4 => 'color: #0000cd;'                        // Special methods
            ),
        'COMMENTS' => array(
            1 => 'color: #808080; font-style: italic;',
            'MULTI' => 'color: #808080; font-style: italic;'
            ),
        'ESCAPE_CHAR' => array(
            0 => 'color: #000099; font-weight: bold;'
            ),
        'BRACKETS' => array(
            0 => 'color: black;'
            ),
        'STRINGS' => array(
            0 => 'color: #483d8b;'
            ),
        'NUMBERS' => array(
            0 => 'color: #ff4500;'
            ),
        'METHODS' => array(
            1 => 'color: black;'
            ),
        'SYMBOLS' => array(
            0 => 'color: #66cc66;'
            ),
        'REGEXPS' => array(
            ),
        'SCRIPT' => array(
            )
        ),
    'URLS' => array(
        1 => '',
        2 => '',
        3 => '',
        4 => ''
        ),
    'OOLANG' => true,
    'OBJECT_SPLITTERS' => array(
        1 => '.'
        ),
    'REGEXPS' => array(
        ),
    'STRICT_MODE_APPLIES' => GESHI_NEVER,
    'SCRIPT_DELIMITERS' => array(
        ),
    'HIGHLIGHT_STRICT_BLOCK' => array(
        )
);

?>