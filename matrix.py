"""
matrix.py
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

import types
from sys import argv
import os

VERSION = "0.2-rc2"

MATRIX_VALID_TYPES = ( types.IntType, types.FloatType, types.LongType, types.ComplexType )
MATRIX_VALID_TYPENAMES = ( 'int', 'float', 'long', 'complex' )
MATRIX_VALID_INTS = ( types.IntType, types.LongType )
MATRIX_VALID_COLLECTIONS = ( types.ListType, types.TupleType )
MATRIX_USE_FRACTION = False

# add the fraction class if it is available
if os.path.exists( os.path.join( os.path.abspath( os.path.dirname( argv[ 0 ] ) ), "fraction.py" ) ):
    import fraction as _fraction
    MATRIX_USE_FRACTION = True
    MATRIX_VALID_TYPES = MATRIX_VALID_TYPES + ( type( _fraction.fraction( 1, 2 ) ), )
    MATRIX_VALID_TYPENAMES += ( 'fraction', )


class matrix( object ):
    """
    A class for matrix operations. All indices start at 0.
    """

    def __init__( self, *rows ):
        """
        Accepts either a matrix, a 2-dimensional list of numbers,
        a list with a matrix width ( int ), or a series of one-dimensional lists of numbers.
        
        :Parameters:
            rows : list
                Arguments for creating a matrix.
        """
        self._width = 0
        self._height = 0
        self._value = list( )

        if rows:
            # if the value passed into the constructor is a matrix
            if ( ( len( rows ) == 1 ) and ( type( rows[ 0 ] ) == type( self ) ) ):
                for row in rows[ 0 ].value:
                    newRow = list( )
                    for item in row: # this should make a deep copy.
                        newRow.append( item )
                    self.addRow( *newRow )
            # if the value passed into the constructor is a two-dimensional list
            elif ( ( len( rows ) == 1 ) and ( type( rows[ 0 ] ) in MATRIX_VALID_COLLECTIONS ) and ( type( rows[ 0 ][ 0 ] in MATRIX_VALID_COLLECTIONS ) ) ):
                for row in rows[ 0 ]:
                    newRow = list( )
                    for item in row: # this should make a deep copy.
                        newRow.append( item )
                    self.addRow( *newRow )
            # if the value passed into the constructor is a list followed by a matrix width
            elif ( ( len( rows ) == 2 ) and ( type( rows[ 0 ] ) in MATRIX_VALID_COLLECTIONS ) and ( type( rows[ 1 ] ) in MATRIX_VALID_INTS ) ):
                if ( len( rows[ 0 ] ) % rows[ 1 ] ):
                    raise ValueError( 'Invalid list length for matrix construction, must be a multiple of width argument' )
                newRow = list( )
                for i in range( len( rows[ 0 ] ) ):
                    if ( i and ( not i % rows[ 1 ] ) ): # i > 0 and a multiple of the given width.
                        self.addRow( *newRow )
                        newRow = list( )
                    newRow.append( rows[ 0 ][ i ] )
                #when we get here, there should still be one row left in the "buffer", so
                self.addRow( *newRow )
            # if the value passed into the constructor is several lists
            else:
                for row in rows:
                    if not ( type( row ) in MATRIX_VALID_COLLECTIONS ):
                        raise TypeError( "Constructor arguments must be of type 'list' or 'tuple'" ) # fix this!
                    self.addRow( *row )
                    

    def __abs__( self ):
        """
        Absolute value.

        Call:  abs( matrix )

        :rtype: matrix
        :returns: a copy of the matrix with all values changed to their absolute value
        """
        returnvalue = matrix( )
        for row in self._value:
            newRow = list()
            for item in row: # this should make a deep copy.
                newRow.append( abs( item ) )
            returnvalue.append( newRow )
        return returnvalue

    def __add__( self, obj ):
        """
        Addition. Requires matrices of the same size.
        
        Call:  mat1 + mat2

        :rtype: matrix
        :returns: The result of adding mat1 and mat2 ( Linear Algebra )
        """
        if not ( type( self ) == type( obj ) ):
            return NotImplemented
        if not ( self.size == obj.size ):
            raise matrixSizeError( "Matrices must be the same size for '+'" )
        returnvalue = matrix( )
        for i in range( self._height ):
            currentRow = list( )
            for j in range( self._width ):
                currentRow.append( self._value[ i ][ j ] + obj.value[ i ][ j ] )
            returnvalue.addRow( *currentRow )
        return returnvalue

    def __contains__( self, item ):
        """
        Contains.

        Call:  if x in matrix:

        :Parameters:
            item : number
                The number to look for.
                
        :rtype: boolean
        :returns: True if a value is contained in the matrix.
        """
        for row in self._value:
            for i in row:
                if i == item:
                    return True
        return False

    def __div__( self, obj ):
        """
        Division.

        Call: matrix / x

        :Parameters:
            obj : number
                The number to divide each item in the matrix by.
        """
        if ( type( obj ) in MATRIX_VALID_TYPES):
            returnvalue = matrix( )
            for row in self._value:
                newRow = list( )
                for item in row:
                    if ( MATRIX_USE_FRACTION ):
                        newItem = _fraction.fraction( item, obj )
                    else:
                        newItem = item / obj
                    # convert all of the round values to int.
                    if ( type( newItem ) != types.ComplexType ) and ( round( newItem, 4 ) == long( newItem ) ):
                        if not ( MATRIX_USE_FRACTION and ( type( newItem ) == type( _fraction.fraction( 1, 2 ) ) ) ):
                            newItem = int( round( newItem ) )
                    newRow.append( newItem )
                returnvalue.addRow( *newRow )
            return returnvalue
        else:
            return NotImplemented

    def __divmod__( self, value ):
        """
        Division / Modulus

        Call: divmod( matrix )

        :Parameters:
            value : number
                The value to mod/divide the matrix by.
            
        :rtype: tuple
        :returns: A 2 item tuple containing the matrix after division in item 0 \
        and the matrix after modulus in item 1.
        """
        return tuple( self.__div__( value ), self.__mod__( value ) )

    def __float__( self ):
        """
        Convert to Float

        Call: float( matrix )

        :rtype: matrix
        :returns: returns the determinant as a float value.
        """
        return float( self.determinant( ) )

    def __eq__( self, matrix ):
        """
        Equality

        Call: mat1 == mat2

        :Parameters:
            matrix : matrix
                The matrix to compare this matrix to
            
        :rtype: boolean
        :returns: True if the matrices are identical
        """
        if not ( type( self ) == type( matrix ) ):
            return NotImplemented
        if not ( self.size == matrix.size ):
            return False
        for i in range( self._height ):
            for j in range( self._width ):
                if not ( self.value[ i ][ j ] == matrix.value[ i ][ j ] ):
                    return False
        return True

    def __getattr__( self, name ):
        """
        Get attribute.

        Call: mat.value; mat.width; mat.height; mat.size

        :Parameters:
            name : string
                The object property to get
            
        :rtype: int, list, or tuple
        :returns: The value requested.
        """
        # these should return copies, not the objects themselves.
        if name == 'width':
            return int( self._width )
        if name == 'height':
            return int( self._height )
        if name == 'value':
            return list( self._value )
        if name == 'size':
            return ( int( self._width ), int( self._height ) )

    def __getitem__( self , index ):
        """
        For getting parts of the matrix, mat[x] or mat[x][y]. The 'y' part will be
        handled by the list item returned.

        Call: matrix[x] or matrix[x][y]

        :Parameters:
            index : int
                The row requested.
            
        :rtype: list
        :returns: The row requested, not a copy thereof, which means modifying the return \
        value will modify the matrix object, so be careful with this.
        """
        if not ( type( index ) in MATRIX_VALID_INTS ):
            return NotImplemented
        return self._value[ index ]

    def __int__( self ):
        """
        Integer cast.

        Call: int( matrix );

        :rtype: int
        :returns: the determinant of the matrix
        """
        return int( self.determinant( ) )

    # not sure if this method is a good idea.
    def __invert__( self ):
        """
        Usually used for binary inversion, here returns the inverse of the matrix.

        Call: ~matrix

        :rtype: matrix
        :returns: The inverse of the matrix.
        """
        return self.inverse( )

    def __iter__( self ):
        """
        Simple iterator method

        Call: for x in mat:, list( mat ), etc.

        :rtype: matrix
        :returns: self
        """
        self._iterpos = 0
        return self

    def __mod__( self, mod ):
        """
        Modulus operator

        Call: matrix % x

        :Parameters:
            mod : number
                The number to mod each item in the matrix by.
            
        :rtype: matrix
        :returns: A matrix with all items modded
        """
        if not ( type( mod ) in  MATRIX_VALID_TYPES):
            return NotImplemented
        returnvalue = matrix( )
        for i in range( self._height ):
            currentRow = list( )
            for j in range( self._width ):
                currentRow.append( self._value[ i ][ j ] % mod )
            returnvalue.addRow( *currentRow )
        return returnvalue
    
    def __mul__( self, obj ):
        """
        Multiplication

        Call: mat * mat, mat * x

        :Parameters:
            obj : number; matrix
                The number or matrix to multiply this matrix by.
                
        :rtype: matrix
        :returns: The result of the multiplication ( Linear Algebra )
        """
        returnvalue = matrix( )
        if ( type( obj ) in MATRIX_VALID_TYPES):
            for row in self._value:
                newRow = list( )
                for item in row:
                    newRow.append( item * obj )
                returnvalue.addRow( *newRow )
            return returnvalue
        if ( type ( obj ) == type ( self ) ):
            if not ( self._width == obj.height ):
                raise ValueError( "Matrices are the incorrect size for '*'" )
            else:
                for i in range( self._height ):
                    row = list()
                    for j in range( obj.width ):
                        item = 0
                        for k in range( self._width ):
                            item += self._value[ i ][ k ] * obj.value[ k ][ j ]
                        row.append( item )
                    returnvalue.addRow( *row )
                return returnvalue
        return NotImplemented
    
    def __ne__( self, matrix ):
        """
        Non-equality

        Call: matrix1 != matrix2

        :Parameters:
            matrix : matrix
                The matrix to compare this matrix to.

        :rtype: boolean
        :returns: True if the matrices are NOT equal
        """
        return not __eq__( matrix )
    
    def __neg__( self ):
        """
        Negative of a matrix

        :rtype: matrix
        :returns: A matrix with the sign of each item changed.
        """
        return self.__mul__( -1 )

    def __nonzero__( self ):
        """
        Nonzero.

        Call: bool( matrix )
        
        :rtype: boolean
        :returns: True if this is not a zero matrix
        """
        for row in self._value:
            for item in row:
                if item:
                    return True
        return False

    def __pos__( self ):
        """
        Positive

        Call: +matrix

        :rtype: matrix
        :returns: A copy of itself.
        """
        return matrix( self )

    def __pow__( self, power ):
        """
        Power. This is only valid for square matrices

        Call: mat ** x or pow( mat, x )
        
        :Parameters:
            power : int
                The power to raise this matrix to
            
        :rtype: matrix
        :returns: The result of the calculation ( Linear Algebra )
        """
        if not ( type( power ) in  ( types.IntType, types.LongType ) ):
            return NotImplemented
        if not self.isSquare( ):
            raise ValueError( "Power invalid for non-square matrices" )
        if ( power > 0 ):
            p = power
            returnvalue = matrix( self )
        elif ( power < 0 ):
            p =  -power
            returnvalue = self.inverse( )
        elif ( power == 0 ):
            return NotImplemented
        for i in range( p - 1 ):
            returnvalue *= returnvalue
        return returnvalue

    def __repr__( self ):
        """
        Representation. Formats the matrix for printing.

        Call: repr( matrix ); str( matrix )

        :rtype: string
        :returns: A formatted representation of this matrix.
        """
        returnvalue = str( )
        itemwidth = self._maxValueLength( )
        for i  in range( self._height ):
            if i:
                returnvalue += '\n'
            returnvalue += '['
            for j in range( self._width ):
                if type( self._value[ i ][ j ] ) == types.FloatType:
                    formatstring = " %%%d.3f " % ( itemwidth )
                else:
                    formatstring = " %%%ds " % itemwidth
                returnvalue += ( formatstring % self._value[ i ][ j ] )
            returnvalue += ']'
        return returnvalue

    def __rmul__( self, obj ):
        """
        Right side multiplication

        Call: x * mat

        :Parameters:
            obj : number
                The number to multiply this matrix by.
            
        :rtype: matrix
        :returns: The same as mat * x
        """
        if ( type( obj ) in MATRIX_VALID_TYPES ):
            return self.__mul__( obj )
        return NotImplemented

    __str__ = __repr__

    def __sub__( self, obj ):
        """
        Subtraction. Requires matrices of the same size.

        Call: mat1 - mat2

        :Parameters:
            obj : matrix
                The matrix to subtract from this matrix
                
        :rtype: matrix
        :returns: The result of the calculation ( Linear Algebra )
        """
        if not ( type( self ) == type( obj ) ):
            return NotImplemented
        if not ( self.size == obj.size ):
            raise ValueError( "Matrices must be the same size for '+'" )
        returnvalue = matrix( )
        for i in range( self._height ):
            currentRow = list( )
            for j in range( self._width ):
                currentRow.append( self._value[ i ][ j ] - obj.value[ i ][ j ] )
            returnvalue.addRow( *currentRow )
        return returnvalue

    def _maxValueLength( self ):
        """
        Get the string length of the longest item in the matrix.
        This is for formatting the output of __str__ and __repr__.

        :rtype: int
        :returns: The string length of the longest item in the matrix.
        """
        returnvalue = 0
        for row in self._value:
            for item in row:
                if ( type( item ) == type( float( ) ) ):
                    returnvalue = max(returnvalue, len(  '%.3f' % item ) )
                else:
                    returnvalue = max(returnvalue, len( str( item ) ) )
        return returnvalue

    def addColumn( self, *column ):
        """
        Adds a column to the matrix. This must be the same height as the current columns, if there are any.

        Call: matrix.addColumn( list ) or matrix.addColumn( item, item, item, ... )

        :Parameters:
            column : list
                The column to be inserted
        """
        self.insertRow( self._width, *column )

    def addRow( self, *row ):
        """
        Adds a row to the matrix. This must be the same width as the current rows, if there are any.

        Call: matrix.addRow( list ) or matrix.addRow( item, item, item, ... )

        :Parameters:
            row : list
                The row to be inserted
        """
        self.insertRow( self._height, *row )
        
    def adjoint( self ):
        """
        Adjoint of the matrix.

        :rtype: matrix
        :returns: The adjoint of this matrix.
        """
        return self.cofactormatrix( ).transpose( )

    # Aliases for adjoint    
    adj = adjugate = adjoint

    def approx( self ): #stub!
        """
        Approximates all values by converting fractions to floating point numbers
        """
        print "FIXME: This method has not yet been implemented"

    def cofactor( self, row, column ):
        """
        Cofactors. Only for square matrices

        :Parameters:
            row : int
                The row number
            column : int
                The column number
        :rtype: number
        :returns: The cofactor of the item at row, column.
        """
        if not self.isSquare( ):
            raiseValueError( "Cofactor is not defined for a non-square matrix" )
        return ( ( -1 ) ** ( row + column ) ) * self.minor( row, column )
                
    def cofactormatrix( self ):
        """
        The cofactor matrix. Only for square matrices.

        :rtype: matrix
        :returns: A matrix consisting of the cofactors of this matrix
        """
        returnvalue = matrix( )
        for i in range( self._height ):
            newRow = list( )
            for j in range( self._width ):
                newRow.append( self.cofactor( i, j ) )
            returnvalue.addRow( *newRow )
        return returnvalue
                
    def deleteColumn( self, column ):
        """
        Deletes a column from this matrix

        :Parameters:
            column : int
                The column number to delete ( Starting at 0 )
        """
        if ( column >= self._width or column <= -self._width ):
            raise IndexError( 'Invalid index, row %d does not exist' % column )
        returnvalue = list( )
        self._width -= 1
        for row in self._value:
            returnvalue.append( row.pop( column ) )
        return returnvalue

    def deleteRow( self, row ):
        """
        Deletes a row from this matrix

        :Parameters:
            row : int
                The row number to delete ( Starting at 0 )
        """
        if ( row >= self._height or row <= -self.height):
            raise IndexError( 'Invalid index, row %d does not exist' % row )
        self._height -= 1
        return self._value.pop( row )

    def determinant( self ):
        """
        Determinant. Only for square matrices.

        :rtype: number
        :returns: The determinant of this matrix
        """
        if not self.isSquare( ):
            raise ValueError( "Determinant is not defined for non-square matrix" )
        if ( self._height == 1 and self._width == 1):
            return self._value[ 0 ][ 0 ]
        returnvalue = 0
        for i in range( self._width ):
            returnvalue += self._value[ 0 ][ i ] * self.cofactor( 0, i )
        return returnvalue

    # An alias for determinant
    det = determinant
            
    def getColumn( self, column ):
        """
        Get a column from this matrix

        :Parameters:
            column : int
                The column to get.
            
        :rtype: list
        :returns: The column as a list
        """
        returnvalue = list( )
        for row in self._value:
            returnvalue.append( row[ column ] )
        return returnvalue

    def getRow( self, row ):
        """
        Get a row from this matrix

        :Parameters:
            row : int
                The row to get.
        :rtype: list
        :returns: The row as a list
        """
        returnvalue = list( )
        for item in self._value[ row ]:
            returnvalue.append( item )
        return returnvalue

    def hadamard( self, value ):
        """
        Takes the Hadamard product of two matrices.

        [ a  b ] . [ e  f ]  = [ a*e  c*f ]
        [ c  d ]   [ g  h ]    [ c*g  d*h ]

        :Parameters:
            value : matrix
                The matrix to use in finding the Hadamard product
        :rtype: matrix
        :returns: The Hadamard product of this matrix and the passed-in matrix.
        """
        if not ( type( self ) == type( value ) ):
            raise TypeError( "Inapproproate argument type for hadamard product" )
        if not( self.size == value.size ):
            raise ValueError( "Matrices must be of the same size for hadamard product" )

    def insertColumn( self, index, *column ):
        """
        Inserts a column into the matrix. This must be the same height as the current columns, if there are any.

        Call: matrix.insertColumn( index, list ) or matrix.insertColumn( index, item, item, item, ... )

        :Parameters:
            index : int
                The column number to insert the new column before.
            column : list
                The column to be inserted
        """
        if ( ( len( column ) == 1 ) and ( type( column[ 0 ] ) in MATRIX_VALID_COLLECTIONS ) ):
            column = column[ 0 ]
        if self._height:
            if not ( len( column ) == self._height ):
                raise ValueError( 'Improper length for new column: %d, should be %d' % (len( column ), self._height ) )
        else:
            self._height = len( column )
            for i in range( self._height ):
                self._value.append( list( ) )
        self._width += 1
        for i in range( self._height ):
            if not ( type( column[ i ] ) in MATRIX_VALID_TYPES):
                message = "Values must be of type "
                for t in range( len( MATRIX_VALID_TYPENAMES ) ):
                    if t:
                        message += ' or '
                    message += "'%s'" % MATRIX_VALID_TYPENAMES[ t ]
                raise TypeError( message )
            self._value[ i ].insert( index, column[ i ] )

    def insertRow( self, index, *row ):
        """
        Adds a row to the matrix. This must be the same width as the current rows, if there are any.

        Call: matrix.insertRow( list ) or matrix.insertRow( item, item, item, ... )

        :Parameters:
            index : int
                The row number to insert the new row before.
            row : list
                The row to be inserted
        """
        if ( ( len( row ) == 1 ) and ( type( row[ 0 ] ) in MATRIX_VALID_COLLECTIONS ) ):
            row = row[ 0 ]
        if self._width:
            if not ( len( row ) == self._width ):
                raise ValueError( 'Improper length for new row: %d, should be %d' % (len( row ), self._width ) )
        else:
            self._width = len( row )
        self._height += 1
        #make a deep copy
        newrow = list( )
        for item in row:
            if not ( type( item ) in MATRIX_VALID_TYPES ):
                message = "Values must be of type "
                for t in range( len( MATRIX_VALID_TYPENAMES ) ):
                    if t:
                        message += ' or '
                    message += "'%s'" % MATRIX_VALID_TYPENAMES[ t ]
                raise TypeError( message )
            newrow.append( item )
        self._value.insert( index, newrow )

    def inverse( self ):
        """
        Inverse.

        :rtype: matrix
        :returns: The inverse of this matrx.
        """
        if not self.isSquare( ):
            raise ValueError( "Inverse is not defined for a non-square matrix" )
        if not self.determinant( ):
            raise ValueError( 'This matrix is not invertible' )
        return ( self.adjoint( ).__div__(  self.determinant( ) ) ) # future division breaks the "/" operator, so we have to call the function directly.

    def isInvertible( self ):
        """
        Checks to see if this matrix is invertible

        :rtype: boolean
        :returns: True if the matrix can be inverted.
        """
        return bool( self.isSquare( ) and self.determinant( ) )

    def isSquare( self ):
        """
        Checks for a square matrix

        :rtype: boolean
        :returns: True if the matrix is square
        """
        return self._width == self._height

    def itemsToInt( self ):
        """
        Convert all items to int.

        :rtype: matrix
        :returns: A copy with all items in the matrix as an int.
        """
        returnvalue = matrix( )
        for row in self._value:
            newRow = list( )
            for item in row:
                # round the item to 3 decimal places before converting,
                # so floats like 1.999999964 become 2, not 1
                newRow.append( int( round( item, 3 ) ) )
            returnvalue.addRow( *newRow )
        return returnvalue
    
    def itemsToFloat( self ):
        """
        Convert all items to float.

        :rtype: matrix
        :returns: A copy with all items in the matrix as an float.
        """
        returnvalue = matrix( )
        for row in self._value:
            newRow = list( )
            for item in row:
                newRow.append( float( item ) )
            returnvalue.addRow( *newRow )
        return returnvalue

    def kronecker( self, value ):
        """
        Returns the Kronecker product of this matrix and the passed-in matrix

        :Paramters:
            value : matrix
            The value of the matrix to combine this matrix with

        :rtype: matrix
        :returns: The Kronecker Product of the two matrices
        """
        pass

    def minor( self, i, j ):
        """
        The Minor of a matrix

        :rtype: number
        :returns: The minor of the item at column i, row j
        """
        if not self.isSquare( ):
            raise ValueError( "Minor not defined for non-square matrix" )
        if ( self._height == 1 and self._width == 1):
            raise ValueError( "not defined for 1x1 matrix" )
        m = matrix( self )
        m.deleteRow( i )
        m.deleteColumn( j )
        return m.determinant( )

    #next() method for the iterator; returns each item in the matrix, first row0, then row1, etc.
    def next( self ):
        """
        Iterator method.
        """
        if self._iterpos < ( self._width * self._height ):
            x,y = divmod( self._iterpos, self._width )
            v = self[ x ][ y ]
            self._iterpos += 1
            return v
        del self._iterpos
        raise StopIteration( )

    def roundItems( self, digits = 0 ):
        """
        Round off the items in a matrix.

        :Parameters:
            digits : int
                How many digits past the decimal point to round to. Can be negative.
            
        :rtype: matrix
        :returns: A matrix with all items rounded to 'digits' places.
        """
        returnvalue = matrix( )
        for row in self._value:
            newRow = list( )
            for item in row:
                item = round( item, digits )
                if ( digits <= 0 ):
                    item = int( item )
                newRow.append( item )
            returnvalue.addRow( *newRow )
        return returnvalue

    # An alias for roundItems
    round = roundItems # alias  

    def swapColumns( self, i, j ):
        """
        Swaps columns i and j.

        :Parameters:
            i : int
                The first of 2 columns to swap.
            j : int
                The second of 2 columns to swap.
        """
        if not ( type( i ) in MATRIX_VALID_INTS and type( j ) in MATRIX_VALID_INTS ): # this should be fixed to accomodate 'long' types
            raise TypeError( "Row indices must be of type 'int'" )
        columnA = self.deleteColumn( max( i, j ) )
        columnB = self.deleteColumn( min( i, j ) )
        self.insertColumn( min( i, j ), *columnA )
        self.insertColumn( max( i, j ), *columnB )
    
    def swapRows( self, i, j ):
        """
        Swaps rows i and j.

        :Parameters:
            i : int
                The first of 2 rows to swap.
            j : int
                The second of 2 rows to swap.
        """
        if not ( type( i ) in MATRIX_VALID_INTS and type( j ) in MATRIX_VALID_INTS ): # this should be fixed to accomodate 'long' types
            raise TypeError( "Row indices must be of type 'int'" )
        rowA = self.deleteRow( max( i, j ) )
        rowB = self.deleteRow( min( i, j ) )
        self.insertRow( min( i, j ), *rowA )
        self.insertRow( max( i, j ), *rowB )

    def transpose( self ):
        """
        Transpose of a matrix.

        :rtype: matrix
        :returns: The transpose of this matrix.
        """
        returnvalue = matrix( )
        for i in range( self._width ):
            row = list( )
            for j in range( self._height ):
                row.append( self._value[ j ][ i ] )
            returnvalue.addRow( *row )
        return returnvalue


    

def identMatrix( size ):
    """
    Creates an identity matrix

    :Parameters:
        size : int
            The size of the square matrix to return.
            
    :rtype: matrix
    :returns: An identity matrix of the specified size.
    """
    returnvalue = matrix( )
    for i in range( size ):
        newrow = [ 0 ] * size
        newrow[ i ] = 1
        returnvalue.addRow( *newrow )
    return returnvalue

def zeroMatrix( width, height ):
    """
    Creates a zero matrix

    :Parameters:
        width : int
            The width of the matrix to return
        height : int
            The height of the matrix to return

    :rtype: matrix
    :return: A zero matrix of the specified size.
    """
    returnvalue = matrix( )
    for i in range( width ):
        newrow = [ 0 ] * height
        returnvalue.addRow( *newrow )
    return returnvalue
