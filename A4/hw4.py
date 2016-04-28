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

var_ranges = []

def union( A, B ):
	return list( set( A ).union( set( B ) ) )

def card( A ):
	return len( A )

def valCard( A ):
	global var_ranges
	s = 1
	for e in A:
		s *= var_ranges[ e ]
	return s

def calcStrides( scope ):
	global var_ranges
	rev_scope = list( reversed( scope ) )

	res = [ 0 ] * len( scope )
	res[ 0 ] = 1
	for idx in range( 1, len( rev_scope ) ):
		res[ idx ] = res[ idx - 1 ] * var_ranges[ rev_scope[ idx - 1 ] ]

	l = list( reversed( res ) )
	#print( "Calculated stride:", l )
	return l

	

class Factor(dict):
	def __init__(self, scope_, vals_):
		self.scope = scope_
		self.vals = vals_
		self.stride = calcStrides( scope_ )

	def __mul__(self, other):

		phi1 = self.vals
		phi2 = other.vals

		j = 0
		k = 0

		u = union( self.scope, other.scope )
		print( "Self scope:", self.scope )
		print( "Other scope:", other.scope )

		assignment = [ 0 for l in range( card(u) ) ]
		
		r = range( valCard( u ) )
		psi = [ 0 for _ in r ]
		for i in r:
			#print( "i", i )

			psi[ i ] = phi1[ j ] * phi2[ k ]
			for l in range( card( u ) - 1 ):
				#print( "L:", l )
				#print( "Num of Elements:", card( u ) )
				assignment[ l ] += 1
				if assignment[ l ] == var_ranges[ l ]:
					assignment[ l ] = 0
					if l in self.scope:
						j -= ( var_ranges[ l ] - 1 ) * self.stride[ l ]
					if l in other.scope:
						k -= ( var_ranges[ l ] - 1 ) * other.stride[ l ]
				else:
					#print( "Self stride:", self.stride )
					if l in self.scope:
						j += self.stride[ l ]
					#print( "Other stride:", other.stride )
					if l in other.scope:
						k += other.stride[ l ]
					break
		
		print( "Union:", u )
		print( "Values:", psi )
		print( "Finished factor" )
		return Factor( u, psi )
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
	global var_ranges
	var_ranges = [ next_int() for i in range( num_vars ) ]

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
	#print "Num vars: ",num_vars
	#print ("Ranges: ",var_ranges)
	#print "Scopes: ",factor_scopes
	#print "Values: ",factor_vals
	return [ Factor(s,v) for (s,v) in zip( factor_scopes, factor_vals ) ]


#
# MAIN PROGRAM
#

def main():
	factors = read_model()
	# Compute Z by brute force
	f = reduce( Factor.__mul__, factors )
	z = sum( f.vals )
	print( "Z = ", z )
	return

main()
