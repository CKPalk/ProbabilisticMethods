''' Work of Cameron Palk '''


def FactorInfo( dict ):
	def __init__( self, _scope, _card, _stride ):
		self.scope 	= _scope
		self.card 	= _card
		self.stride = _stride

	def __repr__( self ):
		return ( "Scope : {0.scope}\n" +
				 "Cards : {0.card}\n" +
				 "Stride: {0.stride}" ).format( self )

	def __mul__( self, other ):
		new_scope = new_card = new_stride = []
		for idx in range( len( self.scope ) ):
			new_scope.append( self.scope[idx] )
			new_card.append( self.card[idx] )
			new_stride.append( self.stride[idx] )
		for idx in range( len( other.scope ) ):
			rv = self.scope[idx]
			if rv not in new_scope:
				new_scope.append( rv )
				new_card.append( other.card[idx] )
				new_stride.append( other.stride[idx] )
		return FactorInfo( new_scope, new_card, new_stride )


class Factor( object ):
	def __init__( self, _info, _vals ):
		self.info = _info
		self.vals = _vals


















def main( ):
	f = FactorInfo( [0,1], [2,3], [1,3] )
	print( f )

	print( f )

	return

if __name__=='__main__':
	main( )
