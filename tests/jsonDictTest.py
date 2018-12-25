import sys
import os
sys.path.append(os.getcwd()+'\\src')

from jsonDict import jsonDict

a = jsonDict("test")
print("JSON is currently at:")
print(a)
print()

print("Setting data key 10 = fish")
a[10] = "fish"
print("Current value of key 10:")
print(a[10])
print("Setting 'Goblin' to '5'")
a["Goblin"] = 5
print("Current data:")
print(a)
print()

print("Delete nonexistant key:")
del a['asdadf']
print("Delete key 10:")
del a[10]
print("Current data:")
print(a)

print("Check nonexistant key:")
print("abdasfas" in a)
print("Check Goblin")
print("Goblin" in a)