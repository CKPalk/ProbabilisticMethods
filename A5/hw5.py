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

''' Calculate Stride
@param	scope		Array of RVs
@return	{int:int}	Dictionary mapping RVs from scope to strides
'''
def calcStrides( scope ):
	rev_scope = list( reversed( scope ) )
	res = [ 1 ] + [ 0 ] * ( len( scope ) - 1 )
	for idx in range( 1, len( rev_scope ) ):
		res[ idx ] = res[ idx - 1 ] * global_card[ rev_scope[ idx - 1 ] ]
	stride = list( reversed( res ) )
	return { scope[i] : stride[i] for i in range( len( scope ) ) }

# FACTOR CLASS DEFINITION START
class Factor( dict ):

	def __init__(self, _scope, _vals):
		self.scope = _scope
		self.vals = _vals
		self.stride = calcStrides( _scope )

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

		return Factor( new_scope, new_vals )
	#

	def containsRV( self, rv ):
		return rv in self.scope
	#

	def sumOut( self, rv ):
		res_scope = [ s for s in self.scope if s is not rv ]
		rv_card   = global_card[ rv ]
		rv_stride = self.stride[ rv ]

		# Populate this value list
		res_vals  = [ 0 ] * ( len( self.vals ) // rv_card )

		for idx in range( len( res_vals ) ):
			# Sum the appropriate values from the origional factors vals:
			#  1. Using this convolution find the starting index
			start_idx = ( idx % rv_stride ) + ((idx // rv_stride) * rv_card * rv_stride)
			#  2. Collect the values by stepping by the stride of the RV
			#     Step as many times as the cardinality of the RV
			temp_vals = [ self.vals[ start_idx + (rv_stride * step) ] for step in range( rv_card ) ]
			#  3. Sum these collected values for an entry into the resulting value list
			res_vals[ idx ] = sum( temp_vals )

		return Factor( res_scope, res_vals )
# FACTOR CLASS DEFINITION END



# DANIELS READER START
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
# DANIELS READER END


''' Factor Count With Var '''
def factorCountWithVar( factors, rv ):
	return sum( [ 1 if f.containsRV( rv ) else 0 for f in factors ] )
#

''' Factor Stats '''
def factorStats( factors, possibleVariables ):
	return { v: factorCountWithVar(factors,v) for v in range( num_vars ) if v in possibleVariables }
#

''' Unioned Scopes '''
def unionedScopes( factors ):
	return reduce( lambda agg, x: agg.union(set(x.scope)), factors, set() )
#

''' Compute Partition Function

	What the Factor is going on!?
		1. Find out which RV should be summed out from the [remaining] Factors to mitigate work
			A Factor is a clique. We want to find the RV that is in the least number of cliques.
			To do this we count how many times each RV shows up in our Factor array,
			then choose the RV with the lowest count.
			Is this the right way to do it? I honestly have no clue. But it's fast at execution so...
			Also I will call this choosen RV, the_RV
		2. Collect the Factors containing the_RV and remove them from the full list of Factors
		3. Multiply the collected subset together, you will have one Factor from this
		4. Put that Factor back into the full list of Factors
		5. Repeat from step 1 until you have one Factor left in the list OR you have tried every RV
		6. If you have more than one Factor left, multiply it together to get one Factor
		7. Get the Partition Function by summing the values of the resulting Factor singleton

	@input 	factors		An array of Factor objects representing the graph
	@return [float]		The partition function
'''
def computePartitionFunction( factors ):

	possibleVariables = unionedScopes( factors )

	# Get smart about that Z calc
	while possibleVariables:
		# Find the next RV to try and sum out
		stats = factorStats( factors, possibleVariables )
		the_RV = min( stats, key=lambda x: stats[x] )
		possibleVariables.remove( the_RV )
		# Create a subset of Factors with the RV we want
		factors_sub = [ f for f in factors if f.containsRV( the_RV )   ]
		# If there are less than 2 then continuing with this RV is useless
		if len( factors_sub ) < 2: continue
		# Save the remaining Factors not in our subset
		new_factors = [ f for f in factors if f not in factors_sub ]
		# Multiply the subset of factors containing the_RV
		factored_sub = reduce( Factor.__mul__, factors_sub )
		# Append either a summed out Factor or just the Factor if summing out doesn't make sense
		new_factors.append(
			factored_sub.sumOut( the_RV ) if len factored_sub.scope ) > 1 else factored_sub
		)
		# If there is only one factor left we can preemptively stop
		if len( new_factors ) == 1: break
		# Updated factors to the new factors
		factors = new_factors

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
