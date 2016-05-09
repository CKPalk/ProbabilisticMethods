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
		style = "\n{0}\nScope: {1}\nStride: {2}\nVals:\n{3}\n{0}\n"
		vertBar = ''.join( ['-'] * 50 )
		return style.format( vertBar, self.scope, self.stride,
							 '\n'.join( [ str( round( e, 3 ) ) for e in self.vals ] ) )

	def __mul__(self, other):
		XUX 		= union( self.scope, other.scope )
		assignment 	= { e : 0 for e in XUX }
		card 		= cardOfUnion( XUX )
		psi 		= [ 0 ] * cardinalityOfValues( XUX )

		idx1 = idx2 = 0
		for i in range( 0, cardinalityOfValues( XUX ) ):
			psi[ i ] = self.vals[ idx1 ] * other.vals[ idx2 ]
			for l in reversed( XUX ):
				assignment[ l ] += 1
				if assignment[ l ] == card[ l ]:
					assignment[ l ] = 0
					idx1 -= (( card[ l ] - 1 ) * self.stride [ l ] ) if l in self.scope  else 0
					idx2 -= (( card[ l ] - 1 ) * other.stride[ l ] ) if l in other.scope else 0
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
		# Sum out check, ensure that the origional sum = final sum
		print( "--- Sum out initial sum:", sum(self.vals))
		if rv not in self.scope:
			raise Exception( "Trying to sum out {} which is not in the Factor".format( rv ) )

		'''
		Now that we know what we are summing out we can prepare our resulting Factor
		'''
		# We know there will only be half as many values in the resulting Factor
		res_vals  = [ 0 ] * ( len( self.vals ) // 2 )

		# The scope will be the origional factors remove our rv
		res_scope = [ s for s in self.scope if s is not rv ]
		rv_stride = self.stride[ rv ]

		for idx in range( len( res_vals ) ):
			sec = idx // rv_stride
			idx1 = idx + ( sec * rv_stride )
			idx2 = idx1 + rv_stride
			res_vals[ idx ] = self.vals[ idx1 ] + self.vals[ idx2 ]
			# print( "res[" + str(idx) + "] = vals[" + str(idx1) + "] + vals[" + str(idx2) + "]" )

		print( "--- Sum out final sum:", sum(res_vals))
		return Factor( res_scope, res_vals )


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

def main():
	factors = read_model()

	# Get smart about that Z calc
	for rv in range( num_vars ):
		print( "Summing out", rv )
		print( "Initial factors" )
		pf(factors)
		factors_sub = [ f for f in factors if f.containsRV( rv )   ]
		if not factors_sub:
			print( "There are no factors with", rv )
			continue
		print( "Factor subset:" )
		pf(factors_sub)
		new_factors = [ f for f in factors if f not in factors_sub ]
		print( "New factors" )
		pf(factors)
		factored_sub = reduce( Factor.__mul__, factors_sub )
		print(factored_sub)
		fs = factored_sub.sumOut(rv)
		print(fs)
		new_factors.append( fs )
		factors = new_factors
		print( "Final factors" )
		pf(factors)
		if len( factors ) == 1:
			print( "One factor left" )
			print( factors[0] )
			break

	z = sum( factors[0].vals )

	#f = reduce( Factor.__mul__, factors )

	#print( f.sumOut( 0 ) )

	#z = sum( f.vals )
	print( "\nZ = ", z, "\n" )
	return

main()
