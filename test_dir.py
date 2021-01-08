import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CURR_DIR_0= os.path.dirname(os.path.realpath(__file__))
CURR_DIR_1 = os.getcwd()

print("BASE_DIR : ", BASE_DIR)
print("CURR_DIR_0 : ", CURR_DIR_0)
print("CURR_DIR_1 : ", CURR_DIR_1)
