from typing import Iterable

# 01 INTRODUCTION
print("Hello wold")

# Defining variables
x = 5
print(x)
# Out: 5

# Summing variables
a = 3
b = 7
print(a+b)

# Conditional example
a = 10
if a == 10:
    print("Es 10")
else:
    print("No es 10")

# Decimals and strings
value_decimal = 10.3234
my_strings = "Hola wold"

# We can make multiple assignments
a, b, c = 4, 3, 2

# We perform some operations with a,b,c
d = (a + b) * c

# We define a Boolean variable
printer = True

# If printer, print()
if printer:
    print(x, d)

# Comments
'''
This is a comment
of several lines
of code
'''
# Indentation and code blocks
if True:
    print("True") # The general rule is to use four spaces.

# Multiple lines
'''
-Do not exceed 79 characters.
-Using '\' can break the code into several lines.
'''
x = 1 + 2 + 3 + 4 +\
    5 + 6 + 7 + 8

x2 = (1 + 2 + 3 + 4 +
     5 + 6 + 7 + 8)

print(x)

def funcion(a1, b1, c1):
    return a1+b1+c1

d = funcion(10,
23,
3)

# Assign the same value to different variables
x = y = z = 10

x3, y3 = 4, 2

x4, y4, z4 = 1, 2, 3

# Naming variables
'''
# Invalid
-El nombre no puede empezar por un número.
-No se permite el uso de guiones -
-Tampoco se permite el uso de espacios.
-No usar nombres reservados para Python
'''
# Valid
_variable = 10
vari_able = 20
variable10 = 30
variable = 60
variaBle = 10

import keyword
print(keyword.kwlist)

# Variables and scope of application
x5 = 10 # globally

def funcion():
    x5 = 5 # local

funcion()
print(x)

# Dynamic typing
class Pato:
    def speak(self):
        print("¡Cua!, Cua!")
p = Pato()
p.speak()
# ¡Cua!, Cua!

def call_speak(x):
    x.speak()

call_speak(Pato())

# 02 CONTROL STRUCTURES
#for <variable> in <iterable>:
#    <Code>
for i in range(0, 5):
    print(i)
for i in "Python":
    print(i)
# Iterables and iterators
lista = [1, 2, 3, 4]
cadena = "Python"
number = 10

print(isinstance(lista, Iterable))  # True
print(isinstance(cadena, Iterable))  # True
print(isinstance(number, Iterable))  # False

lista = [5, 6, 3, 2]
it = iter(lista)
print(it)       #<list_iterator object at 0x106243828>
print(type(it)) #<class 'list_iterator'>

it = iter(lista)
print(next(it))

#FOR ANITY
lista = [[56, 34, 1],
         [12, 4, 5],
         [9, 4, 3]]
for i in lista:
    print(i)

for i in lista:
    for j in i:
        print(j)
# Exit: 56,34,1,12,4,5,9,4,3

print("--------")

x = 5
while x > 0:
    x -=1
    print(x)

# Exit: 4,3,2,1,0

# 03 TYPES AND STRUCTURES
# Lists
a = [90, "Python", 3.87]
print(a[0]) #90
print(a[1]) #Python
print(a[2]) #3.87

# 04 FUNCTIONS
#def name_function(arguments):
   # <code>
   # return

def f(x):
    return 2*x
y = f(3)
print(y) # 6

# 04 FUNCTIONS
# Step by value and reference
x = 10
def funcion_x(entry):
    entry = 0
funcion_x(x)

print(x) # 10

x = [10, 20, 30]
def funcion_y(entry):
    entry.append(40)

funcion_y(x)
print(x) # [10, 20, 30, 40]

# Args and Kwargs
def suma(*args):
    s = 0
    for arg in args:
        s += arg
    return s

print(suma(1, 3, 4, 2))
#Salida 10

suma(1, 1)
#Salida 2

def funcion(a, b, *args, **kwargs):
    print("a =", a)
    print("b =", b)
    for arg in args:
        print("args =", arg)
    for key, value in kwargs.items():
        print(key, "=", value)

args = [1, 2, 3, 4]
kwargs = {'x':"Hola", 'y':"Que", 'z':"Tal"}

funcion(10, 20, *args, **kwargs)

# OOP Object Oriented Programming
# Creating an empty class
class Dog:
    pass
# We create an object of the dog class
my_dog = Dog()


class Dog:
# Class attribute
    species = 'mammal'

# The __init__ method is called when creating the object. This is the builder (constructor)
    def __init__(self, name, race):
        print(f"Create dog {name}, {race}")

        # Instance attributes
        self.name = name
        self.race = race

# Defining methods
    def ladra(self):
        print("Guau")

    def camina(self, pasos):
        print(f"Walking {pasos} steps")

my_dog2 = Dog("Toby", "Bulldog")

print(type(my_dog2))
# Create dog Toby, Bulldog
# <class '__main__.Dog'>

print(my_dog2.name) # Toby
print(my_dog2.race) # Bulldog
print(my_dog2.species)
# mammal

my_dog2.ladra()
my_dog2.camina(10)

# Guau
# Walking 10 steps

#Methods in Python: Instance, Class, and Static
class Clase:
    # Instance Methods
    def metodo(self, arg1, arg2):
        return 'Método normal', self

    @classmethod
    def metododeclase(cls):
        return 'Método de clase', cls

    @staticmethod
    def metodoestatico():
        return "Método estático"

my_class = Clase()
print(my_class.metodo("a", "b"))
# ('Normal method', <__main__.Class object at 0x00000269512FDD30>)

# Inheritance
# We define a parent class
class Animal:
    pass

# We create a child class that inherits from the parent class
class DogTwo(Animal):
    pass

print(DogTwo.__bases__)
# (<class '__main__.Animal'>,)

print(Animal.__subclasses__())
# [<class '__main__.DogTwo'>]