import random


def generate_secret_key(key_length: int) -> str:
    symbols = 'qwertyuiopasdfghjklzxcvbnm'
    numbers = '1234567890'
    symbols_list = list(symbols + symbols.upper() + numbers)
    return ''.join([random.choice(symbols_list) for _ in range(key_length)])


secret_key = generate_secret_key(100)
print(secret_key)
