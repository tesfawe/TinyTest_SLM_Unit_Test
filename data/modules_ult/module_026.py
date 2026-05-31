
def calc_num_weights3(num_inputs, layer_sizes, num_outputs, m_trainable_arr, b_trainable_arr):
    n = 0
    if len(layer_sizes) == 0:
        if m_trainable_arr and m_trainable_arr[0]:
            n += num_inputs * num_outputs
        if b_trainable_arr and b_trainable_arr[0]:
            n += num_outputs
        return n
    if m_trainable_arr and m_trainable_arr[0]:
        n += num_inputs * layer_sizes[0]
    if b_trainable_arr and b_trainable_arr[0]:
        n += layer_sizes[0]
    for i in range(1, len(layer_sizes)):
        if m_trainable_arr and i < len(m_trainable_arr) and m_trainable_arr[i]:
            n += layer_sizes[i-1] * layer_sizes[i]
        if b_trainable_arr and i < len(b_trainable_arr) and b_trainable_arr[i]:
            n += layer_sizes[i]
    if m_trainable_arr and m_trainable_arr[-1]:
        n += layer_sizes[-1] * num_outputs
    if b_trainable_arr and b_trainable_arr[-1]:
        n += num_outputs
    return n
