import random


class RandomGenerators:
     
    def generate_random_numbers(self, length):
        if length == "unlimited":
            length = random.randint(50, 100)

        else:
            length = int(length)

        if length <= 0:
            return ""

        first_digit = str(random.randint(1, 9))
        remaining_digits = ''.join([str(random.randint(0, 9))for _ in range(length - 1)])  
        return first_digit + remaining_digits  


        first_digit = str(random.randint(1,9))
        remaining_digits = ''.join([str(random.randint(0,9))for _ in range(length - 1)])
        return first_digit + remaining_digits
    
    def generate_random_text(self, length):
        if length == "unlimited":
            length = random.randint(50, 100)
        else:
            length = int(length)

        if length <=0:
            return ""

        letters =  "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        return ''.join(random.choice(letters)for _ in range(length))
    
    def generate_random_ip(self):
        return f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"
    