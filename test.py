def calculate_average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

def find_maximum(numbers):
    if not numbers:
        return None
    return max(numbers)

def find_minimum(numbers):
    if not numbers:
        return None
    return min(numbers)