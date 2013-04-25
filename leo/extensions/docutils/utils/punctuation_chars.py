#!/usr/bin/env python
# -*- coding: utf8 -*-
#@+leo-ver=5-thin
#@+node:ekr.20130421172316.10765: * @file C:\leo.repo\trunk\leo\extensions\docutils\utils\punctuation_chars.py
#@@first
#@@first
#@@language python
# :Copyright: © 2011 Günter Milde.
# :License: Released under the terms of the `2-Clause BSD license`_, in short:
#
#    Copying and distribution of this file, with or without modification,
#    are permitted in any medium without royalty provided the copyright
#    notice and this notice are preserved.
#    This file is offered as-is, without any warranty.
#
# .. _2-Clause BSD license: http://www.spdx.org/licenses/BSD-2-Clause

# :Id: $Id: punctuation_chars.py 7463 2012-06-22 19:49:51Z milde $

import sys, re
import unicodedata
isPython2 = sys.version_info < (3,)
u_chr = unichr if isPython2 else chr

from docutils.utils.u import u ###

# punctuation characters around inline markup
# ===========================================
#
# This module provides the lists of characters for the implementation of
# the `inline markup recognition rules`_ in the reStructuredText parser
# (states.py)
#
# .. _inline markup recognition rules:
#     ../../../docs/ref/rst/restructuredtext.html#inline-markup

# Docutils punctuation category sample strings
# --------------------------------------------
#
# The sample strings are generated by punctuation_samples() and put here
# literal to avoid the time-consuming generation with every Docutils
# run. Running this file as a standalone module checks the definitions below
# against a re-calculation.

# **Important**: The backslashes are *not* redundant: they are used in regular expressions in states.py.

#@+<< define openers_ords >>
#@+node:ekr.20130422090029.10772: ** << define openers_ords >>
# openers_original = ur"""\"\'\(\<\[\{༺༼᚛⁅⁽₍〈❨❪❬❮❰❲❴⟅⟦⟨⟪⟬⟮⦃⦅⦇⦉⦋⦍⦏⦑⦓⦕⦗⧘⧚⧼⸢⸤⸦⸨〈《「『【〔〖〘〚〝〝﴾︗︵︷︹︻︽︿﹁﹃﹇﹙﹛﹝（［｛｟｢«‘“‹⸂⸄⸉⸌⸜⸠‚„»’”›⸃⸅⸊⸍⸝⸡‛‟"""
openers_ords = [
    92, # REVERSE SOLIDUS
    34, # QUOTATION MARK
    92, # REVERSE SOLIDUS
    39, # APOSTROPHE
    92, # REVERSE SOLIDUS
    40, # LEFT PARENTHESIS
    92, # REVERSE SOLIDUS
    60, # LESS-THAN SIGN
    92, # REVERSE SOLIDUS
    91, # LEFT SQUARE BRACKET
    92, # REVERSE SOLIDUS
    123, # LEFT CURLY BRACKET
    3898, # TIBETAN MARK GUG RTAGS GYON
    3900, # TIBETAN MARK ANG KHANG GYON
    5787, # OGHAM FEATHER MARK
    8261, # LEFT SQUARE BRACKET WITH QUILL
    8317, # SUPERSCRIPT LEFT PARENTHESIS
    8333, # SUBSCRIPT LEFT PARENTHESIS
    9001, # LEFT-POINTING ANGLE BRACKET
    10088, # MEDIUM LEFT PARENTHESIS ORNAMENT
    10090, # MEDIUM FLATTENED LEFT PARENTHESIS ORNAMENT
    10092, # MEDIUM LEFT-POINTING ANGLE BRACKET ORNAMENT
    10094, # HEAVY LEFT-POINTING ANGLE QUOTATION MARK ORNAMENT
    10096, # HEAVY LEFT-POINTING ANGLE BRACKET ORNAMENT
    10098, # LIGHT LEFT TORTOISE SHELL BRACKET ORNAMENT
    10100, # MEDIUM LEFT CURLY BRACKET ORNAMENT
    10181, # LEFT S-SHAPED BAG DELIMITER
    10214, # MATHEMATICAL LEFT WHITE SQUARE BRACKET
    10216, # MATHEMATICAL LEFT ANGLE BRACKET
    10218, # MATHEMATICAL LEFT DOUBLE ANGLE BRACKET
    10220, # MATHEMATICAL LEFT WHITE TORTOISE SHELL BRACKET
    10222, # MATHEMATICAL LEFT FLATTENED PARENTHESIS
    10627, # LEFT WHITE CURLY BRACKET
    10629, # LEFT WHITE PARENTHESIS
    10631, # Z NOTATION LEFT IMAGE BRACKET
    10633, # Z NOTATION LEFT BINDING BRACKET
    10635, # LEFT SQUARE BRACKET WITH UNDERBAR
    10637, # LEFT SQUARE BRACKET WITH TICK IN TOP CORNER
    10639, # LEFT SQUARE BRACKET WITH TICK IN BOTTOM CORNER
    10641, # LEFT ANGLE BRACKET WITH DOT
    10643, # LEFT ARC LESS-THAN BRACKET
    10645, # DOUBLE LEFT ARC GREATER-THAN BRACKET
    10647, # LEFT BLACK TORTOISE SHELL BRACKET
    10712, # LEFT WIGGLY FENCE
    10714, # LEFT DOUBLE WIGGLY FENCE
    10748, # LEFT-POINTING CURVED ANGLE BRACKET
    11810, # TOP LEFT HALF BRACKET
    11812, # BOTTOM LEFT HALF BRACKET
    11814, # LEFT SIDEWAYS U BRACKET
    11816, # LEFT DOUBLE PARENTHESIS
    12296, # LEFT ANGLE BRACKET
    12298, # LEFT DOUBLE ANGLE BRACKET
    12300, # LEFT CORNER BRACKET
    12302, # LEFT WHITE CORNER BRACKET
    12304, # LEFT BLACK LENTICULAR BRACKET
    12308, # LEFT TORTOISE SHELL BRACKET
    12310, # LEFT WHITE LENTICULAR BRACKET
    12312, # LEFT WHITE TORTOISE SHELL BRACKET
    12314, # LEFT WHITE SQUARE BRACKET
    12317, # REVERSED DOUBLE PRIME QUOTATION MARK
    12317, # REVERSED DOUBLE PRIME QUOTATION MARK
    64830, # ORNATE LEFT PARENTHESIS
    65047, # PRESENTATION FORM FOR VERTICAL LEFT WHITE LENTICULAR BRACKET
    65077, # PRESENTATION FORM FOR VERTICAL LEFT PARENTHESIS
    65079, # PRESENTATION FORM FOR VERTICAL LEFT CURLY BRACKET
    65081, # PRESENTATION FORM FOR VERTICAL LEFT TORTOISE SHELL BRACKET
    65083, # PRESENTATION FORM FOR VERTICAL LEFT BLACK LENTICULAR BRACKET
    65085, # PRESENTATION FORM FOR VERTICAL LEFT DOUBLE ANGLE BRACKET
    65087, # PRESENTATION FORM FOR VERTICAL LEFT ANGLE BRACKET
    65089, # PRESENTATION FORM FOR VERTICAL LEFT CORNER BRACKET
    65091, # PRESENTATION FORM FOR VERTICAL LEFT WHITE CORNER BRACKET
    65095, # PRESENTATION FORM FOR VERTICAL LEFT SQUARE BRACKET
    65113, # SMALL LEFT PARENTHESIS
    65115, # SMALL LEFT CURLY BRACKET
    65117, # SMALL LEFT TORTOISE SHELL BRACKET
    65288, # FULLWIDTH LEFT PARENTHESIS
    65339, # FULLWIDTH LEFT SQUARE BRACKET
    65371, # FULLWIDTH LEFT CURLY BRACKET
    65375, # FULLWIDTH LEFT WHITE PARENTHESIS
    65378, # HALFWIDTH LEFT CORNER BRACKET
    171, # LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
    8216, # LEFT SINGLE QUOTATION MARK
    8220, # LEFT DOUBLE QUOTATION MARK
    8249, # SINGLE LEFT-POINTING ANGLE QUOTATION MARK
    11778, # LEFT SUBSTITUTION BRACKET
    11780, # LEFT DOTTED SUBSTITUTION BRACKET
    11785, # LEFT TRANSPOSITION BRACKET
    11788, # LEFT RAISED OMISSION BRACKET
    11804, # LEFT LOW PARAPHRASE BRACKET
    11808, # LEFT VERTICAL BAR WITH QUILL
    8218, # SINGLE LOW-9 QUOTATION MARK
    8222, # DOUBLE LOW-9 QUOTATION MARK
    187, # RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
    8217, # RIGHT SINGLE QUOTATION MARK
    8221, # RIGHT DOUBLE QUOTATION MARK
    8250, # SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
    11779, # RIGHT SUBSTITUTION BRACKET
    11781, # RIGHT DOTTED SUBSTITUTION BRACKET
    11786, # RIGHT TRANSPOSITION BRACKET
    11789, # RIGHT RAISED OMISSION BRACKET
    11805, # RIGHT LOW PARAPHRASE BRACKET
    11809, # RIGHT VERTICAL BAR WITH QUILL
    8219, # SINGLE HIGH-REVERSED-9 QUOTATION MARK
    8223, # DOUBLE HIGH-REVERSED-9 QUOTATION MARK
]
#@-<< define openers_ords >>
openers = ''.join([u_chr(n) for n in openers_ords])
#@+<< define closers_ords >>
#@+node:ekr.20130422090029.10774: ** << define closers_ords >>
# closers = ur"""\"\'\)\>\]\}༻༽᚜⁆⁾₎〉❩❫❭❯❱❳❵⟆⟧⟩⟫⟭⟯⦄⦆⦈⦊⦌⦎⦐⦒⦔⦖⦘⧙⧛⧽⸣⸥⸧⸩〉》」』】〕〗〙〛〞〟﴿︘︶︸︺︼︾﹀﹂﹄﹈﹚﹜﹞）］｝｠｣»’”›⸃⸅⸊⸍⸝⸡‛‟«‘“‹⸂⸄⸉⸌⸜⸠‚„"""

closers_ords = [
    92, # REVERSE SOLIDUS
    34, # QUOTATION MARK
    92, # REVERSE SOLIDUS
    39, # APOSTROPHE
    92, # REVERSE SOLIDUS
    41, # RIGHT PARENTHESIS
    92, # REVERSE SOLIDUS
    62, # GREATER-THAN SIGN
    92, # REVERSE SOLIDUS
    93, # RIGHT SQUARE BRACKET
    92, # REVERSE SOLIDUS
    125, # RIGHT CURLY BRACKET
    3899, # TIBETAN MARK GUG RTAGS GYAS
    3901, # TIBETAN MARK ANG KHANG GYAS
    5788, # OGHAM REVERSED FEATHER MARK
    8262, # RIGHT SQUARE BRACKET WITH QUILL
    8318, # SUPERSCRIPT RIGHT PARENTHESIS
    8334, # SUBSCRIPT RIGHT PARENTHESIS
    9002, # RIGHT-POINTING ANGLE BRACKET
    10089, # MEDIUM RIGHT PARENTHESIS ORNAMENT
    10091, # MEDIUM FLATTENED RIGHT PARENTHESIS ORNAMENT
    10093, # MEDIUM RIGHT-POINTING ANGLE BRACKET ORNAMENT
    10095, # HEAVY RIGHT-POINTING ANGLE QUOTATION MARK ORNAMENT
    10097, # HEAVY RIGHT-POINTING ANGLE BRACKET ORNAMENT
    10099, # LIGHT RIGHT TORTOISE SHELL BRACKET ORNAMENT
    10101, # MEDIUM RIGHT CURLY BRACKET ORNAMENT
    10182, # RIGHT S-SHAPED BAG DELIMITER
    10215, # MATHEMATICAL RIGHT WHITE SQUARE BRACKET
    10217, # MATHEMATICAL RIGHT ANGLE BRACKET
    10219, # MATHEMATICAL RIGHT DOUBLE ANGLE BRACKET
    10221, # MATHEMATICAL RIGHT WHITE TORTOISE SHELL BRACKET
    10223, # MATHEMATICAL RIGHT FLATTENED PARENTHESIS
    10628, # RIGHT WHITE CURLY BRACKET
    10630, # RIGHT WHITE PARENTHESIS
    10632, # Z NOTATION RIGHT IMAGE BRACKET
    10634, # Z NOTATION RIGHT BINDING BRACKET
    10636, # RIGHT SQUARE BRACKET WITH UNDERBAR
    10638, # RIGHT SQUARE BRACKET WITH TICK IN BOTTOM CORNER
    10640, # RIGHT SQUARE BRACKET WITH TICK IN TOP CORNER
    10642, # RIGHT ANGLE BRACKET WITH DOT
    10644, # RIGHT ARC GREATER-THAN BRACKET
    10646, # DOUBLE RIGHT ARC LESS-THAN BRACKET
    10648, # RIGHT BLACK TORTOISE SHELL BRACKET
    10713, # RIGHT WIGGLY FENCE
    10715, # RIGHT DOUBLE WIGGLY FENCE
    10749, # RIGHT-POINTING CURVED ANGLE BRACKET
    11811, # TOP RIGHT HALF BRACKET
    11813, # BOTTOM RIGHT HALF BRACKET
    11815, # RIGHT SIDEWAYS U BRACKET
    11817, # RIGHT DOUBLE PARENTHESIS
    12297, # RIGHT ANGLE BRACKET
    12299, # RIGHT DOUBLE ANGLE BRACKET
    12301, # RIGHT CORNER BRACKET
    12303, # RIGHT WHITE CORNER BRACKET
    12305, # RIGHT BLACK LENTICULAR BRACKET
    12309, # RIGHT TORTOISE SHELL BRACKET
    12311, # RIGHT WHITE LENTICULAR BRACKET
    12313, # RIGHT WHITE TORTOISE SHELL BRACKET
    12315, # RIGHT WHITE SQUARE BRACKET
    12318, # DOUBLE PRIME QUOTATION MARK
    12319, # LOW DOUBLE PRIME QUOTATION MARK
    64831, # ORNATE RIGHT PARENTHESIS
    65048, # PRESENTATION FORM FOR VERTICAL RIGHT WHITE LENTICULAR BRAKCET
    65078, # PRESENTATION FORM FOR VERTICAL RIGHT PARENTHESIS
    65080, # PRESENTATION FORM FOR VERTICAL RIGHT CURLY BRACKET
    65082, # PRESENTATION FORM FOR VERTICAL RIGHT TORTOISE SHELL BRACKET
    65084, # PRESENTATION FORM FOR VERTICAL RIGHT BLACK LENTICULAR BRACKET
    65086, # PRESENTATION FORM FOR VERTICAL RIGHT DOUBLE ANGLE BRACKET
    65088, # PRESENTATION FORM FOR VERTICAL RIGHT ANGLE BRACKET
    65090, # PRESENTATION FORM FOR VERTICAL RIGHT CORNER BRACKET
    65092, # PRESENTATION FORM FOR VERTICAL RIGHT WHITE CORNER BRACKET
    65096, # PRESENTATION FORM FOR VERTICAL RIGHT SQUARE BRACKET
    65114, # SMALL RIGHT PARENTHESIS
    65116, # SMALL RIGHT CURLY BRACKET
    65118, # SMALL RIGHT TORTOISE SHELL BRACKET
    65289, # FULLWIDTH RIGHT PARENTHESIS
    65341, # FULLWIDTH RIGHT SQUARE BRACKET
    65373, # FULLWIDTH RIGHT CURLY BRACKET
    65376, # FULLWIDTH RIGHT WHITE PARENTHESIS
    65379, # HALFWIDTH RIGHT CORNER BRACKET
    187, # RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
    8217, # RIGHT SINGLE QUOTATION MARK
    8221, # RIGHT DOUBLE QUOTATION MARK
    8250, # SINGLE RIGHT-POINTING ANGLE QUOTATION MARK
    11779, # RIGHT SUBSTITUTION BRACKET
    11781, # RIGHT DOTTED SUBSTITUTION BRACKET
    11786, # RIGHT TRANSPOSITION BRACKET
    11789, # RIGHT RAISED OMISSION BRACKET
    11805, # RIGHT LOW PARAPHRASE BRACKET
    11809, # RIGHT VERTICAL BAR WITH QUILL
    8219, # SINGLE HIGH-REVERSED-9 QUOTATION MARK
    8223, # DOUBLE HIGH-REVERSED-9 QUOTATION MARK
    171, # LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
    8216, # LEFT SINGLE QUOTATION MARK
    8220, # LEFT DOUBLE QUOTATION MARK
    8249, # SINGLE LEFT-POINTING ANGLE QUOTATION MARK
    11778, # LEFT SUBSTITUTION BRACKET
    11780, # LEFT DOTTED SUBSTITUTION BRACKET
    11785, # LEFT TRANSPOSITION BRACKET
    11788, # LEFT RAISED OMISSION BRACKET
    11804, # LEFT LOW PARAPHRASE BRACKET
    11808, # LEFT VERTICAL BAR WITH QUILL
    8218, # SINGLE LOW-9 QUOTATION MARK
    8222, # DOUBLE LOW-9 QUOTATION MARK
]
#@-<< define closers_ords >>
closers = ''.join([u_chr(n) for n in closers_ords])
#@+<< define delimiter_ords >>
#@+node:ekr.20130422090029.10773: ** << define delimiter_ords >>
# delimiters_original = ur"\-\/\:֊־᐀᠆‐‑‒–—―⸗⸚〜〰゠︱︲﹘﹣－¡·¿;·՚՛՜՝՞՟։׀׃׆׳״؉؊،؍؛؞؟٪٫٬٭۔܀܁܂܃܄܅܆܇܈܉܊܋܌܍߷߸߹࠰࠱࠲࠳࠴࠵࠶࠷࠸࠹࠺࠻࠼࠽࠾।॥॰෴๏๚๛༄༅༆༇༈༉༊་༌།༎༏༐༑༒྅࿐࿑࿒࿓࿔၊။၌၍၎၏჻፡።፣፤፥፦፧፨᙭᙮᛫᛬᛭᜵᜶។៕៖៘៙៚᠀᠁᠂᠃᠄᠅᠇᠈᠉᠊᥄᥅᧞᧟᨞᨟᪠᪡᪢᪣᪤᪥᪦᪨᪩᪪᪫᪬᪭᭚᭛᭜᭝᭞᭟᭠᰻᰼᰽᰾᰿᱾᱿᳓‖‗†‡•‣․‥…‧‰‱′″‴‵‶‷‸※‼‽‾⁁⁂⁃⁇⁈⁉⁊⁋⁌⁍⁎⁏⁐⁑⁓⁕⁖⁗⁘⁙⁚⁛⁜⁝⁞⳹⳺⳻⳼⳾⳿⸀⸁⸆⸇⸈⸋⸎⸏⸐⸑⸒⸓⸔⸕⸖⸘⸙⸛⸞⸟⸪⸫⸬⸭⸮⸰⸱、。〃〽・꓾꓿꘍꘎꘏꙳꙾꛲꛳꛴꛵꛶꛷꡴꡵꡶꡷꣎꣏꣸꣹꣺꤮꤯꥟꧁꧂꧃꧄꧅꧆꧇꧈꧉꧊꧋꧌꧍꧞꧟꩜꩝꩞꩟꫞꫟꯫︐︑︒︓︔︕︖︙︰﹅﹆﹉﹊﹋﹌﹐﹑﹒﹔﹕﹖﹗﹟﹠﹡﹨﹪﹫！＂＃％＆＇＊，．／：；？＠＼｡､･𐄀𐄁𐎟𐏐𐡗𐤟𐤿𐩐𐩑𐩒𐩓𐩔𐩕𐩖𐩗𐩘𐩿𐬹𐬺𐬻𐬼𐬽𐬾𐬿𑂻𑂼𑂾𑂿𑃀𑃁𒑰𒑱𒑲𒑳"
# delimiter_ords = [ord(ch) for ch in delimiters_original if unicodedata.name(ch,'Unknown') != 'Unknown']
delimiter_ords = [
    92, # REVERSE SOLIDUS
    45, # HYPHEN-MINUS
    92, # REVERSE SOLIDUS
    47, # SOLIDUS
    92, # REVERSE SOLIDUS
    58, # COLON
    1418, # ARMENIAN HYPHEN
    1470, # HEBREW PUNCTUATION MAQAF
    5120, # CANADIAN SYLLABICS HYPHEN
    6150, # MONGOLIAN TODO SOFT HYPHEN
    8208, # HYPHEN
    8209, # NON-BREAKING HYPHEN
    8210, # FIGURE DASH
    8211, # EN DASH
    8212, # EM DASH
    8213, # HORIZONTAL BAR
    11799, # DOUBLE OBLIQUE HYPHEN
    11802, # HYPHEN WITH DIAERESIS
    12316, # WAVE DASH
    12336, # WAVY DASH
    12448, # KATAKANA-HIRAGANA DOUBLE HYPHEN
    65073, # PRESENTATION FORM FOR VERTICAL EM DASH
    65074, # PRESENTATION FORM FOR VERTICAL EN DASH
    65112, # SMALL EM DASH
    65123, # SMALL HYPHEN-MINUS
    65293, # FULLWIDTH HYPHEN-MINUS
    161, # INVERTED EXCLAMATION MARK
    183, # MIDDLE DOT
    191, # INVERTED QUESTION MARK
    894, # GREEK QUESTION MARK
    903, # GREEK ANO TELEIA
    1370, # ARMENIAN APOSTROPHE
    1371, # ARMENIAN EMPHASIS MARK
    1372, # ARMENIAN EXCLAMATION MARK
    1373, # ARMENIAN COMMA
    1374, # ARMENIAN QUESTION MARK
    1375, # ARMENIAN ABBREVIATION MARK
    1417, # ARMENIAN FULL STOP
    1472, # HEBREW PUNCTUATION PASEQ
    1475, # HEBREW PUNCTUATION SOF PASUQ
    1478, # HEBREW PUNCTUATION NUN HAFUKHA
    1523, # HEBREW PUNCTUATION GERESH
    1524, # HEBREW PUNCTUATION GERSHAYIM
    1545, # ARABIC-INDIC PER MILLE SIGN
    1546, # ARABIC-INDIC PER TEN THOUSAND SIGN
    1548, # ARABIC COMMA
    1549, # ARABIC DATE SEPARATOR
    1563, # ARABIC SEMICOLON
    1566, # ARABIC TRIPLE DOT PUNCTUATION MARK
    1567, # ARABIC QUESTION MARK
    1642, # ARABIC PERCENT SIGN
    1643, # ARABIC DECIMAL SEPARATOR
    1644, # ARABIC THOUSANDS SEPARATOR
    1645, # ARABIC FIVE POINTED STAR
    1748, # ARABIC FULL STOP
    1792, # SYRIAC END OF PARAGRAPH
    1793, # SYRIAC SUPRALINEAR FULL STOP
    1794, # SYRIAC SUBLINEAR FULL STOP
    1795, # SYRIAC SUPRALINEAR COLON
    1796, # SYRIAC SUBLINEAR COLON
    1797, # SYRIAC HORIZONTAL COLON
    1798, # SYRIAC COLON SKEWED LEFT
    1799, # SYRIAC COLON SKEWED RIGHT
    1800, # SYRIAC SUPRALINEAR COLON SKEWED LEFT
    1801, # SYRIAC SUBLINEAR COLON SKEWED RIGHT
    1802, # SYRIAC CONTRACTION
    1803, # SYRIAC HARKLEAN OBELUS
    1804, # SYRIAC HARKLEAN METOBELUS
    1805, # SYRIAC HARKLEAN ASTERISCUS
    2039, # NKO SYMBOL GBAKURUNEN
    2040, # NKO COMMA
    2041, # NKO EXCLAMATION MARK
    2096, # SAMARITAN PUNCTUATION NEQUDAA
    2097, # SAMARITAN PUNCTUATION AFSAAQ
    2098, # SAMARITAN PUNCTUATION ANGED
    2099, # SAMARITAN PUNCTUATION BAU
    2100, # SAMARITAN PUNCTUATION ATMAAU
    2101, # SAMARITAN PUNCTUATION SHIYYAALAA
    2102, # SAMARITAN ABBREVIATION MARK
    2103, # SAMARITAN PUNCTUATION MELODIC QITSA
    2104, # SAMARITAN PUNCTUATION ZIQAA
    2105, # SAMARITAN PUNCTUATION QITSA
    2106, # SAMARITAN PUNCTUATION ZAEF
    2107, # SAMARITAN PUNCTUATION TURU
    2108, # SAMARITAN PUNCTUATION ARKAANU
    2109, # SAMARITAN PUNCTUATION SOF MASHFAAT
    2110, # SAMARITAN PUNCTUATION ANNAAU
    2404, # DEVANAGARI DANDA
    2405, # DEVANAGARI DOUBLE DANDA
    2416, # DEVANAGARI ABBREVIATION SIGN
    3572, # SINHALA PUNCTUATION KUNDDALIYA
    3663, # THAI CHARACTER FONGMAN
    3674, # THAI CHARACTER ANGKHANKHU
    3675, # THAI CHARACTER KHOMUT
    3844, # TIBETAN MARK INITIAL YIG MGO MDUN MA
    3845, # TIBETAN MARK CLOSING YIG MGO SGAB MA
    3846, # TIBETAN MARK CARET YIG MGO PHUR SHAD MA
    3847, # TIBETAN MARK YIG MGO TSHEG SHAD MA
    3848, # TIBETAN MARK SBRUL SHAD
    3849, # TIBETAN MARK BSKUR YIG MGO
    3850, # TIBETAN MARK BKA- SHOG YIG MGO
    3851, # TIBETAN MARK INTERSYLLABIC TSHEG
    3852, # TIBETAN MARK DELIMITER TSHEG BSTAR
    3853, # TIBETAN MARK SHAD
    3854, # TIBETAN MARK NYIS SHAD
    3855, # TIBETAN MARK TSHEG SHAD
    3856, # TIBETAN MARK NYIS TSHEG SHAD
    3857, # TIBETAN MARK RIN CHEN SPUNGS SHAD
    3858, # TIBETAN MARK RGYA GRAM SHAD
    3973, # TIBETAN MARK PALUTA
    4048, # TIBETAN MARK BSKA- SHOG GI MGO RGYAN
    4049, # TIBETAN MARK MNYAM YIG GI MGO RGYAN
    4050, # TIBETAN MARK NYIS TSHEG
    4051, # TIBETAN MARK INITIAL BRDA RNYING YIG MGO MDUN MA
    4052, # TIBETAN MARK CLOSING BRDA RNYING YIG MGO SGAB MA
    4170, # MYANMAR SIGN LITTLE SECTION
    4171, # MYANMAR SIGN SECTION
    4172, # MYANMAR SYMBOL LOCATIVE
    4173, # MYANMAR SYMBOL COMPLETED
    4174, # MYANMAR SYMBOL AFOREMENTIONED
    4175, # MYANMAR SYMBOL GENITIVE
    4347, # GEORGIAN PARAGRAPH SEPARATOR
    4961, # ETHIOPIC WORDSPACE
    4962, # ETHIOPIC FULL STOP
    4963, # ETHIOPIC COMMA
    4964, # ETHIOPIC SEMICOLON
    4965, # ETHIOPIC COLON
    4966, # ETHIOPIC PREFACE COLON
    4967, # ETHIOPIC QUESTION MARK
    4968, # ETHIOPIC PARAGRAPH SEPARATOR
    5741, # CANADIAN SYLLABICS CHI SIGN
    5742, # CANADIAN SYLLABICS FULL STOP
    5867, # RUNIC SINGLE PUNCTUATION
    5868, # RUNIC MULTIPLE PUNCTUATION
    5869, # RUNIC CROSS PUNCTUATION
    5941, # PHILIPPINE SINGLE PUNCTUATION
    5942, # PHILIPPINE DOUBLE PUNCTUATION
    6100, # KHMER SIGN KHAN
    6101, # KHMER SIGN BARIYOOSAN
    6102, # KHMER SIGN CAMNUC PII KUUH
    6104, # KHMER SIGN BEYYAL
    6105, # KHMER SIGN PHNAEK MUAN
    6106, # KHMER SIGN KOOMUUT
    6144, # MONGOLIAN BIRGA
    6145, # MONGOLIAN ELLIPSIS
    6146, # MONGOLIAN COMMA
    6147, # MONGOLIAN FULL STOP
    6148, # MONGOLIAN COLON
    6149, # MONGOLIAN FOUR DOTS
    6151, # MONGOLIAN SIBE SYLLABLE BOUNDARY MARKER
    6152, # MONGOLIAN MANCHU COMMA
    6153, # MONGOLIAN MANCHU FULL STOP
    6154, # MONGOLIAN NIRUGU
    6468, # LIMBU EXCLAMATION MARK
    6469, # LIMBU QUESTION MARK
    6622, # NEW TAI LUE SIGN LAE
    6623, # NEW TAI LUE SIGN LAEV
    6686, # BUGINESE PALLAWA
    6687, # BUGINESE END OF SECTION
    6816, # TAI THAM SIGN WIANG
    6817, # TAI THAM SIGN WIANGWAAK
    6818, # TAI THAM SIGN SAWAN
    6819, # TAI THAM SIGN KEOW
    6820, # TAI THAM SIGN HOY
    6821, # TAI THAM SIGN DOKMAI
    6822, # TAI THAM SIGN REVERSED ROTATED RANA
    6824, # TAI THAM SIGN KAAN
    6825, # TAI THAM SIGN KAANKUU
    6826, # TAI THAM SIGN SATKAAN
    6827, # TAI THAM SIGN SATKAANKUU
    6828, # TAI THAM SIGN HANG
    6829, # TAI THAM SIGN CAANG
    7002, # BALINESE PANTI
    7003, # BALINESE PAMADA
    7004, # BALINESE WINDU
    7005, # BALINESE CARIK PAMUNGKAH
    7006, # BALINESE CARIK SIKI
    7007, # BALINESE CARIK PAREREN
    7008, # BALINESE PAMENENG
    7227, # LEPCHA PUNCTUATION TA-ROL
    7228, # LEPCHA PUNCTUATION NYET THYOOM TA-ROL
    7229, # LEPCHA PUNCTUATION CER-WA
    7230, # LEPCHA PUNCTUATION TSHOOK CER-WA
    7231, # LEPCHA PUNCTUATION TSHOOK
    7294, # OL CHIKI PUNCTUATION MUCAAD
    7295, # OL CHIKI PUNCTUATION DOUBLE MUCAAD
    7379, # VEDIC SIGN NIHSHVASA
    8214, # DOUBLE VERTICAL LINE
    8215, # DOUBLE LOW LINE
    8224, # DAGGER
    8225, # DOUBLE DAGGER
    8226, # BULLET
    8227, # TRIANGULAR BULLET
    8228, # ONE DOT LEADER
    8229, # TWO DOT LEADER
    8230, # HORIZONTAL ELLIPSIS
    8231, # HYPHENATION POINT
    8240, # PER MILLE SIGN
    8241, # PER TEN THOUSAND SIGN
    8242, # PRIME
    8243, # DOUBLE PRIME
    8244, # TRIPLE PRIME
    8245, # REVERSED PRIME
    8246, # REVERSED DOUBLE PRIME
    8247, # REVERSED TRIPLE PRIME
    8248, # CARET
    8251, # REFERENCE MARK
    8252, # DOUBLE EXCLAMATION MARK
    8253, # INTERROBANG
    8254, # OVERLINE
    8257, # CARET INSERTION POINT
    8258, # ASTERISM
    8259, # HYPHEN BULLET
    8263, # DOUBLE QUESTION MARK
    8264, # QUESTION EXCLAMATION MARK
    8265, # EXCLAMATION QUESTION MARK
    8266, # TIRONIAN SIGN ET
    8267, # REVERSED PILCROW SIGN
    8268, # BLACK LEFTWARDS BULLET
    8269, # BLACK RIGHTWARDS BULLET
    8270, # LOW ASTERISK
    8271, # REVERSED SEMICOLON
    8272, # CLOSE UP
    8273, # TWO ASTERISKS ALIGNED VERTICALLY
    8275, # SWUNG DASH
    8277, # FLOWER PUNCTUATION MARK
    8278, # THREE DOT PUNCTUATION
    8279, # QUADRUPLE PRIME
    8280, # FOUR DOT PUNCTUATION
    8281, # FIVE DOT PUNCTUATION
    8282, # TWO DOT PUNCTUATION
    8283, # FOUR DOT MARK
    8284, # DOTTED CROSS
    8285, # TRICOLON
    8286, # VERTICAL FOUR DOTS
    11513, # COPTIC OLD NUBIAN FULL STOP
    11514, # COPTIC OLD NUBIAN DIRECT QUESTION MARK
    11515, # COPTIC OLD NUBIAN INDIRECT QUESTION MARK
    11516, # COPTIC OLD NUBIAN VERSE DIVIDER
    11518, # COPTIC FULL STOP
    11519, # COPTIC MORPHOLOGICAL DIVIDER
    11776, # RIGHT ANGLE SUBSTITUTION MARKER
    11777, # RIGHT ANGLE DOTTED SUBSTITUTION MARKER
    11782, # RAISED INTERPOLATION MARKER
    11783, # RAISED DOTTED INTERPOLATION MARKER
    11784, # DOTTED TRANSPOSITION MARKER
    11787, # RAISED SQUARE
    11790, # EDITORIAL CORONIS
    11791, # PARAGRAPHOS
    11792, # FORKED PARAGRAPHOS
    11793, # REVERSED FORKED PARAGRAPHOS
    11794, # HYPODIASTOLE
    11795, # DOTTED OBELOS
    11796, # DOWNWARDS ANCORA
    11797, # UPWARDS ANCORA
    11798, # DOTTED RIGHT-POINTING ANGLE
    11800, # INVERTED INTERROBANG
    11801, # PALM BRANCH
    11803, # TILDE WITH RING ABOVE
    11806, # TILDE WITH DOT ABOVE
    11807, # TILDE WITH DOT BELOW
    11818, # TWO DOTS OVER ONE DOT PUNCTUATION
    11819, # ONE DOT OVER TWO DOTS PUNCTUATION
    11820, # SQUARED FOUR DOT PUNCTUATION
    11821, # FIVE DOT MARK
    11822, # REVERSED QUESTION MARK
    11824, # RING POINT
    11825, # WORD SEPARATOR MIDDLE DOT
    12289, # IDEOGRAPHIC COMMA
    12290, # IDEOGRAPHIC FULL STOP
    12291, # DITTO MARK
    12349, # PART ALTERNATION MARK
    12539, # KATAKANA MIDDLE DOT
    42238, # LISU PUNCTUATION COMMA
    42239, # LISU PUNCTUATION FULL STOP
    42509, # VAI COMMA
    42510, # VAI FULL STOP
    42511, # VAI QUESTION MARK
    42611, # SLAVONIC ASTERISK
    42622, # CYRILLIC KAVYKA
    42738, # BAMUM NJAEMLI
    42739, # BAMUM FULL STOP
    42740, # BAMUM COLON
    42741, # BAMUM COMMA
    42742, # BAMUM SEMICOLON
    42743, # BAMUM QUESTION MARK
    43124, # PHAGS-PA SINGLE HEAD MARK
    43125, # PHAGS-PA DOUBLE HEAD MARK
    43126, # PHAGS-PA MARK SHAD
    43127, # PHAGS-PA MARK DOUBLE SHAD
    43214, # SAURASHTRA DANDA
    43215, # SAURASHTRA DOUBLE DANDA
    43256, # DEVANAGARI SIGN PUSHPIKA
    43257, # DEVANAGARI GAP FILLER
    43258, # DEVANAGARI CARET
    43310, # KAYAH LI SIGN CWI
    43311, # KAYAH LI SIGN SHYA
    43359, # REJANG SECTION MARK
    43457, # JAVANESE LEFT RERENGGAN
    43458, # JAVANESE RIGHT RERENGGAN
    43459, # JAVANESE PADA ANDAP
    43460, # JAVANESE PADA MADYA
    43461, # JAVANESE PADA LUHUR
    43462, # JAVANESE PADA WINDU
    43463, # JAVANESE PADA PANGKAT
    43464, # JAVANESE PADA LINGSA
    43465, # JAVANESE PADA LUNGSI
    43466, # JAVANESE PADA ADEG
    43467, # JAVANESE PADA ADEG ADEG
    43468, # JAVANESE PADA PISELEH
    43469, # JAVANESE TURNED PADA PISELEH
    43486, # JAVANESE PADA TIRTA TUMETES
    43487, # JAVANESE PADA ISEN-ISEN
    43612, # CHAM PUNCTUATION SPIRAL
    43613, # CHAM PUNCTUATION DANDA
    43614, # CHAM PUNCTUATION DOUBLE DANDA
    43615, # CHAM PUNCTUATION TRIPLE DANDA
    43742, # TAI VIET SYMBOL HO HOI
    43743, # TAI VIET SYMBOL KOI KOI
    44011, # MEETEI MAYEK CHEIKHEI
    65040, # PRESENTATION FORM FOR VERTICAL COMMA
    65041, # PRESENTATION FORM FOR VERTICAL IDEOGRAPHIC COMMA
    65042, # PRESENTATION FORM FOR VERTICAL IDEOGRAPHIC FULL STOP
    65043, # PRESENTATION FORM FOR VERTICAL COLON
    65044, # PRESENTATION FORM FOR VERTICAL SEMICOLON
    65045, # PRESENTATION FORM FOR VERTICAL EXCLAMATION MARK
    65046, # PRESENTATION FORM FOR VERTICAL QUESTION MARK
    65049, # PRESENTATION FORM FOR VERTICAL HORIZONTAL ELLIPSIS
    65072, # PRESENTATION FORM FOR VERTICAL TWO DOT LEADER
    65093, # SESAME DOT
    65094, # WHITE SESAME DOT
    65097, # DASHED OVERLINE
    65098, # CENTRELINE OVERLINE
    65099, # WAVY OVERLINE
    65100, # DOUBLE WAVY OVERLINE
    65104, # SMALL COMMA
    65105, # SMALL IDEOGRAPHIC COMMA
    65106, # SMALL FULL STOP
    65108, # SMALL SEMICOLON
    65109, # SMALL COLON
    65110, # SMALL QUESTION MARK
    65111, # SMALL EXCLAMATION MARK
    65119, # SMALL NUMBER SIGN
    65120, # SMALL AMPERSAND
    65121, # SMALL ASTERISK
    65128, # SMALL REVERSE SOLIDUS
    65130, # SMALL PERCENT SIGN
    65131, # SMALL COMMERCIAL AT
    65281, # FULLWIDTH EXCLAMATION MARK
    65282, # FULLWIDTH QUOTATION MARK
    65283, # FULLWIDTH NUMBER SIGN
    65285, # FULLWIDTH PERCENT SIGN
    65286, # FULLWIDTH AMPERSAND
    65287, # FULLWIDTH APOSTROPHE
    65290, # FULLWIDTH ASTERISK
    65292, # FULLWIDTH COMMA
    65294, # FULLWIDTH FULL STOP
    65295, # FULLWIDTH SOLIDUS
    65306, # FULLWIDTH COLON
    65307, # FULLWIDTH SEMICOLON
    65311, # FULLWIDTH QUESTION MARK
    65312, # FULLWIDTH COMMERCIAL AT
    65340, # FULLWIDTH REVERSE SOLIDUS
    65377, # HALFWIDTH IDEOGRAPHIC FULL STOP
    65380, # HALFWIDTH IDEOGRAPHIC COMMA
    65381, # HALFWIDTH KATAKANA MIDDLE DOT
]
#@-<< define delimiter_ords >>
delimiters = ''.join([u_chr(n) for n in delimiter_ords])
# closing_delimiters_original = ur"\.\,\;\!\?"
if isPython2:
    closing_delimiters = unicode("\\.\\,\\;\\!\\?")
else:
    closing_delimiters = str("\\.\\,\\;\\!\\?")
# assert closing_delimiters == closing_delimiters_original
if isPython2:
    assert isinstance(openers,unicode)
    assert isinstance(closers,unicode)
    assert isinstance(delimiters,unicode)
    assert isinstance(closing_delimiters,unicode)

# Unicode punctuation character categories
# ----------------------------------------

unicode_punctuation_categories = {
    # 'Pc': 'Connector', # not used in Docutils inline markup recognition
    'Pd': 'Dash',
    'Ps': 'Open',
    'Pe': 'Close',
    'Pi': 'Initial quote', # may behave like Ps or Pe depending on usage
    'Pf': 'Final quote', # may behave like Ps or Pe depending on usage
    'Po': 'Other'
    }
"""Unicode character categories for punctuation"""


# generate character pattern strings
# ==================================

def unicode_charlists(categories, cp_min=0, cp_max=None):
    """Return dictionary of Unicode character lists.

    For each of the `catagories`, an item contains a list with all Unicode
    characters with `cp_min` <= code-point <= `cp_max` that belong to the
    category. (The default values check every code-point supported by Python.)
    """
    # Determine highest code point with one of the given categories
    # (may shorten the search time considerably if there are many
    # categories with not too high characters):
    if cp_max is None:
        cp_max = max(x for x in xrange(sys.maxunicode + 1)
                     if unicodedata.category(u_chr(x)) in categories)
        # print cp_max # => 74867 for unicode_punctuation_categories
    charlists = {}
    for cat in categories:
        charlists[cat] = [u_chr(x) for x in xrange(cp_min, cp_max+1)
                          if unicodedata.category(u_chr(x)) == cat]
    return charlists


# Character categories in Docutils
# --------------------------------

def punctuation_samples():

    """Docutils punctuation category sample strings.

    Return list of sample strings for the categories "Open", "Close",
    "Delimiters" and "Closing-Delimiters" used in the `inline markup
    recognition rules`_.
    """

    # Lists with characters in Unicode punctuation character categories
    cp_min = 160 # ASCII chars have special rules for backwards compatibility
    ucharlists = unicode_charlists(unicode_punctuation_categories, cp_min)

    # match opening/closing characters
    # --------------------------------
    # Rearange the lists to ensure matching characters at the same
    # index position.

    # low quotation marks are also used as closers (e.g. in Greek)
    # move them to category Pi:
    ucharlists['Ps'].remove(u('‚')) # 201A  SINGLE LOW-9 QUOTATION MARK
    ucharlists['Ps'].remove(u('„')) # 201E  DOUBLE LOW-9 QUOTATION MARK
    ucharlists['Pi'] += [u('‚'), u('„')]

    ucharlists['Pi'].remove(u('‛')) # 201B  SINGLE HIGH-REVERSED-9 QUOTATION MARK
    ucharlists['Pi'].remove(u('‟')) # 201F  DOUBLE HIGH-REVERSED-9 QUOTATION MARK
    ucharlists['Pf'] += [u('‛'), u('‟')]

    # 301F  LOW DOUBLE PRIME QUOTATION MARK misses the opening pendant:
    ucharlists['Ps'].insert(ucharlists['Pe'].index(u('\u301f')), u('\u301d'))

    # print u''.join(ucharlists['Ps']).encode('utf8')
    # print u''.join(ucharlists['Pe']).encode('utf8')
    # print u''.join(ucharlists['Pi']).encode('utf8')
    # print u''.join(ucharlists['Pf']).encode('utf8')

    # The Docutils character categories
    # ---------------------------------
    #
    # The categorization of ASCII chars is non-standard to reduce both
    # false positives and need for escaping. (see `inline markup recognition
    # rules`_)

    # matching, allowed before markup
    openers = [re.escape('"\'(<[{')]
    for cat in ('Ps', 'Pi', 'Pf'):
        openers.extend(ucharlists[cat])

    # matching, allowed after markup
    closers = [re.escape('"\')>]}')]
    for cat in ('Pe', 'Pf', 'Pi'):
        closers.extend(ucharlists[cat])

    # non-matching, allowed on both sides
    delimiters = [re.escape('-/:')]
    for cat in ('Pd', 'Po'):
        delimiters.extend(ucharlists[cat])

    # non-matching, after markup
    closing_delimiters = [re.escape('.,;!?')]

    # # Test open/close matching:
    # for i in range(min(len(openers),len(closers))):
    #     print '%4d    %s    %s' % (i, openers[i].encode('utf8'),
    #                                closers[i].encode('utf8'))

    return [u('').join(chars)
            for chars in (openers, closers, delimiters, closing_delimiters)]


# Matching open/close quotes
# --------------------------

# Rule (5) requires determination of matching open/close pairs. However,
# the pairing of open/close quotes is ambigue due to  different typographic
# conventions in different languages.

# quote_pairs_original = {
    # u'\xbb':   u'\xbb', # Swedish
    # u'\u2018': u'\u201a', # Greek
    # u'\u2019': u'\u2019', # Swedish
    # u'\u201a': u'\u2018\u2019', # German, Polish
    # u'\u201c': u'\u201e', # German
    # u'\u201e': u'\u201c\u201d',
    # u'\u201d': u'\u201d', # Swedish
    # u'\u203a': u'\u203a', # Swedish
# }
quote_pairs_ord_d = {
    0xbb:   [0xbb],
    0x2018: [0x201a],
    0x2019: [0x2019],
    0x201a: [0x2018,0x2019],
    0x201c: [0x201e],
    0x201d: [0x201d],
    0x201e: [0x201c,0x201d],
    0x203a: [0x203a],
}
quote_pairs = {}
d = quote_pairs_ord_d
for n in d.keys():
    ch = u_chr(n)
    quote_pairs [ch] = ''.join([u_chr(n2) for n2 in d.get(n)])
# assert quote_pairs == quote_pairs_original

def match_chars(c1, c2):
    try:
        i = openers.index(c1)
    except ValueError:  # c1 not in openers
        return False
    return c2 == closers[i] or c2 in quote_pairs.get(c1, '')

# print results
# =============

if __name__ == '__main__':

    # (re) create and compare the samples:
    (o, c, d, cd) = punctuation_samples()
    if o != openers:
        print('- openers = ur"""%s"""' % openers.encode('utf8'))
        print('+ openers = ur"""%s"""' % o.encode('utf8'))
    if c != closers:
        print('- closers = ur"""%s"""' % closers.encode('utf8'))
        print('+ closers = ur"""%s"""' % c.encode('utf8'))
    if d != delimiters:
        print('- delimiters = ur"%s"' % delimiters.encode('utf8'))
        print('+ delimiters = ur"%s"' % d.encode('utf8'))
    if cd != closing_delimiters:
        print('- closing_delimiters = ur"%s"' % closing_delimiters.encode('utf8'))
        print('+ closing_delimiters = ur"%s"' % cd.encode('utf8'))

    # # test prints
    # print 'openers = ', repr(openers)
    # print 'closers = ', repr(closers)
    # print 'delimiters = ', repr(delimiters)
    # print 'closing_delimiters = ', repr(closing_delimiters)

    # ucharlists = unicode_charlists(unicode_punctuation_categories)
    # for cat, chars in ucharlists.items():
    #     # print cat, chars
    #     # compact output (visible with a comprehensive font):
    #     print (u":%s: %s" % (cat, u''.join(chars))).encode('utf8')
#@-leo
