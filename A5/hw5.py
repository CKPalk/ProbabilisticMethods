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


def printableVals( vals ):
	return [ round( v, 3 ) for v in vals ]

def union( A, B ):
	return list( set( A ).union( set( B ) ) )

def calcStrides( scope ):
	rev_scope = list( reversed( scope ) )
	res = [ 1 ] + [ 0 ] * ( len( scope ) - 1 )
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
		new_scope 	= union( self.scope, other.scope )
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

		return Factor( new_scope, new_vals )
	#

	def __rmul__(self, other):
		return self * other

	def __imul__(self, other):
		return self * other

	def containsRV( self, rv ):
		return rv in self.scope

	def sumOut( self, rv ):

		# Sum out check, ensure that the origional sum = final sum
		sum_in = round( sum( self.vals ), ndigits=3 )
		#print( " > Sum out {:2} sum in:  {}".format( rv, sum_in ) )

		if rv not in self.scope:
			raise Exception( "Trying to sum out {:2} which is not in the Factor".format( rv ) )

		# The number of resulting values will be the the origional number divided by the cardinality of our summed out rv
		rv_card = global_card[ rv ]
		res_vals  = [ 0 ] * ( len( self.vals ) // rv_card )

		# The scope will be the origional factors remove our rv
		res_scope = [ s for s in self.scope if s is not rv ]
		rv_stride = self.stride[ rv ]
		#print( rv, "stride", rv_stride )

		#print( self )
		for idx in range( len( res_vals ) ):

			#print( "for [{}]".format(idx))

			#sec = idx // rv_stride
			#start_idx = idx + ( sec * rv_stride )

			start_idx = ( idx % rv_stride ) + ((idx // rv_stride) * rv_card * rv_stride)
			#print( "Section {} = {} // {}".format( sec, idx, rv_stride ) )
			#start_idx = (idx % rv_card) + ( sec * rv_stride * rv_card )


			#print( [ start_idx + (rv_stride * step) for step in range( rv_card ) ] )


			# Sum the appropriate values from the origional factors vals
			#  - Start at ...
			#  - Step by the stride of the RV
			res_vals[ idx ] = sum( [ self.vals[ start_idx + (rv_stride * step) ] for step in range( rv_card ) ] )

		#print( Factor( res_scope, res_vals ) )
		sum_out = round( sum( res_vals ), ndigits=3 )
		#print( " < Sum out {:2} sum out: {}".format( rv, sum_out ) )

		if abs(sum_in-sum_out) > 0.01:
			print( "SUM DIFFERENCE IS {}".format( abs(sum_in-sum_out) ))
			#print( self )
			#print( Factor( res_scope, res_vals ) )
			for idx in range( len( res_vals ) ):
				#print( "for [{}]".format(idx))
				sec = idx // rv_card
				#start_idx = (idx % rv_card) + ( sec * rv_stride * rv_card )
				start_idx = ( idx % rv_card ) + ((idx // rv_card) * rv_card * rv_stride)

				# Sum the appropriate values from the origional factors vals
				#  - Start at ...
				#  - Step by the stride of the RV
				#print( [ start_idx + (rv_stride * step) for step in range( rv_card ) ] )

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


def pf(f):
	for x in f:
		print(x)

def factorCountWithVar( factors, rv ):
	return sum( [ 1 if f.containsRV( rv ) else 0 for f in factors ] )

def factorStats( factors, possibleVariables ):
	return { v: factorCountWithVar(factors,v) for v in range( num_vars ) if v in possibleVariables }


def computePartitionFunction( factors ):
	possibleVariables = set( range( num_vars ) )

	# Get smart about that Z calc
	while possibleVariables:

		# Break down how many factors contain each possible RV
		stats = factorStats( factors, possibleVariables )
		# Take the minimum of these counts and try to sum out that RV
		rv = min( stats, key=lambda x: stats[x] )
		possibleVariables.remove( rv )

		factors_sub = [ f for f in factors if f.containsRV( rv )   ]

		if len( factors_sub ) < 2:
			continue

		new_factors = [ f for f in factors if f not in factors_sub ]

		# Factor the subset of factors containing the RV
		factored_sub = reduce( Factor.__mul__, factors_sub )

		new_factors.append(
			factored_sub.sumOut(rv) if len(factored_sub.scope) > 1 else factored_sub
		)

		# Updated factors to the new factors
		factors = new_factors

		if len( factors ) == 1:
			break
	#

	f = reduce( Factor.__mul__, factors )
	z = sum( f.vals )
	return z
#

def main():
	# Read file
	factors = read_model()

	# Computer partition function
	z = computePartitionFunction( factors )

	# Print results
	print( "\tZ = ", z )
	return

# Run main if this module is being run
if __name__ == '__main__':
	main()
