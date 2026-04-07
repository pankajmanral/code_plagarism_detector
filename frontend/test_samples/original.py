def calculate_factorial(n):
    """
    Calculate the factorial of a given number.
    """
    if n < 0:
        return None
    elif n == 0 or n == 1:
        return 1
    
    result = 1
    for i in range(2, n + 1):
        result *= i
        
    return result

if __name__ == "__main__":
    num = 5
    fact = calculate_factorial(num)
    print(f"The factorial of {num} is {fact}")
