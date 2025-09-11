import random

symblos = 'qwertyuiopasdfghjklzxcvbnm'
symblos_list = list(symblos + symblos.upper() + '1234567890')
print(''.join([random.choice(symblos_list) for i in range(50)]))


# from main import hash_password
# print(hash_password("admin"))
