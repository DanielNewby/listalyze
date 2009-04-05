#!/usr/bin/env python
'''Adapt list of "numbers" to HTML <OL> element.

It is safe to do ``from listalyze import *``.  Only the
``listalyze()`` function will be imported.

To use, simply place this file in a directory that is on the
search path or is listed in the ``PYTHONPATH`` environment
variable.

This file is copyright 2009 by Daniel A. Newby who grants the
possessor a perpetual, irrevocable, sublicensable, royalty-free
license to use, modify, and distribute copies (including
modified copies) of this file provided this license grant is
attached to each copy.  A violator may completely remedy breach
of this license by ceasing further violation and reattaching
this statement to all copies they easily can.

Execute this file from the command line to run some unit tests:
    > ./listalyze.py

Maintainer:
    Daniel A. Newby
    dn@teco-xaco.com
'''

__version__ = '1.0.0'
__release_data__ = '2009-04-04'

__all__ = [
	'listalyze',
]


from copy import copy
import string


# Converters for numbering schemes.
def convert_decimal( number ):
	return int( number )

def convert_lower_alpha( number ):
	result = 0
	for ch in number:
		result *= 26
		result += ord(ch) - ord('a') + 1
	return result

def convert_upper_alpha( number ):
	result = 0
	for ch in number:
		result *= 26
		result += ord(ch) - ord('A') + 1
	return result

def convert_mixed_alpha( number ):
	return convert_upper_alpha( number.upper() )

scheme_converters = {
	u'decimal'     : convert_decimal,
	u'lower-alpha' : convert_lower_alpha,
	u'upper-alpha' : convert_upper_alpha,
	u'mixed-alpha' : convert_mixed_alpha,
}


# Character sets for numbering schemes.
scheme_character_sets = {
	u'decimal' : set( [unicode(ch) for ch in string.digits] ),
	
	u'lower-alpha' : set( [unicode(ch) for ch in string.ascii_lowercase] ),
	
	u'upper-alpha' : set( [unicode(ch) for ch in string.ascii_uppercase] ),
	
	u'mixed-alpha' : set( [unicode(ch) for ch in
		(string.ascii_lowercase + string.ascii_uppercase)] ),
}
all_scheme_names = set( scheme_character_sets )

# Notes for future expansion of character sets:
#	Roman numerals:  in addition to the normal English characters like 'M'
#	that can be used for Roman numberals, Unicode defines several Roman
#	numeral-specific characters like U+216F.  The bastards.
#		See http://www.w3.org/TR/css3-lists/#list-content


def categorize_number( number ):
	'''Returns the set of number scheme names that the number
	might be part of.
	
	For example, categorize_number( u'i' ) would return
	set( [u'lower-alpha', u'lower-roman'] ) (assuming Roman
	numerals were supported yet.)
	'''
	schemes = copy( all_scheme_names )
	for scheme_name in scheme_character_sets:
		charset = scheme_character_sets[scheme_name]
		for ch in number:
			if ch not in charset:
				schemes.remove( scheme_name )
				break
	return schemes


def listalyze( numbers, require_dot = True, mixed_case = False ):
	'''Figures out how to make an HTML ``<OL>`` element
    (numbered list) match a list of numbers.  The recognized
    number schemes include both proper numbers (1, 2, 3, ...)
    as well as other sequences such as alphabets (A, B, C, ...).
    
    `numbers` is an iterable producing a sequence of Unicode
    strings, such as the list ``[u'A.', u'B.', u'D.']``.  Its
    values are all loaded into memory at the same time, so they
    had better fit.  Leading and trailing whitespace on numbers
    are ignored.
    
    `require_dot` is a boolean that says whether each input
    number must have a trailing period character (".").  If
    true, no numbering scheme will be recognized if any number
    lacks a trailing period.  If false, trailing periods are
    ignored if present.
    
    `mixed_case` is a boolean that says whether to accept
    letter-using numbering schemes without regard to case
    differences (lowercase versus uppercase).  If true,
    ``listalyze`` does not distinguish between case; the
    `numbering_type` return value is given in the upper case
    variant; the caller must manually change it to lowercase if
    desired.  If false, ``listalyze`` distinguishes case;
    `numbers` = [u'a.', u'B.'] would be considered an invalid
    numbering scheme and the `numbering_type` return value
    would be ``None``.
    
    Returns a ``(numbering_type, value_list, default_order)``
    tuple.
    
    `numbering_type`:
        If ``None``, the `numbers` did not fit a supported numbering
        scheme.  `value_list` is a list containing the elements
        from `numbers`; it may be used to render the list into a
        fallback HTML element such as a ``<TABLE>``.
        
        Otherwise `numbering_type` is a string that describes
        the numbering scheme in use, such as u'decimal'.
        `value_list` is a list containing the elements converted
        into ordinal numbers.  For example, if `numbers`
        produces ``[u'A.', u'B.', u'D.']``, then `value_list`
        will be ``[1, 2, 4]``.
        
        The values for `numbering_type` are taken from the
        CSS 2.1 ``list-style-type`` property:
        http://www.w3.org/TR/CSS21/generate.html#propdef-list-style-type
    
    `value_list` is a list of the numbers (raw or converted) as
    described above.  These are always unicode strings.
    
    `default_order` is True if the `numbers` were a recognized
    type of ordinal and run from the default CSS 2.1 starting
    point with no skipped values.  This means that an HTML
    ``<OL>`` element would generate the same numbering without
    using the ``<LI>`` elements' ``VALUE`` attributes.  If
    False, then each ``<LI>`` element should have a ``VALUE``
    attribute taken from `value_list`.
    
    Example usage:
        >>> from listalyze import *
        >>> listalyze( [u'A.', u'B.', u'D.'] )
        (u'upper-alpha', [1, 2, 4], True)
        
    This example might be turned into this HTML:
        <OL STYLE="list-style-type: upper-alpha;">
            <LI VALUE="1">Item labeled "A."</LI>
            <LI VALUE="2">Item labeled "B."</LI>
            <LI VALUE="4">Item labeled "D."</LI>
        </OL>
    
    The ``VALUE`` attribute is deprecated by HTML 4.01.
    Unfortunately CSS 2.1 provides no way to manually set the
    value of a list item using styles, so compromises must be
    made.
    
    The following number schemes from CSS 2.1 are supported:
    
        ``decimal``: 1, 2, 3, ...
            Negative numbers are not supported.
        
        ``lower-alpha``: a, b, c, ..., z, aa, ab, ...
        
        ``upper-alpha``: A, B, C, ..., Z, AA, AB, ...
        
    These strings are defined in
    ``http://www.w3.org/TR/CSS21/generate.html#propdef-list-style-type``.
'''
	# Make list from `numbers` iterable.
	numbers_list = []
	try:
		numbers_list = [N for N in numbers]
	except TypeError:
		raise TypeError( '\'%s\' object is not iterable ("numbers" parameter)' %
			type( numbers ).__name__ )
	
	nl_iter = xrange( len( numbers_list ) )
	raw_numbers_list = copy( numbers_list )
	
	# Value to return when we don't recognize the numbering scheme.
	dont_recognize_scheme = (None, raw_numbers_list, False)
	
	# Only accept unicode strings.  This is to keep non-unicode stuff
	# from making it to an HTML generator.
	for i in nl_iter:
		number = numbers_list[i]
		if type(number) is not unicode:
			raise TypeError( '\'%s\' object is not a unicode string '\
				'(item with index %d returned from "numbers" iterable)' %
				(type( number ).__name__, i) )
		numbers_list[i] = number.strip()
	
	if require_dot:
		# Require a trailing dot on each number, and strip 'em all off.
		for i in nl_iter:
			number = numbers_list[i]
			if (len( number ) < 2) or (number[-1] != u'.'):
				return dont_recognize_scheme
			numbers_list[i] = number[:-1]
	else:
		# Strip trailing dots if they are there, otherwise do nothing.
		for i in nl_iter:
			if len( numbers_list[i] ) < 1:
				return dont_recognize_scheme
			if numbers_list[i][-1] == u'.':
				numbers_list[i] = numbers_list[i][:-1]
			if numbers_list[i] == u'':
				return dont_recognize_scheme
	
	# Categorize numbers and find set of schemes that matches them all.
	number_schemes = copy( all_scheme_names )
	for number in numbers_list:
		# "&" means intersection for sets.
		number_schemes &= categorize_number( number )
	
	# If mixed-case support is turned off, filter out mixed case schemes.
	if not mixed_case:
		if u'mixed-alpha' in number_schemes:
			number_schemes.remove( u'mixed-alpha' )
	
	# Don't use the mixed-alpha numbering scheme if an alternative scheme
	# matches.
	if (len( number_schemes ) > 1) and (u'mixed-alpha' in number_schemes):
		number_schemes.remove( u'mixed-alpha' )
	
	# If/when Roman number support is added, set can have two items, and
	# decision must be made to force it to 'alpha' or 'roman'.
	if len( number_schemes ) != 1:
		return dont_recognize_scheme
	
	# Convert numbers
	scheme = list(number_schemes)[0]
	converter = scheme_converters[scheme]
	default_order = True
	for i in nl_iter:
		numbers_list[i] = converter( numbers_list[i] )
		if numbers_list[i] != i + 1:
			default_order = False
	
	# Force mixed-case numbering schemes to upper case.  (It looks good
	# and saves work for the 99.9% of callers who don't care.)
	if scheme == u'mixed-alpha':
		scheme = u'upper-alpha'
	
	return (scheme, numbers_list, default_order)


# Test the code.
if __name__ == "__main__":
	import sys
	
	def fail( msg ):
		print 'Test failure:', msg
		sys.exit( 1 )
		
	print 'Testing listalyzer.py ...'
	
	try:
		listalyze( 14 )
	except TypeError, err:
		pass
	else:
		fail( 'accepted non-iterator "numbers"' )
	
	try:
		listalyze( [u'1', '2', u'3'] )
	except TypeError, err:
		pass
	else:
		fail( 'accepted non-Unicode number.' )
	
	result = listalyze( [u'1.', u'2'] )
	if result[0] != None:
		fail( 'accepted non-dotted number with require_dot = True' )
	if result[1] != [u'1.', u'2']:
		fail( 'altered return results even when no numbering scheme '
			'recognized' )
	
	result = listalyze( [u'1.', u'2'], False )
	if result[0] == None:
		fail( 'rejected non-dotted number with require_dot = False' )
	if result[2] != True:
		fail( 'failed to recognize numbers in canonical order' )
	
	result = listalyze( [u'1', u'2', u'4'], False )
	if result[0] != u'decimal':
		fail( 'failed to recognize decimal numbering scheme' )
	if result[2] != False:
		fail( 'failed to recognize numbers in non-canonical order' )
	
	result = listalyze( [u'1', u'9', u'10', u'11', u'99', u'100', u'101',
		u'999', u'1000', u'1001'], False )
	if result[1] != [1, 9, 10, 11, 99, 100, 101, 999, 1000, 1001]:
		fail( 'failed to convert numbers accurately' )
	
	result = listalyze( [u'a', u'b', u'c.', u'z', u'aa', u'ab', u'az', u'ba'],
		False )
	if result[0] != u'lower-alpha':
		fail( 'failed to recognize lower-alpha numbering scheme' )
	if result[1] != [1, 2, 3, 26, 27, 28, 52, 53]:
		fail( 'failed to convert lowercase letters accurately' )
	
	result = listalyze( [u'A', u'B', u'C.', u'Z', u'AA', u'AB', u'AZ', u'BA'],
		False )
	if result[0] != u'upper-alpha':
		fail( 'failed to recognize upper-alpha numbering scheme' )
	if result[1] != [1, 2, 3, 26, 27, 28, 52, 53]:
		fail( 'failed to convert uppercase letters accurately' )
	if result[2] != False:
		fail( 'failed to recognize numbers in non-canonical order' )
	
	result = listalyze( [unicode(chr(ord('a') + i)) for i in xrange(26)] +
		[u'aa', u'ab'],
		False )
	if result[1] != [i + 1 for i in xrange( 28 )]:
		fail( 'failed to convert uppercase letters accurately' )
	if result[2] != True:
		fail( 'failed to recognize numbers in canonical order' )
	
	result = listalyze( [u'1.', u'a.'] )
	if result[0] != None:
		fail( 'improperly accepted mixed scheme numbers' )
	
	result = listalyze( [u'1.', u'A.'] )
	if result[0] != None:
		fail( 'improperly accepted mixed scheme numbers' )
	
	result = listalyze( [u'a.', u'1.'] )
	if result[0] != None:
		fail( 'improperly accepted mixed scheme numbers' )
	
	result = listalyze( [u'a.', u'B.'], mixed_case = False )
	if result[0] != None:
		fail( 'improperly accepted mixed case alphabetic numbering' )
	
	result = listalyze( [u'a.', u'B.'], mixed_case = True )
	if result[0] != u'upper-alpha':
		fail( 'improperly rejected mixed case alphabetic numbering' )
	
	print 'Tests successful.'
	print 'Exiting.'
	
	sys.exit( 0 )

