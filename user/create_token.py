from django.test import TestCase

# Create your tests here.


import random
import string
import time


# ------------------------------------------------------------
# 可使用的字元來源
# string.ascii_letters, string.digits
# string.ascii_uppercase, string.ascii_lowercase
# ------------------------------------------------------------
def Rand_Abc2Num8():
    source = string.punctuation + string.digits + string.ascii_lowercase
    li_source = [i for i in source]
    token = random.sample(li_source, 50)
    token = ''.join(token)
    return token


print((Rand_Abc2Num8()))
