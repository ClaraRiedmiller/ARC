# this file stores our testgrids

import numpy as np

# this is the test grid that looks a bit like a pacifier
grid1 = np.array([[None,None,None,None,None, None, None], 
                  [None,3,2,3,None, None, None], 
                  [None,3,None,3,3, None, None], 
                  [None,3,3,4,None, None, None], 
                  [None,None,None,None,None, None, None]]).astype(object)


# this is the test grid that looks a bit like a pacifier
grid2 = np.array([[None,None,None,None,None, None, None, None, None, None], 
                  [None,3,2,3,3, 3, None, None, None, None], 
                  [None,3,None, None, None,3, 3, None, None, None], 
                  [None,3,None, None, None,6, None, None, None, None], 
                  [None,3,None, None, None,6, None, None, None, None], 
                  [None,3,None, None, None,6, None, None, None, None], 
                  [None,6,6,3,6, 3, None, None, None, None],
                  [None,None,None,None,None, None, None, None, None, None],
                  [None,None,None,None,None, None, None, None, None, None],
                  [None,None,None,None,None, None, None, None, None, None]]).astype(object)