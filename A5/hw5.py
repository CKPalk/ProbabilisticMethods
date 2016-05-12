# CIS 410/510pm
# Homework #5
# Cameron Palk
# May 2016
#
# Special thanks to Daniel Lowd for the skeletor code

import sys
import tokenize
from functools import reduce


global_card = []
num_vars = 0


def pVal( val ):
	return round( val, 3 )

def printableVals( vals ):
	return [ pVal( v ) for v in vals ]

def cardinality( A ):
	return len( A )

def cardinalityOfValues( XUX ):
	return reduce( lambda agg, x: agg * global_card[x], XUX, 1 )

def cardOfUnion( U ):
	return { u : global_card[ u ] for u in U }

def union( A, B ):
    return [ a for a in A ] + [ b for b in B if b not in A ]

def calcStrides( scope ):
	rev_scope = list( reversed( scope ) )
	res = [ 0 ] * len( scope )
	res[ 0 ] = 1
	for idx in range( 1, len( rev_scope ) ):
		res[ idx ] = res[ idx - 1 ] * global_card[ rev_scope[ idx - 1 ] ]
	stride = list( reversed( res ) )
	return { scope[i] : stride[i] for i in range( len( scope ) ) }


class Factor( dict ):

	def __init__(self, scope_, vals_):
		self.scope = scope_
		self.vals = vals_
		self.stride = calcStrides( scope_ )

	def __eq__(self, other):
		return (self.scope  == other.scope and
				self.vals   == other.vals  and
				self.stride == other.stride )

	def __repr__( self ):
		style = "\n{0}\nScope: {1}\nStride: {2}\nCard: {3}\nVals:\n{4}\n{0}\n"
		vertBar = ''.join( ['-'] * 50 )
		return style.format( vertBar, self.scope, self.stride,
							 { v : global_card[v] for v in self.scope },
							 '\n'.join( [ str( round( e, 3 ) ) for e in self.vals ] ) )

	def __mul__(self, other):
		XUX 		= union( self.scope, other.scope )
		assignment 	= { e : 0 for e in XUX }
		union_card 		= cardOfUnion( XUX )
		psi 		= [ 0 ] * cardinalityOfValues( XUX )

		idx1 = idx2 = 0
		for i in range( 0, cardinalityOfValues( XUX ) ):
			psi[ i ] = self.vals[ idx1 ] * other.vals[ idx2 ]
			for l in reversed( XUX ):
				assignment[ l ] += 1
				if assignment[ l ] == union_card[ l ]:
					assignment[ l ] = 0
					idx1 -= (( union_card[ l ] - 1 ) * self.stride [ l ] ) if l in self.scope  else 0
					idx2 -= (( union_card[ l ] - 1 ) * other.stride[ l ] ) if l in other.scope else 0
				else:
					idx1 += self.stride [ l ] if l in self.scope  else 0
					idx2 += other.stride[ l ] if l in other.scope else 0
					break
		return Factor( XUX, psi )
	#

	def __rmul__(self, other):
		return self * other

	def __imul__(self, other):
		return self * other

	def containsRV( self, rv ):
		return rv in self.scope

	def sumOut( self, rv ):

		if rv not in self.scope:
			raise Exception( "Trying to sum out {} which is not in the Factor".format( rv ) )

		# The number of resulting values will be the the origional number divided by the cardinality of our summed out rv
		rv_card = global_card[ rv ]
		res_vals  = [ 0 ] * ( len( self.vals ) // rv_card )

		# The scope will be the origional factors remove our rv
		res_scope = [ s for s in self.scope if s is not rv ]
		rv_stride = self.stride[ rv ]
		#print( rv, "stride", rv_stride )

		for idx in range( len( res_vals ) ):
			sec = idx // rv_stride
			start_idx = idx + ( sec * rv_stride )

			# Sum the appropriate values from the origional factors vals
			#  - Start at ...
			#  - Step by the stride of the RV
			res_vals[ idx ] = sum( [ self.vals[ start_idx + (rv_stride * step) ] for step in range( rv_card ) ] )

		

		return Factor( res_scope, res_vals )


#
# READ IN MODEL FILE
# ( don't tell me what to do! )

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
# MAIN PROGRAM
#

def pf(f):
	for x in f:
		print(x)

def factorCountWithVar( factors, rv ):
	return sum( [ 1 if f.containsRV( rv ) else 0 for f in factors ] )

def factorStats( factors, possibleVariables ):
	return { v: factorCountWithVar(factors,v) for v in range( num_vars ) if v in possibleVariables }

def main():
	factors = read_model()

	possibleVariables = set( range( num_vars ) )

	# Get smart about that Z calc
	while possibleVariables:

		stats = factorStats( factors, possibleVariables )
		rv = min( stats, key=lambda x: stats[x] )
		possibleVariables.remove( rv )

		factors_sub = [ f for f in factors if f.containsRV( rv )   ]

		if len( factors_sub ) < 2:
			continue

		new_factors = [ f for f in factors if f not in factors_sub ]
		factored_sub = reduce( Factor.__mul__, factors_sub )

		new_factors.append(
			factored_sub.sumOut(rv) if len(factored_sub.scope) > 1 else factored_sub
		)

		factors = new_factors
		if len( factors ) == 1:
			break
	#

	f = reduce( Factor.__mul__, factors )

	z = sum( f.vals )
	print( "\nZ = ", z, "\n" )
	return

main()
