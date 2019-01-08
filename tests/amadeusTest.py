import sys
import os
sys.path.append(os.getcwd()+'\\src')

from Amadeus import Amadeus

print("Amadeas Testing")
driver = Amadeus()
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

inStr = "DearPhilip"
print("\nAdd Stack {0}".format(inStr))
driver.addStack(inStr)
print(driver.getStack())
print("Remove stack {0}".format(inStr))
driver.removeStack(inStr)
print(driver.getStack())
print("Remove stack {0} again".format(inStr))
driver.removeStack(inStr)
print(driver.getStack())