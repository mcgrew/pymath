"""
fraction.py
(c) 2007 Thomas McGrew

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
"""

from __future__ import division # forward compatibility. I don't like this change, but I want to make sure things work in python 3.0
import types
from sys import maxint as MAXINT

VERSION = "0.1"

FRACTION_VALID_TYPES = ( types.IntType, types.LongType, types.ComplexType, types.FloatType )
FRACTION_FLOAT_ACCURACY = 8 # how many decimal places to round floats to. This may be overidden to increase/decrease accuracy, but don't make it too large.


class fraction( object ):
	"""
	A class for dealing with fractions
	"""

	def __init__( self, *arg ):
		"""
		Constructor. Takes either 2 ints ( or longs ) or a fraction. Passing the constructor a
		fraction simply makes a copy of the original.

		:Parameters:
			arg : int
				A series of arguments
		"""
		if ( len( arg ) == 2 ):
			# if one of the arguments is a fraction:
			if ( type( self ) in ( type( arg[ 0 ] ), type( arg[ 1 ] ) ) ):
				# future division is broken, so simple division doesn't work here.
				if ( type( self ) == type( arg[ 0 ] ) == type( arg[ 1 ] ) ):
					 self.numerator = arg[ 0 ].numerator * arg[ 1 ].denominator
					 self.denominator = arg[ 0 ].denominator * arg[ 1 ].numerator
				elif ( type( self ) == type( arg[ 0 ] ) ):
					self.numerator = arg[ 0 ].numerator
					self.denominator = arg[ 0 ].denominator * arg[ 1 ]
				else: #( type( self ) == type( arg[ 1 ] ) ):
					self.numerator = arg[ 0 ] * arg[ 1 ].denominator
					self.denominator = arg[ 1 ].numerator
					
			elif ( type( arg[ 0 ] ) in FRACTION_VALID_TYPES ) and ( type( arg[ 1 ] ) in FRACTION_VALID_TYPES ):
				self.numerator = arg[ 0 ]
				if ( arg[ 1 ] ):
					self.denominator = arg[ 1 ]
				else:
					raise ZeroDivisionError( "Denominator of a fraction cannot be 0" )
			else:
				raise TypeError( "Invalid type for Fraction Constructor" )

		elif ( len( arg ) == 1 ):
			if ( type( arg[ 0 ] ) in FRACTION_VALID_TYPES ):
				 self.numerator = arg[ 0 ]
				 self.denominator = 1
			elif ( type( arg[ 0 ] ) == type( self ) ): # if the argument is a fraction, copy it.
				self.numerator = arg[ 0 ].numerator
				self.denominator = arg[ 0 ].denominator
			else:
				try: # check to see if the object has a __fraction__ method that returns a fraction. If not, raise an error.
					f = arg[ 0 ].__fraction__( )
				except AttributeError:
					raise TypeError( "Invalid type for fraction constructor" )
				if ( type( f ) == type( self ) ):
					self = f
				else:
					raise TypeError( "__fraction__( ) method returns incorrect data type for fraction constructor" )
		elif not len( arg ):
			self.numerator = 0
			self.denominator = 1
		else:
			raise TypeError( "fraction constructor takes at most 2 arguments (%d given)" % len( arg ) )

		#eliminate any float values, we don't need floats in a fraction.
		if ( types.FloatType in ( type( self.numerator ), type( self.denominator ) ) ):
			self.numerator, self.denominator = self._noFloats( self.numerator, self.denominator )
			
		self._reduce( )

	def _noFloats( self, numerator, denominator ):
		"""
		Internal Function - eliminates any float values in the fraction without losing [much if any] accuracy
		"""
		if ( type( numerator ) == types.ComplexType ):
			numerator *= ( 10 ** FRACTION_FLOAT_ACCURACY )
		else:
			numerator = long( round( numerator * ( 10 ** FRACTION_FLOAT_ACCURACY ) ) )
		if ( type( denominator ) == types.ComplexType ):
			denominator *= ( 10 ** FRACTION_FLOAT_ACCURACY )
		else:
			denominator = long( round( denominator * ( 10 ** FRACTION_FLOAT_ACCURACY ) ) )
		return numerator, denominator


	def _reduce( self ):
		"""
		Internal Function: reduces the fraction to it's simplest form.
		"""
		numFactors = self._factor( self.numerator )
		denFactors = self._factor( self.denominator )
		i = j = 0
		while ( i < len( numFactors ) ):
			j = 0
			while ( j < len( denFactors ) ):
				if ( numFactors[ i ] == denFactors[ j ] ):
					self.numerator /= numFactors[ i ]
					self.denominator /= denFactors[ j ]
					numFactors.pop( i )
					denFactors.pop( j )
					j = 0
				else:
					j+=1
				if ( i >= len( numFactors ) ): #make sure that wasn't the last factor
					break
			i+=1
		# we can sometimes simplify complex fractions more if the denominator has no real component
		if ( type( self.denominator ) == types.ComplexType ) and not ( self.denominator.real ):
			self.numerator *= -1j
			self.denominator *= -1j

		# convert each part to an int/long/float if there is no imaginary part.
		if ( type( self.numerator ) == types.ComplexType ) and not ( self.numerator.imag ):
			if ( self.numerator.real == long( self.numerator.real ) ): # if this is an even value
				self.numerator  = long( self.numerator.real ) 
			else: self.numerator = self.numerator.real
		if ( type( self.denominator ) == types.ComplexType ) and not ( self.denominator.imag ):
			if self.denominator == long( self.denominator.real ): #if this is an even value
				self.denominator = long( self.denominator.real )
			else: self.denominator = self.denominator.real

		# convert these back to long if they are not complex
		if ( type( self.numerator ) != types.ComplexType ): self.numerator = long( self.numerator )
		if ( type( self.denominator ) != types.ComplexType ): self.denominator = long( self.denominator )

		# convert the longs to int if they are small enough.
		if ( type( self.numerator ) == types.LongType and self.numerator < MAXINT ):
			self.numerator = int( self.numerator )
		if ( type( self.numerator ) == types.LongType and self.denominator < MAXINT ):
			self.denominator = int( self.denominator )

		# somehow I may need to reduce the complex values more, frac + frac doesn't always return the same
		# fraction as frac * 2 if the values are complex, though the two fractions are equal. I don't see
		# any obvious way to make them look the same( though they test for equality correctly ).

	def _factor( self, value ):
		"""
		Internal Function: determines the whole numer factors of a number.

		:Parameters:
			value : int
				The number to find the factors of

		:rtype: list
		:returns: A list containing the prime factors of value
		"""
		if not value:
			return list( )
		returnvalue = list( )
		if ( type( value ) == types.ComplexType ):
			if ( value.real == int( value.real ) ) and ( value.imag == int( value.imag ) ):
				realfactors = self._factor( int( value.real ) )
				imagfactors = self._factor( int( value.imag ) )
				if not value.real:
					imagfactors.append( 1j )
					return imagfactors
				if not value.imag:
					return realfactors
				# this should give us the union of the two lists.
		# there is a problem here somewhere.
				returnvalue = filter( lambda f:f in realfactors, imagfactors )
				returnvalue = filter( lambda f:f in returnvalue, realfactors )
				for v in returnvalue:
					value /= v
				returnvalue.append( value )
		else:
			if value < 0:
				value = -value
				returnvalue.append( -1 )
			i = 2
			while ( i*i <= value ):
				if not ( value % i ):
					returnvalue.append( i )
					value /= i
				else:
					i+=1
			if ( value > 1 ):
				returnvalue.append( value ) # at this point 'value' is a float, but it doesn't seem to affect things.
		return returnvalue

	def __abs__( self ):
		"""
		Returns the absolute value of this fraction

		:rtype: fraction
		:returns: The absolute value of this fraction
		"""
		if ( self < 0 ): return -self
		else: return self

	def __add__( self, value ):
		"""
		Fraction addition.

		call: frac + frac; frac + int; frac + float

		:Parameters:
			value : int
				The value to multiply this fraction by.

		:rtype: fraction, int or float
		:returns: The result of addition
		"""
		if ( type( value ) == type( self ) ):
			newNumerator = self.numerator * value.denominator + value.numerator * self.denominator
			newDenominator = self.denominator * value.denominator
			returnvalue = fraction( newNumerator, newDenominator )
			if ( returnvalue.denominator == 1 ):
				return returnvalue.numerator
			if not ( returnvalue.numerator ):
				return 0
			else: return returnvalue
			
##		elif ( type( value ) == types.FloatType ):
##		   return value + float( self )

		elif ( type( value ) in FRACTION_VALID_TYPES ):
			returnvalue = self + fraction( value )
			if ( type( returnvalue ) != type( self ) ) or returnvalue.numerator:
				return returnvalue
			else: return 0
			
		else: return NotImplemented

	def __div__( self, value ):
		"""
		Fraction division.

		call: frac / frac; frac / int; frac / float

		:Parameters:
			value : fraction, float, or int
				The value to multiply the fraction by.

		:rtype: fraction, int, or float
		:returns: The result of division
		"""
		if ( type( value ) == type( self ) ):
			returnvalue = self * ~value
			if ( returnvalue.denominator == 1 ):
				return returnvalue.numerator
			else:
				return returnvalue

		elif ( type( value ) in FRACTION_VALID_TYPES ):
			returnvalue = fraction( self.numerator , self.denominator * value )
			if ( returnvalue.denominator == 1 ):
				return returnvalue.numerator
			else:
				return returnvalue
		elif ( type( value ) == types.FloatType ):
			return ( self.numerator / ( self.denominator * value ) )
		else:
			return NotImplemented

		def __divmod__( self, value ):
			return ( self / value, self % value )

	def __float__( self ):
		"""
		Converts the fraction to a float value

		:rtype: float
		:returns: The float eauivalent of this fraction
		"""
		if ( types.ComplexType in ( type( self.numerator ), type( self.denominator ) ) ):
			n,d = self.numerator, self.denominator
			if ( type( n ) == types.ComplexType ): n = abs( n )
			if ( type( d ) == types.ComplexType ): d = abs( d )
			return n / d
		return float( self.numerator ) / self.denominator

	def __eq__( self, value ):
		"""
		Returns true if the value passed in is equal to this fraction

		:rtype: boolean
		:returns: True if the values are equal
		"""
		if ( type( self ) == type( value ) ):
			selfval, valueval = self.numerator / self.denominator, value.numerator / value.denominator
			if ( types.ComplexType in ( type( selfval ), type( valueval ) ) ):
				if not ( types.ComplexType == type( selfval ) == type( valueval ) ):
					return False
				return ( round( selfval.real, FRACTION_FLOAT_ACCURACY ) == round( valueval.real, FRACTION_FLOAT_ACCURACY ) ) and \
					   ( round( selfval.imag, FRACTION_FLOAT_ACCURACY ) == round( valueval.imag, FRACTION_FLOAT_ACCURACY ) )
			return round( self.numerator / self.denominator, FRACTION_FLOAT_ACCURACY ) == round( value.numerator / value.denominator, FRACTION_FLOAT_ACCURACY )

		elif ( type( value ) in ( types.IntType, types.LongType ) ):
			return long( self ) == value

		elif ( type( value ) == types.FloatType ):
			   return round( float( self ), FRACTION_FLOAT_ACCURACY ) == round( value, FRACTION_FLOAT_ACCURACY )
			
		elif ( type( value ) == types.ComplexType ):
			selfval = self.numerator / self.denominator
			if not ( type( selfval ) == types.ComplexType ):
					return False
			return ( round( selfval.real, FRACTION_FLOAT_ACCURACY ) == round( value.real, FRACTION_FLOAT_ACCURACY ) ) and \
				   ( round( selfval.imag, FRACTION_FLOAT_ACCURACY ) == round( value.imag, FRACTION_FLOAT_ACCURACY ) )

			return ( self.numerator / self.denominator ) == value

		else:
			return NotImplemented

	def __ge__( self, value ):
		"""
		Returns true if the value is greater than or equal to this object

		:Parameters:
			value : fraction, float, long, int
			The value to compare this fraction to

		:rtype: boolean
		:returns: True if this fraction's value is greater than or equal to the passed-in value
		"""
		return ( self > value ) or ( self == value )

	def __gt__( self, value ):
		"""
		Returns true if the value is greater than this object

		:Parameters:
			value : fraction, float, long, int
			The value to compare this fraction to

		:rtype: boolean
		:returns: True if this fraction's value is greater than the passed-in value
		"""
		if ( type( value ) == types.ComplexType ):
			return NotImplemented
		if ( type( value ) == type( self ) ):
			return ( self.numerator * value.denominator ) > ( self.denominator * value.numerator )
		else:
			return( self.numerator ) > ( self.denominator * value )
			
	def __int__( self ):
		"""
		Converts the fraction to an integer value

		:rtype: int
		:returns: The integer equivalent of this fraction ( rounded down )
		"""
		returnvalue =  self.numerator / self.denominator
		if ( type( returnvalue ) == types.ComplexType ):
			returnvalue = int( abs( returnvalue ) )
		else:
			returnvalue = int( returnvalue )
		return returnvalue

	def __invert__( self ):
		return fraction( self.denominator, self.numerator )

	def __le__( self, value ):
		"""
		Returns true if the value is less than or equal to this object

		:Parameters:
			value : fraction, float, long, int
			The value to compare this fraction to

		:rtype: boolean
		:returns: True if this fraction's value is less than or equal to the passed-in value
		"""
		return ( self < value ) or ( self == value )

	def __long__( self ):
		"""
		Converts the fraction to a long value

		:rtype: long
		:returns: The long representation of this fraction( rounded down )
		"""
		returnvalue =  self.numerator / self.denominator
		if ( type( returnvalue ) == types.ComplexType ):
			returnvalue = long( abs( returnvalue ) )
		else:
			returnvalue = long( returnvalue )
		return returnvalue

	def __lt__( self, value ):
		"""
		Returns true if the value is less than this object

		:Parameters:
			value : fraction, float, long, int
			The value to compare this fraction to

		:rtype: boolean
		:returns: True if this fraction's value is less than the passed-in value
		"""
		if ( type( value ) == types.ComplexType ):
			return NotImplemented
		if ( type( value ) == type( self ) ):
			return ( self.numerator * value.denominator ) < ( self.denominator * value.numerator )
		else:
			return( self.numerator ) < ( self.denominator * value )

	def __mod__( self, value ):
		"""
		Takes the modulus of this fraction

		:rtype: fraction
		:returns: The modulus of this fraction
		"""
		if ( type( value ) == type( self ) ):
			returnvalue = fraction( self )
			if ( returnvalue < 0 ):
				while ( returnvalue < -value ): returnvalue += value
			else:
				while ( returnvalue > value ): returnvlaue -= value
			return returnvalue
		elif ( type( value ) in ( types.IntType, types.LongType ) ):
			return fraction( self.numerator % ( value * self.denominator ), self.denominator )
		elif ( type ( value ) == types.FloatType ):
			return float( self ) % value
		else: return NotImplemented


	def __mul__( self, value ):
		"""
		Fraction multiplication.

		call: frac * frac; frac * int; frac * float

		:Parameters:
			value : fraction, float, or int
				The value to multiply the fraction by.
		:rtype: fraction, float or int
		:returns: The product of the operation.
		"""
		if ( type( value ) == type( self ) ):
			return fraction( self.numerator * value.numerator, self.denominator * value.denominator )
			if ( returnvalue.denominator == 1 ):
				return returnvalue.numerator
			else:
				return returnvalue

		elif ( type( value ) in FRACTION_VALID_TYPES ):
			returnvalue = fraction( self.numerator * value, self.denominator )
			if ( returnvalue.denominator == 1 ):
				return returnvalue.numerator
			else:
				return returnvalue

		elif ( type( value ) == types.FloatType ):
			return ( value * self.numerator / self.denominator )
		else:
			return NotImplemented

	def __ne__( self, value ):
		"""
		Returns true if the values are not equal

		:rtype: boolean
		:returns: True if the values are not equal
		"""
		return not ( self == value )

	def __neg__( self ):
		"""
		Changes the fraction to it's additive inverse ( negative )
		"""
		return fraction( -self.numerator, self.denominator )

	def __nonzero__( self ):
		"""
		Returns true if the fraction is not equal to zero

		:rtype: boolean
		:returns: True if the fraction is not equal to zero
		"""
		return bool( self.numerator )

	def __pos__( self ):
		"""
		The positive of the fraction, basicallly a copy of itself

		:rtype: fraction
		:returns: A copy of itself
		"""
		return fraction( self )

	def __pow__( self, power ):
		"""
		Raise this fraction to a power

		:rtype: fraction
		:returns: The result of raising this fraction to a power
		"""
		if ( power > 0 ):
			return fraction( self.numerator ** power, self.denominator ** power )
		if ( power < 0 ):
			return fraction( self.denominator ** abs( power ), self.numerator ** abs( power ) )
		return 1

	def __radd__( self, value ):
		"""
		Fraction addition.

		call: frac + frac; int + frac; float + frac

		:Parameters:
			value : int
				The value to multiply this fraction by.

		:rtype: fraction, int or float
		:returns: The result of addition
		"""
		return self + value

	def __rdiv__( self, value ):
		"""
		Fraction division.

		call: frac / frac; int / frac ; float / frac

		:Parameters:
			value : fraction, float, or int
				The value to multiply the fraction by.

		:rtype: fraction, int, or float
		:returns: The result of division
		"""
		return self.inverse( ) * value

	def __repr__( self ):
		"""
		Returns a string representation of the fraction.

		:rtype: string
		:returns: A string representation of the fraction
		"""
		return ( "%s/%s" % ( self.numerator, self.denominator ) )

	def __rmul__( self, value ):
		"""
		Fraction multiplication.

		call: frac * frac; int * frac; float * frac

		:Parameters:
			value : fraction, float, or int
				The value to multiply the fraction by.
		:rtype: fraction, float or int
		:returns: The product of the operation.
		"""
		return self * value

	def __rsub__( self, value ):
		"""
		Fraction addition.

		call: frac - frac; int - frac; float - frac

		:Parameters:
			value : int
				The value to multiply this fraction by.

		:rtype: fraction, int or float
		:returns: The result of subtraction
		"""
		return ( -self ) + value

	__str__ = __repr__

	def __sub__( self, value ):
		"""
		Fraction addition.

		call: frac - frac; frac - int

		:Parameters:
			value : int
				The value to multiply this fraction by.

		:rtype: fraction, int or float
		:returns: The result of subtraction
		"""

		return self + ( -value )

	def inverse( self ):
		"""
		Returns the multiplicative inverse of this fraction

		:rtype: fraction
		:returns: The multiplicative inverse of this fraction
		"""
		return fraction( self.denominator, self.numerator )

