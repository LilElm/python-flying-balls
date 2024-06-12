# -*- coding: utf-8 -*-
"""
Created on Wed Jun 12 15:23:22 2024

@author: ultservi
"""



mylist = ["yoo", "boo", "coo", "doo"]
print(f"mylist = {mylist}")

#a, b = mylist

#unpack = *(mylist)
#print(f"a = {a}")
#print(f"b = {b}")

a, *b = mylist

print(f"a = {a}")
print(f"b = {b}")


input()