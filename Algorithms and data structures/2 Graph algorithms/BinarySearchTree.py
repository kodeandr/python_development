import sys

sys.setrecursionlimit(100000)

def is_bst(node, min_val, max_val, values, left, right):
    """
    Проверяет, является ли поддерево BST
    
    Args:
        node: текущий узел
        min_val: минимальное допустимое значение
        max_val: максимальное допустимое значение
        values: массив значений узлов
        left: массив левых потомков
        right: массив правых потомков
    
    Returns:
        True если поддерево является BST, иначе False
    """
    if node == -1:
        return True
    
    current_value = values[node]
    
    # Проверяем, находится ли значение в допустимом диапазоне
    if current_value <= min_val or current_value >= max_val:
        return False
    
    # Для левого поддерева: все значения должны быть < current_value
    # Для правого поддерева: все значения должны быть > current_value
    return (is_bst(left[node], min_val, current_value, values, left, right) and
            is_bst(right[node], current_value, max_val, values, left, right))

def main():
    # Читаем количество вершин
    n = int(sys.stdin.readline().strip())
    
    # Инициализируем массивы для хранения данных о дереве
    values = [0] * n
    left_children = [-1] * n
    right_children = [-1] * n
    
    # Читаем данные о каждой вершине
    for i in range(n):
        data = sys.stdin.readline().split()
        values[i] = int(data[0])
        left_children[i] = int(data[1])
        right_children[i] = int(data[2])
    
    # Проверяем, является ли дерево BST
    # Начинаем с корня и бесконечных границ
    result = is_bst(0, float('-inf'), float('inf'), values, left_children, right_children)
    
    print("TRUE" if result else "FALSE")

if __name__ == "__main__":
    main()