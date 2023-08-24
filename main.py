import random
def encrypt(str1, str2):
    new_array = []
    for i in range(len(str1)):
        new_array.append(str1[i])
        new_array.append(str2[i])
    return random.shuffle(new_array)

str1 = ['h','l','a','d','f','t','r','w','d','t']
str2 = ['m','l','s','d','2','t','6','w','d','e']

print(encrypt(str1, str2))