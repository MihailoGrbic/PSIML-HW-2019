import numpy as np
import copy

def make_matrix(lines):
    matrix = np.array([[]], dtype = bool)
    for line in lines:
        row = np.array([], dtype = bool)
        for char in line:
            if char == '#':
                row = np.append(row, True)
            else:
                row = np.append(row, False)
        matrix = np.vstack([matrix, row]) if matrix.size else row

    if len(matrix.shape) == 1:
        matrix = np.expand_dims(matrix, axis = 0)
    return matrix
            
def make_validity_and_score_matrix(board, piece_list):                                                                                  # not real matrices, they are lists of matrices
    validity_matrix_list = []
    score_matrix_list = []

    for piece_index in range(0, len(piece_list)):
        for rotation in range(0, 271, 90):
            piece = rotate_object(piece_list[piece_index], rotation)

            validity_matrix = np.ndarray(shape = (board.shape[0] - piece.shape[0] + 1, board.shape[1] - piece.shape[1] + 1), dtype = bool)
            score_matrix = np.zeros((board.shape[0] - piece.shape[0] + 1, board.shape[1] - piece.shape[1] + 1))

            for y_position in range(0, validity_matrix.shape[0]):
                for x_position in range(0, validity_matrix.shape[1]):
                    position_valid = valid_position(board, piece, x_position, y_position)
                    validity_matrix[y_position][x_position] = position_valid
                    if position_valid:
                        score_matrix[y_position][x_position] = calculate_score(board, piece, x_position, y_position)
                    else:
                        score_matrix[y_position][x_position] = -1

            validity_matrix_list.append(validity_matrix)
            score_matrix_list.append(score_matrix)
    return validity_matrix_list, score_matrix_list


def task1(validity_matrix_list, score_matrix_list):                                                                   
    best_score = -1

    for piece_index in range(0, len(validity_matrix_list)):
        validity_matrix = np.copy(validity_matrix_list[piece_index])
        score_matrix = np.copy(score_matrix_list[piece_index])
        for x_position in range(0, validity_matrix.shape[1]):
            for y_position in range(0, validity_matrix.shape[0]):

                if validity_matrix[y_position][x_position] and (y_position == validity_matrix.shape[0] - 1 or not validity_matrix[y_position + 1][x_position]):           
                    current_score = score_matrix[y_position][x_position]
                    if current_score > best_score:
                        best_score = current_score
                        best_piece_index = piece_index
                        best_x = x_position
                    break
    
    best_rotation = 90 * (best_piece_index % 4)
    best_piece_index = int(best_piece_index / 4)
    return best_piece_index, best_rotation, best_x

def task2(validity_matrix_list, score_matrix_list):
    best_score = -1
    for piece_index in range(0, len(validity_matrix_list)):
        #print(piece_index)
        validity_matrix = np.copy(validity_matrix_list[piece_index])
        score_matrix = np.copy(score_matrix_list[piece_index])

        # if piece_index == 0:
        #     print (validity_matrix)
        #     print (score_matrix)

        found_movement = False
        while not found_movement:
            best_piece_score =  -1
            for x_position in range(0, validity_matrix.shape[1]):
                for y_position in range(0, validity_matrix.shape[0]):
                    if validity_matrix[y_position][x_position] and (y_position == validity_matrix.shape[0] - 1 or not validity_matrix[y_position + 1][x_position]):      
                        current_score = score_matrix[y_position][x_position]
                        if current_score > best_piece_score:
                            best_piece_score = current_score
                            best_x = x_position
                            best_y = y_position
            #print(best_piece_score)
            best_path = []
            found_movement, best_path = find_path(validity_matrix, best_x, best_y, best_path)
            #if len(best_path) > 0:
                #print("woho")
            #print(score_matrix)     

            if not found_movement:
                score_matrix[best_y][best_x] = -1  

        #print("woho")
        if best_piece_score > best_score:
            #print(best_piece_score)
            best_score = best_piece_score
            best_piece_index = piece_index
            best_best_path = best_path


    best_rotation = 90 * (best_piece_index % 4)
    best_piece_index = int(best_piece_index / 4)
      
    return best_piece_index, best_rotation, best_best_path        


def find_path(validity_matrix, x_position, y_position, prev_path):
    #print(len(prev_path))  
    # if x_position == 19 and y_position == 2:
    #     print("a")                    
    path = copy.copy(prev_path)
    #print(y_position)
    if y_position == 0 or all(validity_matrix[y_position - 1]):
        path.append(0)
        path.append(x_position)
        for i in range(0, y_position - 2):
            path.append(0)
        return True, path
    
    x_move = 0
    # if x_position == 19 and y_position == 2
    while x_position - x_move > 0 and validity_matrix[y_position][x_position - x_move]:
        if validity_matrix[y_position - 1][x_position - x_move]:
            path.append(x_move)
            found_movement, best_path = find_path(validity_matrix, x_position - x_move, y_position - 1, path)
            if found_movement:
                return True, best_path
            path.pop()
        x_move += 1
    
    x_move = 1
    while x_position + x_move < validity_matrix.shape[1] and validity_matrix[y_position][x_position + x_move]:
        if validity_matrix[y_position - 1][x_position + x_move]:
            path.append(-x_move)
            found_movement, best_path = find_path(validity_matrix, x_position + x_move, y_position - 1, path)
            if found_movement:
                return True, best_path
            path.pop()
        x_move += 1

    return False, []




def valid_position(board, piece, x_position, y_position):
    if y_position + piece.shape[0] > len(board):
        return False
    if x_position + piece.shape[1] > len(board[0]):
        return False
    for i in range(0, piece.shape[0]):
        for j in range(0, piece.shape[1]):
            if board[y_position + i][x_position + j] and piece[i][j]:
                return False
    return True
    

def calculate_score(board, piece, x_position, y_position):
    tmp_board = np.copy(board)
    for i in range(0, piece.shape[0]):
        for j in range(0, piece.shape[1]):
            tmp_board[y_position + i][x_position + j] = board[y_position + i][x_position + j] or piece[i][j]
    score = 0
    for row in tmp_board:
        if all(row):
            score += 1
    return score

def rotate_object(object, rotation):
    if rotation == 0:
        return object
    return rotate_object(np.rot90(object), rotation - 90)


if __name__ == "__main__":
    file_path = input()
    f = open(file_path, "r")
    lines = f.readlines()

    board_finished = False
    current_lines = []
    piece_list = []

    for line in lines:
        line = line.rstrip('\n').rstrip('\r')
        
        if not board_finished:
            if len(line) == 0:
                board_finished = True
                board = make_matrix(current_lines)
                current_lines = []
            else:
                current_lines.append(line)
        else:
            if len(line) == 0:
                new_piece =  make_matrix(current_lines)
                piece_list.append(make_matrix(current_lines))
                current_lines = []
            else:
                current_lines.append(line)
    piece_list.append(make_matrix(current_lines))

    validity_matrix_list, score_matrix_list = make_validity_and_score_matrix(board, piece_list)

    best_piece_index, best_rotation, best_x = task1(validity_matrix_list, score_matrix_list) 

    best_piece_index2, best_rotation2, best_best_path = task2(validity_matrix_list, score_matrix_list)

    print(best_piece_index, end = " ")
    print(best_rotation, end = " ")
    print(best_x)
    print(best_piece_index2, end = " ")
    print(best_rotation2, end = " ")
    print("0", end = " ")
    #print(best_best_path)
    for i in range(len(best_best_path) - 1, -1, -1):
        print(best_best_path[i], end = " ")
    print
