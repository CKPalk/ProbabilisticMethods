# CIS 410/510pm
# Homework #4
# Daniel Lowd
# April 2016
#
# TEMPLATE CODE
import sys
import tokenize
from functools import reduce

#
# FACTOR CLASS -- EDIT HERE!
#

card = []

vertBar = ''.join( ['-'] * 50 )

def pVal( val ):
	return round( val, 3 )

def printableVals( vals ):
	return [ pVal( v ) for v in vals ]

def difference( A, B ):
	return list( set( A ).intersection( set( B ) ) )

def cardinality( A ):
	return len( A )

def cardinalityOfValues( XUX ):
	global card
	return reduce( lambda agg,x: agg * card[x], XUX, 1 )



# This may be a naive set union, may be wrong
def union( A, B ):
	return A + B
	#return list( set( A ).union( set( B ) ) )

def calcStrides( scope ):
	global card
	rev_scope = list( reversed( scope ) )
	res = [ 0 ] * len( scope )
	res[ 0 ] = 1
	for idx in range( 1, len( rev_scope ) ):
		res[ idx ] = res[ idx - 1 ] * card[ rev_scope[ idx - 1 ] ]
	l = list( reversed( res ) )
	#l = list( res )
	return l # What is the 'right ordering for this strides array

	

class Factor(dict):
	def __init__(self, scope_, vals_):
		self.scope = scope_
		self.vals = vals_
		self.stride = calcStrides( scope_ )



	def __mul__(self, other):

		#print( "\n\nStarting factor between", self.scope, "and", other.scope )
		print( "\n" )
		print( "Phi1 scope:", self.scope )
		print( "Phi1 strides:", self.stride )
		print( "Phi1:", printableVals( self.vals ) )
		print()
		print( "Phi2 scope:", other.scope )
		print( "Phi2 strides:", other.stride )
		print( "Phi2:", printableVals( other.vals ) )
		print()


		print( "Scopes share", difference( self.scope, other.scope ) )

		global card # Cardinality of each RV, the RV is the index for its card

		phi1 = self.vals
		X1 	 = self.scope
		phi1_stride = self.stride
		phi2 = other.vals
		X2 	 = other.scope
		phi2_stride = other.stride

		idx1 = 0
		idx2 = 0

		# This does not preserve orderings
		XUX = union( X1, X2 ) 
		# This creates an array to store all vals
		psi = [ 0 ] * cardinalityOfValues( XUX ) 

		# Assignment [ 0's x Number of RVs in union ]
		assignment = [ 0 for l in range( 0, cardinality( XUX ) - ) ]
		print( "Assignment:", assignment )

		c = cardinalityOfValues( XUX )
		print( "Joining X1", X1, "with X2", X2 )
		print( "X1 U X2:",  XUX, "cardinality", c )

		# This counts up 0, 1, ..., the number of possible values
		for i in range( 0, cardinalityOfValues( XUX ) ):
			
			psi[ i ] = phi1[ idx1 ] * phi2[ idx2 ]
			print( "psi[", i ,"] = phi1[", idx1, "] * phi2[", idx2, "]")
			print( pVal(psi[ i ]), "=", pVal(phi1[ idx1 ]), "*", pVal(phi2[ idx2 ]), "\n" )

			for l in range( 0, cardinality( XUX ) - 1 ):
				print( "L:", l )
				assignment[ l ] += 1
				print( "Assignment:", assignment )
				if assignment[ l ] == card[ l ]:
					print( "In if statment" )
					assignment[ l ] = 0
					if l in X1:
						idx1 -= (( card[ l ] - 1 ) * phi1_stride[ l ] )
					if l in X2:
						idx2 -= (( card[ l ] - 1 ) * phi2_stride[ l ] )
				else:
					print( "In else statement" )
					print( assignment )
					print( "Card:", card )
					if l in X1:
						idx1 += phi1_stride[ l ]
					if l in X2:
						print( l )
						print( phi2_stride )
						idx2 += phi2_stride[ l ]
					break

		print( "\nReturning new factor over", XUX )
		print( printableVals( psi ) )
		print( vertBar )

		return Factor( XUX, psi )
	#

	def __rmul__(self, other):
		return self * other

	def __imul__(self, other):
		return self * other


#
# READ IN MODEL FILE
#

# Read in all tokens from stdin.  Save it to a (global) buf that we use
# later.  (Is there a better way to do this? Almost certainly.)
curr_token = 0
token_buf = []

def read_tokens():
	global token_buf
	for line in sys.stdin:
		token_buf.extend(line.strip().split())
	#print "Num tokens:",len(token_buf)

def next_token():
	global curr_token
	global token_buf
	curr_token += 1
	return token_buf[ curr_token - 1 ]

def next_int():
	return int( next_token() )

def next_float():
	return float( next_token() )

def read_model():
	# Read in all tokens and throw away the first (expected to be "MARKOV")
	read_tokens()
	s = next_token()

	# Get number of vars, followed by their ranges
	num_vars = next_int()
	global card
	card = [ next_int() for i in range( num_vars ) ]

	# Get number and scopes of factors 
	num_factors = int(next_token())
	factor_scopes = []
	for i in range(num_factors):
		factor_scopes.append( [ next_int() for i in range( next_int() ) ] )

	# Read in all factor values
	factor_vals = []
	for i in range(num_factors):
		factor_vals.append( [ next_float() for i in range( next_int() ) ] )

	# DEBUG
	'''
	print ( "Num vars: ",num_vars )
	print ( "Ranges: ", card )
	print ( "Scopes: ",factor_scopes )
	print ( "Values: ",factor_vals )
	'''
	return [ Factor(s,v) for (s,v) in zip( factor_scopes, factor_vals ) ]


#
# MAIN PROGRAM
#

def main():
	factors = read_model()
	# Compute Z by brute force
	f = reduce( Factor.__mul__, factors )
	z = sum( f.vals )
	print( "\n\nZ = ", z, "\n\n" )
	return

main()
