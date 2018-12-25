import sys
import os
sys.path.append(os.getcwd()+'\\src')

from Amadeas import Amadeas

print("Amadeas Testing")
driver = Amadeas()
print("\nInitalized as:")
print(driver)

print("Add alias Garbage:")
driver.addAlias("123","456")
print("Add SlimeLongName to stack")
driver.addStack("SlimeLongName")
print("Add alias Slime to SlimeLongName")
driver.addAlias("SlimeLongName", "Slime")
print("Add alias BigSlime to Slime")
driver.addAlias("Slime", "BigSlime")
print(driver)

print("\nDelete BigSlime.")
driver.removeAlias("BigSlime")
print("Delete more Garbage.")
driver.removeAlias("CASDF")
print(driver)