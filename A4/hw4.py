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

global_card = []


def pVal( val ):
	return round( val, 3 )

def printableVals( vals ):
	return [ pVal( v ) for v in vals ]

def cardinality( A ):
	return len( A )

def cardinalityOfValues( XUX ):
	return reduce( lambda agg,x: agg * global_card[x], XUX, 1 )

def cardOfUnion( U ):
	return { u : global_card[ u ] for u in U }

def union( A, B ):
    AUB = [ a for a in A ]
    for b in B:
        if b not in A:
            AUB.append( b )
    return AUB

def calcStrides( scope ):
	rev_scope = list( reversed( scope ) )
	res = [ 0 ] * len( scope )
	res[ 0 ] = 1
	for idx in range( 1, len( rev_scope ) ):
		res[ idx ] = res[ idx - 1 ] * global_card[ rev_scope[ idx - 1 ] ]
	stride = list( reversed( res ) )
	return { scope[i] : stride[i] for i in range( len( scope ) ) }


class Factor(dict):

	def __init__(self, scope_, vals_):
		self.scope = scope_
		self.vals = vals_
		self.stride = calcStrides( scope_ )


	# Always add your own representation of classes, so you can print them!
	def __repr__( self ):
		vertBar = ''.join( ['-'] * 50 )
		return "\n{0}\nScope: {1}\nStride: {2}\nVals:\n{3}\n{0}\n".format( vertBar, self.scope, self.stride, '\n'.join(map(str,[round(e,3) for e in self.vals])) )
		

	def __mul__(self, other):

		# Mapping class attributes to pseudocode variable names ( sorta )
		phi1 = self.vals
		X1 	 = self.scope
		phi1_stride = self.stride
		phi2 = other.vals
		X2 	 = other.scope
		phi2_stride = other.stride

		idx1 = 0 # J in the pseudo
		idx2 = 0 # K in the pseudo

		# This is the new scope of our resulting Factor
		XUX = union( X1, X2 ) 

		# Get the cardinalities and local cardinalities
		card_vals = cardinalityOfValues( XUX )
		card_XUX  = cardinality( XUX )
		card 	  = cardOfUnion( XUX )

		# Our results array
		psi = [ 0 ] * cardinalityOfValues( XUX ) 

		# Assignment dictionary from RVs to counters
		assignment = { e : 0 for e in XUX }

		# This counts up 0, 1, ..., the number of possible values
		for i in range( 0, card_vals ):

			# Multiply the correct lines across both Factors
			psi[ i ] = phi1[ idx1 ] * phi2[ idx2 ]

			# This has to run through our union reversed
			# because it makes the program work and idk why
			for l in reversed( XUX ):
				assignment[ l ] += 1
				if assignment[ l ] == card[ l ]:
					assignment[ l ] = 0
					idx1 -= (( card[ l ] - 1 ) * phi1_stride[ l ] ) if l in X1 else 0
					idx2 -= (( card[ l ] - 1 ) * phi2_stride[ l ] ) if l in X2 else 0
				else:
					idx1 += phi1_stride[ l ] if l in X1 else 0
					idx2 += phi2_stride[ l ] if l in X2 else 0
					break

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
	global global_card
	global_card = [ next_int() for i in range( num_vars ) ]

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
	print ( "Ranges: ", global_card )
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
