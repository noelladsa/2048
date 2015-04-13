
class ListOps(object): 								# This doesn't really have to be a class with state
	"""Class that performs all 2048 related operations 
	    on a list mapping to a row or column"""
	STATE_ADDITION = 0 										# Using theses like enums
	STATE_MOVED = 1 										# Using theses like enums

	@staticmethod
	def collapse_list(number_list):
		"""List can contain numbers interspersed with empty positions. 
		List will shrink such that first occuring pairs
		are added and the rest occupy spots that have 0"""
		index = 0 											# Starting from the left extreme of the board
		pair_index = None 									# Stores an index of the start of a pair 
		ops_log = []
		while index < len(number_list):
			filled_index = ListOps._find_next_number(index,number_list) 
			if filled_index is None: 
			 	break 			# List contained no more numbers 
			
			add_success = False
			if pair_index is not None: 						# A pair was already started
				add_success = ListOps._pair_addition(pair_index,filled_index,number_list,ops_log)
				pair_index = None							# Reset pairs to None, the next number in loop will start a pair
		
			if add_success is False:
				if ListOps._move_number(index,filled_index,number_list,ops_log) is True:
					ops_log.append((ListOps.STATE_MOVED,filled_index,index,number_list[to_index]))
				pair_index = index   						# Start a new pair for future additions
				index = index + 1	
			else:
				ops_log.append((ListOps.STATE_ADDITION,filled_index,index,number_list[filled_index],number_list[index]))

		return ops_log

	@staticmethod	
 	def _find_next_number(index,number_list):
		""" Returns the next index where a number is found from  """
		while index < len(number_list): 					# Stops when you've found a number
			if number_list[index] > 0: break
			index = index + 1
		return index if index < len(number_list) else None

	@staticmethod	
	def _pair_addition(to_index, from_index,number_list):
		"""Check if two elements are equal and add to one if so"""	
		if number_list[to_index] == number_list[from_index]:
			number_list[to_index] = 2 * number_list[from_index]	
			number_list[from_index] = 0
			return True
		return False

	@staticmethod	
	def _move_number(to_index, from_index,number_list):
		""" Moving numbers from one position to another,
		 changing previous position to None"""
		if to_index != from_index: 							#Check that number is not in the same place
			number_list[to_index] = number_list[from_index]
			number_list[from_index] = 0
			return True
		return False

	@staticmethod	
	def is_pair_present(number_list):
		""" Searches for number pairs in the list"""
		prev_number = None
		for number in number_list:
			if prev_number != None:
				if prev_number == number: return True
		 	prev_number = number
		return False


ops = ListOps()
num_list,log = ListOps.collapse_list([2,2,None,4])
print "List After",num_list,log