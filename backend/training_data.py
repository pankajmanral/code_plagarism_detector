"""
training_data.py — Generate labelled training data for the KNN classifier.

Creates pairs of Python code snippets that are either:
  • **plagiarised** (label=1) — same logic with renamed variables,
    reordered statements, minor structural changes
  • **original** (label=0) — genuinely different algorithms

The generated dataset is intentionally diverse so the KNN model
learns a robust decision boundary.
"""


# ═══════════════════════════════════════════════════════════════════════════════
# ORIGINAL CODE SAMPLES — distinct algorithms / tasks
# ═══════════════════════════════════════════════════════════════════════════════

ORIGINALS: list[str] = [
    # 0 — bubble sort
    '''
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
''',

    # 1 — binary search
    '''
def binary_search(arr, target):
    low, high = 0, len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
''',

    # 2 — fibonacci recursive
    '''
def fibonacci(n):
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)
''',

    # 3 — factorial iterative
    '''
def factorial(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
''',

    # 4 — matrix multiply
    '''
def matrix_multiply(a, b):
    rows_a, cols_a = len(a), len(a[0])
    rows_b, cols_b = len(b), len(b[0])
    result = [[0] * cols_b for _ in range(rows_a)]
    for i in range(rows_a):
        for j in range(cols_b):
            for k in range(cols_a):
                result[i][j] += a[i][k] * b[k][j]
    return result
''',

    # 5 — linked list
    '''
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node

    def display(self):
        elements = []
        current = self.head
        while current:
            elements.append(current.data)
            current = current.next
        return elements
''',

    # 6 — prime sieve
    '''
def sieve_of_eratosthenes(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit ** 0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    return [i for i in range(limit + 1) if is_prime[i]]
''',

    # 7 — stack implementation
    '''
class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.is_empty():
            return self.items.pop()
        raise IndexError("Stack is empty")

    def peek(self):
        if not self.is_empty():
            return self.items[-1]
        raise IndexError("Stack is empty")

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)
''',

    # 8 — BFS
    '''
from collections import deque

def bfs(graph, start):
    visited = set()
    queue = deque([start])
    visited.add(start)
    result = []
    while queue:
        vertex = queue.popleft()
        result.append(vertex)
        for neighbor in graph[vertex]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return result
''',

    # 9 — merge sort
    '''
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
''',

    # 10 — quicksort
    '''
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
''',

    # 11 — DFS
    '''
def dfs(graph, start, visited=None):
    if visited is None:
        visited = set()
    visited.add(start)
    result = [start]
    for neighbor in graph[start]:
        if neighbor not in visited:
            result.extend(dfs(graph, neighbor, visited))
    return result
''',

    # 12 — caesar cipher
    '''
def caesar_encrypt(text, shift):
    result = []
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            shifted = (ord(char) - base + shift) % 26 + base
            result.append(chr(shifted))
        else:
            result.append(char)
    return ''.join(result)

def caesar_decrypt(text, shift):
    return caesar_encrypt(text, -shift)
''',

    # 13 — word counter
    '''
def count_words(text):
    words = text.lower().split()
    frequency = {}
    for word in words:
        clean_word = ''.join(c for c in word if c.isalnum())
        if clean_word:
            frequency[clean_word] = frequency.get(clean_word, 0) + 1
    return dict(sorted(frequency.items(), key=lambda x: x[1], reverse=True))
''',

    # 14 — temperature converter
    '''
def celsius_to_fahrenheit(celsius):
    return celsius * 9 / 5 + 32

def fahrenheit_to_celsius(fahrenheit):
    return (fahrenheit - 32) * 5 / 9

def celsius_to_kelvin(celsius):
    return celsius + 273.15

def kelvin_to_celsius(kelvin):
    return kelvin - 273.15
''',
]


# ═══════════════════════════════════════════════════════════════════════════════
# PLAGIARISED VARIANTS — same logic, surface-level changes
# ═══════════════════════════════════════════════════════════════════════════════

PLAGIARISED_VARIANTS: list[tuple[int, str]] = [
    # variant of 0 — renamed vars
    (0, '''
def sort_array(data):
    length = len(data)
    for x in range(length):
        for y in range(0, length - x - 1):
            if data[y] > data[y + 1]:
                data[y], data[y + 1] = data[y + 1], data[y]
    return data
'''),

    # variant of 0 — while-loop version
    (0, '''
def my_sort(lst):
    n = len(lst)
    i = 0
    while i < n:
        j = 0
        while j < n - i - 1:
            if lst[j] > lst[j + 1]:
                temp = lst[j]
                lst[j] = lst[j + 1]
                lst[j + 1] = temp
            j += 1
        i += 1
    return lst
'''),

    # variant of 1 — renamed
    (1, '''
def search(numbers, value):
    start, end = 0, len(numbers) - 1
    while start <= end:
        middle = (start + end) // 2
        if numbers[middle] == value:
            return middle
        elif numbers[middle] < value:
            start = middle + 1
        else:
            end = middle - 1
    return -1
'''),

    # variant of 2 — renamed + different base case style
    (2, '''
def fib(num):
    if num <= 0:
        return 0
    if num == 1:
        return 1
    return fib(num - 1) + fib(num - 2)
'''),

    # variant of 3 — using while loop
    (3, '''
def compute_factorial(number):
    output = 1
    counter = 2
    while counter <= number:
        output = output * counter
        counter += 1
    return output
'''),

    # variant of 4 — renamed
    (4, '''
def multiply_matrices(mat1, mat2):
    r1, c1 = len(mat1), len(mat1[0])
    r2, c2 = len(mat2), len(mat2[0])
    res = [[0] * c2 for _ in range(r1)]
    for row in range(r1):
        for col in range(c2):
            for idx in range(c1):
                res[row][col] += mat1[row][idx] * mat2[idx][col]
    return res
'''),

    # variant of 5 — renamed
    (5, '''
class ListNode:
    def __init__(self, value):
        self.value = value
        self.next_node = None

class SinglyLinkedList:
    def __init__(self):
        self.first = None

    def add(self, value):
        node = ListNode(value)
        if not self.first:
            self.first = node
            return
        temp = self.first
        while temp.next_node:
            temp = temp.next_node
        temp.next_node = node

    def to_list(self):
        items = []
        temp = self.first
        while temp:
            items.append(temp.value)
            temp = temp.next_node
        return items
'''),

    # variant of 6 — different variable names
    (6, '''
def find_primes(n):
    flags = [True] * (n + 1)
    flags[0] = flags[1] = False
    for num in range(2, int(n ** 0.5) + 1):
        if flags[num]:
            for multiple in range(num * num, n + 1, num):
                flags[multiple] = False
    return [x for x in range(n + 1) if flags[x]]
'''),

    # variant of 7 — renamed
    (7, '''
class MyStack:
    def __init__(self):
        self.data = []

    def add(self, element):
        self.data.append(element)

    def remove(self):
        if not self.empty():
            return self.data.pop()
        raise IndexError("Nothing to remove")

    def top(self):
        if not self.empty():
            return self.data[-1]
        raise IndexError("Nothing to see")

    def empty(self):
        return len(self.data) == 0

    def count(self):
        return len(self.data)
'''),

    # variant of 8 — renamed
    (8, '''
from collections import deque

def breadth_first(adj, source):
    seen = set()
    q = deque([source])
    seen.add(source)
    order = []
    while q:
        node = q.popleft()
        order.append(node)
        for nb in adj[node]:
            if nb not in seen:
                seen.add(nb)
                q.append(nb)
    return order
'''),

    # variant of 9 — renamed
    (9, '''
def msort(data):
    if len(data) <= 1:
        return data
    middle = len(data) // 2
    left_half = msort(data[:middle])
    right_half = msort(data[middle:])
    return combine(left_half, right_half)

def combine(a, b):
    merged = []
    x = y = 0
    while x < len(a) and y < len(b):
        if a[x] <= b[y]:
            merged.append(a[x])
            x += 1
        else:
            merged.append(b[y])
            y += 1
    merged.extend(a[x:])
    merged.extend(b[y:])
    return merged
'''),

    # variant of 10 — renamed
    (10, '''
def qsort(data):
    if len(data) <= 1:
        return data
    p = data[len(data) // 2]
    lo = [v for v in data if v < p]
    eq = [v for v in data if v == p]
    hi = [v for v in data if v > p]
    return qsort(lo) + eq + qsort(hi)
'''),

    # variant of 11 — renamed
    (11, '''
def depth_first(adj, node, seen=None):
    if seen is None:
        seen = set()
    seen.add(node)
    path = [node]
    for nb in adj[node]:
        if nb not in seen:
            path.extend(depth_first(adj, nb, seen))
    return path
'''),

    # variant of 12 — renamed
    (12, '''
def encode(message, offset):
    output = []
    for ch in message:
        if ch.isalpha():
            start = ord('A') if ch.isupper() else ord('a')
            new_char = (ord(ch) - start + offset) % 26 + start
            output.append(chr(new_char))
        else:
            output.append(ch)
    return ''.join(output)

def decode(message, offset):
    return encode(message, -offset)
'''),

    # variant of 13 — renamed + slightly different
    (13, '''
def word_frequency(paragraph):
    tokens = paragraph.lower().split()
    counts = {}
    for token in tokens:
        cleaned = ''.join(ch for ch in token if ch.isalnum())
        if cleaned:
            counts[cleaned] = counts.get(cleaned, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))
'''),

    # variant of 14 — renamed
    (14, '''
def c_to_f(c):
    return c * 9 / 5 + 32

def f_to_c(f):
    return (f - 32) * 5 / 9

def c_to_k(c):
    return c + 273.15

def k_to_c(k):
    return k - 273.15
'''),
]


def generate_training_pairs() -> tuple[list[tuple[str, str]], list[int]]:
    """
    Build the full training dataset.

    Returns
    -------
    pairs  : list of (code_a, code_b)
    labels : list of int  (1 = plagiarised, 0 = original)
    """
    pairs: list[tuple[str, str]] = []
    labels: list[int] = []

    # ── Plagiarised pairs (label = 1) ─────────────────────────────────────
    for orig_idx, variant in PLAGIARISED_VARIANTS:
        pairs.append((ORIGINALS[orig_idx], variant))
        labels.append(1)

    # ── Original pairs (label = 0) — combine distinct algorithms ──────────
    n = len(ORIGINALS)
    for i in range(n):
        for j in range(i + 1, n):
            # Skip if indices are close (they might be somewhat related)
            if abs(i - j) >= 2:
                pairs.append((ORIGINALS[i], ORIGINALS[j]))
                labels.append(0)

    return pairs, labels
