import math

def compute_convolution_output_dimensions(i, k, s=None, p=None, transposed=False):
    def regular_conv(_i, _k, _s, _p):
        return math.floor((_i + 2 * _p - _k) / _s) + 1
    
    def transposed_conv(_i, _k, _s, _p):
        """
        A convolution described by k, s and p and whose input size i is such that i+2p−k is a multiple of s has an
        associated transposed convolution described by î , k' = k, s' = 1 and p' = k − p − 1, where î  is the
        size of the stretched input obtained by adding s − 1 zeros between each input unit, and its output size is
        """
        return _s * (_i - 1) + _k - 2 * _p
    
    i = (i,) if isinstance(i, int) else i
    k = (k,) * len(i) if isinstance(k, int) else k

    s = s if s is not None else [1] * len(i)
    s = (s,) * len(i) if isinstance(s, int) else s
    p = p if p is not None else [0] * len(i)
    p = (p,) * len(i) if isinstance(p, int) else p
    
    if not transposed:
        return [regular_conv(_i, _k, _s, _p) for _i, _k, _s, _p in zip(i, k, s, p)]
    return [transposed_conv(_i, _k, _s, _p) for _i, _k, _s, _p in zip(i, k, s, p)]
