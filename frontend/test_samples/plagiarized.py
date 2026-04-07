def get_factorial(number_value):
    # This function computes the factorial
    
    if number_value < 0:
        return None
        
    # check base case
    if number_value == 0 or number_value == 1:
        return 1
        
    output_val = 1
    for index in range(2, number_value + 1):
        output_val = output_val * index
        
    return output_val

if __name__ == "__main__":
    test_number = 5
    result = get_factorial(test_number)
    print("Factorial result:", result)
