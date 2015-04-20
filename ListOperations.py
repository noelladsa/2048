ADD = 0
MOVE = 1
NEW = 2

def collapse_list(num_list, transform):
    """List can contain numbers interspersed with empty positions.
    List will shrink such that first occuring pairs
    are added and the rest occupy spots that have 0"""
    pos = 0 											# Starting from_pos the left extreme of the board
    pair_pos = None 									# Stores an x of the start of a pair
    ops_log = []
    while pos < len(num_list):
        filled_pos = _find_next_number(pos, num_list)
        if filled_pos is None:
            break

        op_log = None
        if pair_pos is not None: 						# A pair was already started
            op_log = _pair_addition(pair_pos, filled_pos, num_list, transform)
            pair_pos = None

        if not op_log:
            op_log = _move_number(pos, filled_pos, num_list, transform)
            pair_pos = pos   						# Start a new pair for future additions
            pos = pos + 1

        if op_log:
            ops_log.append(op_log)

    return ops_log


def _find_next_number(pos, num_list):
    """ Returns the next position where a number is found from  """
    while pos < len(num_list):
        if num_list[pos] > 0:
            break
        pos = pos + 1
    return pos if pos < len(num_list) else None


def _pair_addition(to_pos, from_pos, num_list, transform):
    """Check if two elements are equal and add to one if so"""
    if num_list[to_pos] == num_list[from_pos]:
        num_list[to_pos] = 2 * num_list[from_pos]
        num_list[from_pos] = 0
        return {'State': ADD, 'from_pos': abs(transform - from_pos),
                'to_pos': abs(transform - to_pos), 'to_val': num_list[to_pos]}


def _move_number(to_pos, from_pos, num_list, transform):
    """ Moving numbers from one position to another,
    changing previous position to None"""
    if to_pos != from_pos:
        num_list[to_pos] = num_list[from_pos]
        num_list[from_pos] = 0
        return {'State': MOVE, 'from_pos':abs(transform - from_pos),
                'to_pos': abs(transform - to_pos), 'to_val': num_list[to_pos]}


def is_pair_present(num_list):
    """ Searches for number pairs in the list"""
    prev_number = None
    for number in num_list:
        if prev_number == number:
            return True
        prev_number = number
    return False

if __name__ == "__main__":
    array = [2, 2, 0, 4]
    log = collapse_list(array)
    print "Log", log
    print "List After", array
