class Solution:
   def solve(self, older, newer):
      older = older.split('.')
      newer=newer.split('.')
      for o, n in zip(older, newer):
         print(n,o)
#          if int(n)>int(o):
#             return True
#          elif int(n)<int(o):
#             print(n,o)
#             return False
      return False
ob = Solution()
older = "7.2.2"
newer = "7.3.1"
print(ob.solve(older, newer))