# CIS 410/510pm
# Homework 5 beta 0.0.1
# Cameron Palk
# May 2016
#
# Special thanks to Daniel Lowd for the skeletor code

import sys
import tokenize
from functools import reduce


global_card = []
num_vars = 0

''' Calc Strides
'''
def calcStrides( scope ):
	rev_scope = list( reversed( scope ) )
	res = [ 1 ] + [ 0 ] * ( len( scope ) - 1 )
	for idx in range( 1, len( rev_scope ) ):
		res[ idx ] = res[ idx - 1 ] * global_card[ rev_scope[ idx - 1 ] ]
	stride = list( reversed( res ) )
	return { scope[i] : stride[i] for i in range( len( scope ) ) }

# FACTOR CLASS DEFINITION
class Factor( dict ):
	# Constructor
	def __init__(self, scope_, vals_):
		self.scope = scope_
		self.vals = vals_
		self.stride = calcStrides( scope_ )
	#

	# Are two object EQual, True of False
	def __eq__(self, other):
		return (self.scope  == other.scope and
				self.vals   == other.vals  and
				self.stride == other.stride )
	#

	# A string used for printing the Factor Objects
	def __repr__( self ):
		style = "\n{0}\nScope: {1}\nStride: {2}\nCard: {3}\nVals:\n{4}\n{0}\n"
		vertBar = ''.join( ['-'] * 50 )
		return style.format( vertBar, self.scope, self.stride,
							 { v : global_card[v] for v in self.scope },
							 '\n'.join( [ str( round( e, 3 ) ) for e in self.vals ] ) )
	#

	# What the '*' character does between our objects
	def __mul__( self, other ):
		new_scope 	= list( set( self.scope ).union( set( other.scope ) ) )
		assignment 	= { e : 0 for e in new_scope }
		card 		= { u : global_card[ u ] for u in new_scope }
		val_count	= reduce( lambda agg, x: agg * global_card[x], new_scope, 1 )
		new_vals 	= [ 0 ] * val_count

		idx1 = idx2 = 0
		for i in range( 0, val_count ):
			new_vals[ i ] = self.vals[ idx1 ] * other.vals[ idx2 ]
			for rv in reversed( new_scope ):
				if assignment[ rv ] == card[ rv ] - 1:
					idx1 -= assignment[ rv ] * self.stride [ rv ] if rv in self.stride  else 0
					idx2 -= assignment[ rv ] * other.stride[ rv ] if rv in other.stride else 0
					assignment[ rv ] = 0
				else:
					idx1 += self.stride [ rv ] if rv in self.scope  else 0
					idx2 += other.stride[ rv ] if rv in other.scope else 0
					assignment[ rv ] += 1
					break
		#
		return Factor( new_scope, new_vals )
	#

	# Sum out the variable and return a new Factor
	def sumOut( self ):
		# TODO Sum out a RV
		return
	#

	# Helper Functions:
	def containsRV( self, rv ):
		return rv in self.scope
	#
# END FACTOR CLASS DEFINITION

# IGNORE DANIELS READER BELOW
#
# Read in all tokens from stdin.  Save it to a (global) buf that we use
# later.  (Is there a better way to do this? Almost certainly.)
curr_token = 0
token_buf = []

def read_tokens():
	global token_buf
	for line in sys.stdin:
		token_buf.extend(line.strip().split())
#

def next_token():
	global curr_token
	global token_buf
	curr_token += 1
	return token_buf[ curr_token - 1 ]
#

def next_int():
	return int( next_token() )
#

def next_float():
	return float( next_token() )
#

def read_model():
	# Read in all tokens and throw away the first (expected to be "MARKOV")
	read_tokens()
	s = next_token()

	# Get number of vars, followed by their ranges
	global num_vars
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

	return [ Factor(s,v) for (s,v) in zip( factor_scopes, factor_vals ) ]
#
# IGNORE DANIELS READER ABOVE



''' Factor Count With Var
	@input 	factors		Factors we want to look through
	@input	rv			A RV
	@return	[int]		The number of times the rv occures in the factors scopes
'''
def factorCountWithVar( factors, rv ):
	return sum( [ 1 if f.containsRV( rv ) else 0 for f in factors ] )

''' Factor Stats
'''
def factorStats( factors, possibleVariables ):
	return { v: factorCountWithVar(factors,v) for v in range( num_vars ) if v in possibleVariables }


''' Compute Partition Function
	@input 	factors		An array of Factor objects representing the graph
	@return [float]		The partition function ( why is it called a function? )
'''
def computePartitionFunction( factors ):
	# TODO: Implement a faster way to computer partition function by summing out variables
	f = reduce( Factor.__mul__, factors )
	z = sum( f.vals )
	return z
#

''' Main '''
def main():
	# Read file
	factors = read_model()

	# Computer partition function
	z = computePartitionFunction( factors )

	# Print results
	print( "Z =", z )
	return

# Run main if this module is being run directly
if __name__ == '__main__':
	main()
