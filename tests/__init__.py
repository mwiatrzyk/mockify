import os
import sys

this_dir = os.path.abspath(os.path.dirname(__file__))
root_dir = os.path.join(this_dir, '..')
src_dir = os.path.join(root_dir, 'src')

sys.path.insert(0, src_dir)
sys.path.insert(1, root_dir)
