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
# END FACTOR CLASS DEFINITION


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
	# Cards {A:2, B:3, C:2}
	global global_card
	global_card = [2, 3, 2]

	# Computer partition function
	z = computePartitionFunction( factors )

	# Print results
	print( "Z =", z )
	return

# Run main if this module is being run directly
if __name__ == '__main__':
	main()
