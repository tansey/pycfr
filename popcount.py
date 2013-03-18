class PopCount:
    # Generate table of popcounts for 16 bits
    # Then just use it twice.
    # Reference is some stanford paper. 
    # See http://www.valuedlessons.com/2009/01/popcount-in-python-with-benchmarks.html
    POPCOUNT_TABLE16 = [0] * 2**16
    for index in xrange(len(POPCOUNT_TABLE16)):
        POPCOUNT_TABLE16[index] = (index & 1) + POPCOUNT_TABLE16[index >> 1]

    def popcount32_table16(v):
        return (PopCount.POPCOUNT_TABLE16[v & 0xffff] + \
            PopCount.POPCOUNT_TABLE16[(v >> 16) & 0xffff])
    
    popcount = staticmethod(popcount32_table16)