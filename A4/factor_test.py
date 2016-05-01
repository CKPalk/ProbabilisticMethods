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

vertBar = ''.join( ['-'] * 50 )

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
    print( "A:", A, "union B:", B, "=", AUB )
    return AUB

def calcStrides( scope ):
	rev_scope = list( reversed( scope ) )
	res = [ 0 ] * len( scope )
	res[ 0 ] = 1
	for idx in range( 1, len( rev_scope ) ):
		res[ idx ] = res[ idx - 1 ] * global_card[ rev_scope[ idx - 1 ] ]
	stride = list( reversed( res ) )
	#return { scope[i] : res[i]	  for i in range( len( scope ) ) }
	return { scope[i] : stride[i] for i in range( len( scope ) ) }


class Factor(dict):
	def __init__(self, scope_, vals_):
		self.scope = scope_
		self.vals = vals_
		self.stride = calcStrides( scope_ )

	def __repr__( self ):
		return "\n{}\nScope: {}\nStride: {}\nVals:\n{}\n{}\n".format( vertBar, self.scope, self.stride, '\n'.join(map(str,[round(e,3) for e in self.vals])), vertBar )
	


	def __mul__(self, other):

		phi1 = self.vals
		X1 	 = self.scope
		phi1_stride = self.stride
		phi2 = other.vals
		X2 	 = other.scope
		phi2_stride = other.stride

		idx1 = 0
		idx2 = 0

		XUX = union( X1, X2 ) 

		# This creates an array to store all vals
		psi = [ 0 ] * cardinalityOfValues( XUX ) 

		# Assignment [ 0's x Number of RVs in union ]
		assignment = { e : 0 for e in XUX }

		card_vals = cardinalityOfValues( XUX )
		card_XUX  = cardinality( XUX )
		card = cardOfUnion( XUX )

		# This counts up 0, 1, ..., the number of possible values
		for i in range( 0, card_vals ):

			psi[ i ] = phi1[ idx1 ] * phi2[ idx2 ]
			print( "psi[", i, "] = phi1[", idx1, "] x phi2[", idx2, "]" )

			for l in reversed( XUX ):
				assignment[ l ] += 1
				#print( "Updated assignment:", assignment )
				if assignment[ l ] == card[ l ]:
					assignment[ l ] = 0
					if l in X1:
						idx1 -= (( card[ l ] - 1 ) * phi1_stride[ l ] )
					if l in X2:
						idx2 -= (( card[ l ] - 1 ) * phi2_stride[ l ] )
				else:
					if l in X1:
						idx1 += phi1_stride[ l ]
					if l in X2:
						idx2 += phi2_stride[ l ]
					break

		return Factor( XUX, psi )
	#

	def __rmul__(self, other):
		return self * other

	def __imul__(self, other):
		return self * other


#
# MAIN PROGRAM
#

def main():

	A = 0
	B = 1
	C = 2
	D = 3

	global global_card
	global_card = [ 2, 2, 2, 2 ]

	f1 = Factor( [ A ], 	[ 1.5, 1.5 ] )
	f2 = Factor( [ D, B ], 	[ 0.3, 0.7, 2.9, 0.1 ] )

	f3 = f1 * f2

	print( f3 )
		

	return

main()
