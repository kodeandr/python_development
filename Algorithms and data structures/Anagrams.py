def group_anagrams(words):
    groups = {}
    
    for word in words:
        # Создаем ключ - отсортированная версия слова в нижнем регистре
        key = ''.join(sorted(word.lower()))
        
        # Добавляем слово в соответствующую группу
        if key not in groups:
            groups[key] = []
        groups[key].append(word)
    
    # Сортируем слова внутри каждой группы
    for key in groups:
        groups[key].sort()
    
    # Получаем группы и сортируем их по первому элементу
    result = list(groups.values())
    result.sort(key=lambda x: x[0])
    
    return result

# Чтение входных данных
input_str = input().strip()
words = input_str.split()

# Группируем анаграммы
anagram_groups = group_anagrams(words)

# Вывод результата
for group in anagram_groups:
    print(' '.join(group))