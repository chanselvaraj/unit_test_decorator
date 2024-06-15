from create_test import create_test_data

class calculation:
    def __init__(self):
        print('temp')
    @create_test_data()
    def sum_of_even(self,numbers):
        res = sum([num for num in numbers if num % 2 == 0])
        return res

if __name__ == "__main__":
    cobj = calculation()
    input = [1,2,3,4,5,6,7,8]
    output = cobj.sum_of_even(input)
    input = [9,10,11,12,13,14]
    output = cobj.sum_of_even(input)
    input = [15,16,17,18,19,20]
    output = cobj.sum_of_even(input)
    print(output)