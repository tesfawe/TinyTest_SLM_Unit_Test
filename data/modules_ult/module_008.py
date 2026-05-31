import random

def create_three_random_v_indices(current_vector_index, numOfPop):
    while True:
        v_index_1 = random.randint(0,numOfPop)
        if (v_index_1 != current_vector_index):
            break
    while True:
        v_index_2 = random.randint(0, numOfPop)
        if (v_index_2 != v_index_1 and v_index_2 != current_vector_index):
            break
    while True:
        v_index_3 = random.randint(0, numOfPop)
        if (v_index_3 != v_index_1 and v_index_3 != v_index_2 and v_index_3 != current_vector_index):
            break
    return v_index_1, v_index_2, v_index_3