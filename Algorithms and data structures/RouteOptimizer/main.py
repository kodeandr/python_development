"""
Программа оптимизации маршрутов для логистической компании
Решает задачу многокритериальной оптимизации маршрутов
"""

import heapq
import re
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
from enum import Enum


class Criterion(Enum):
    """Критерии оптимизации"""
    LENGTH = 'Д'
    TIME = 'В'
    COST = 'С'
    
    def get_field_index(self) -> int:
        """Возвращает индекс параметра в данных дороги"""
        mapping = {
            Criterion.LENGTH: 0,
            Criterion.TIME: 1,
            Criterion.COST: 2
        }
        return mapping[self]


class RoutePlanner:
    """Основной класс для планирования маршрутов"""
    
    def __init__(self):
        self.city_id_to_name: Dict[int, str] = {}
        self.city_name_to_id: Dict[str, int] = {}
        self.graph: Dict[int, List[Tuple[int, int, int, int]]] = defaultdict(list)
    
    def load_data(self, filename: str) -> None:
        """Загрузка данных из файла"""
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Парсинг секции CITIES
        cities_match = re.search(r'\[CITIES\](.*?)(?=\[|\Z)', content, re.DOTALL)
        if cities_match:
            for line in cities_match.group(1).strip().split('\n'):
                if line.strip():
                    match = re.match(r'(\d+):\s*(.+)', line.strip())
                    if match:
                        city_id = int(match.group(1))
                        city_name = match.group(2).strip()
                        self.city_id_to_name[city_id] = city_name
                        self.city_name_to_id[city_name] = city_id
        
        # Парсинг секции ROADS
        roads_match = re.search(r'\[ROADS\](.*?)(?=\[|\Z)', content, re.DOTALL)
        if roads_match:
            for line in roads_match.group(1).strip().split('\n'):
                if line.strip():
                    # Обрабатываем форматы: "1 - 2: 700, 480, 800" и "1-2: 700, 480, 800"
                    match = re.match(r'(\d+)\s*-\s*(\d+):\s*(\d+),\s*(\d+),\s*(\d+)', line.strip())
                    if match:
                        city1 = int(match.group(1))
                        city2 = int(match.group(2))
                        length = int(match.group(3))
                        time = int(match.group(4))
                        cost = int(match.group(5))
                        
                        # Добавляем двустороннюю дорогу
                        self.graph[city1].append((city2, length, time, cost))
                        self.graph[city2].append((city1, length, time, cost))
    
    def parse_requests(self, filename: str) -> List[Tuple[str, str, List[str]]]:
        """Парсинг запросов из файла"""
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        requests = []
        requests_match = re.search(r'\[REQUESTS\](.*?)(?=\[|\Z)', content, re.DOTALL)
        
        if requests_match:
            for line in requests_match.group(1).strip().split('\n'):
                if line.strip():
                    match = re.match(r'(.+)\s*->\s*(.+)\s*\|\s*\(([Д,В,С]+)\)', line.strip())
                    if match:
                        from_city = match.group(1).strip()
                        to_city = match.group(2).strip()
                        priorities = match.group(3).split(',')
                        requests.append((from_city, to_city, priorities))
        
        return requests
    
    def dijkstra(self, start: int, end: int, criterion: Criterion) -> Optional[Tuple[List[int], int, int, int]]:
        """
        Алгоритм Дейкстры для поиска оптимального пути по одному критерию
        
        Сложность: O((V + E) * log V)
        где V - количество вершин (городов), E - количество рёбер (дорог)
        """
        if start not in self.graph or end not in self.graph:
            return None
        
        # Инициализация структур данных
        distances = {start: 0}
        previous = {start: None}
        priority_queue = [(0, start)]
        
        # Для хранения полных параметров пути (длина, время, стоимость)
        full_params = {start: (0, 0, 0)}
        
        while priority_queue:
            current_dist, current_city = heapq.heappop(priority_queue)
            
            # Если достигли конечной точки
            if current_city == end:
                break
            
            # Если текущее расстояние больше сохранённого
            if current_dist > distances[current_city]:
                continue
            
            # Обработка соседей
            for neighbor, length, time, cost in self.graph[current_city]:
                # Получаем вес по выбранному критерию
                if criterion == Criterion.LENGTH:
                    weight = length
                elif criterion == Criterion.TIME:
                    weight = time
                else:  # Criterion.COST
                    weight = cost
                
                new_distance = distances[current_city] + weight
                
                # Вычисляем полные параметры пути
                current_length, current_time, current_cost = full_params[current_city]
                new_length = current_length + length
                new_time = current_time + time
                new_cost = current_cost + cost
                
                if neighbor not in distances or new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    full_params[neighbor] = (new_length, new_time, new_cost)
                    previous[neighbor] = current_city
                    heapq.heappush(priority_queue, (new_distance, neighbor))
        
        # Восстановление пути
        if end not in distances:
            return None
        
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        
        length, time, cost = full_params[end]
        return path, length, time, cost
    
    def find_optimal_routes(self, from_city: str, to_city: str) -> Dict[str, Optional[Tuple[List[str], int, int, int]]]:
        """Нахождение оптимальных маршрутов по всем критериям"""
        if from_city not in self.city_name_to_id or to_city not in self.city_name_to_id:
            return {criterion: None for criterion in ['ДЛИНА', 'ВРЕМЯ', 'СТОИМОСТЬ']}
        
        start_id = self.city_name_to_id[from_city]
        end_id = self.city_name_to_id[to_city]
        
        results = {}
        
        # Поиск оптимальных маршрутов по каждому критерию
        for criterion in [Criterion.LENGTH, Criterion.TIME, Criterion.COST]:
            result = self.dijkstra(start_id, end_id, criterion)
            
            if result:
                path_ids, length, time, cost = result
                path_names = [self.city_id_to_name[city_id] for city_id in path_ids]
                if criterion == Criterion.LENGTH:
                    results['ДЛИНА'] = (path_names, length, time, cost)
                elif criterion == Criterion.TIME:
                    results['ВРЕМЯ'] = (path_names, length, time, cost)
                else:
                    results['СТОИМОСТЬ'] = (path_names, length, time, cost)
            else:
                if criterion == Criterion.LENGTH:
                    results['ДЛИНА'] = None
                elif criterion == Criterion.TIME:
                    results['ВРЕМЯ'] = None
                else:
                    results['СТОИМОСТЬ'] = None
        
        return results
    
    def find_compromise_route(self, routes: Dict[str, Optional[Tuple[List[str], int, int, int]]], 
                             priorities: List[str]) -> Optional[Tuple[List[str], int, int, int]]:
        """
        Нахождение компромиссного маршрута на основе приоритетов
        
        Алгоритм использует лексикографическую сортировку по приоритетам
        """
        # Фильтруем существующие маршруты
        available_routes = []
        
        for criterion_name, route_data in routes.items():
            if route_data is not None:
                path, length, time, cost = route_data
                # Сопоставляем имя критерия с символом
                criterion_symbol = {'ДЛИНА': 'Д', 'ВРЕМЯ': 'В', 'СТОИМОСТЬ': 'С'}[criterion_name]
                available_routes.append((criterion_symbol, path, length, time, cost))
        
        if not available_routes:
            return None
        
        # Создаем отображение приоритетов для сортировки
        priority_order = {priority: i for i, priority in enumerate(priorities)}
        
        # Сортируем маршруты по приоритетам
        def sort_key(route):
            criterion_symbol, path, length, time, cost = route
            params = {'Д': length, 'В': time, 'С': cost}
            return tuple(params[priority] for priority in priorities)
        
        available_routes.sort(key=sort_key)
        
        # Возвращаем лучший маршрут
        best_route = available_routes[0]
        return best_route[1:]  # Пропускаем criterion_symbol
    
    def process_requests(self, input_file: str, output_file: str) -> None:
        """Основной метод обработки запросов"""
        self.load_data(input_file)
        requests = self.parse_requests(input_file)
        
        output_lines = []
        
        for from_city, to_city, priorities in requests:
            output_lines.append(f"Запрос: {from_city} -> {to_city}")
            
            # Находим оптимальные маршруты по всем критериям
            optimal_routes = self.find_optimal_routes(from_city, to_city)
            
            # Выводим оптимальные маршруты
            for criterion_name in ['ДЛИНА', 'ВРЕМЯ', 'СТОИМОСТЬ']:
                route_data = optimal_routes[criterion_name]
                if route_data:
                    path, length, time, cost = route_data
                    path_str = " -> ".join(path)
                    output_lines.append(
                        f"{criterion_name}: {path_str} | Д={length}, В={time}, С={cost}"
                    )
                else:
                    output_lines.append(f"{criterion_name}: Маршрут не найден")
            
            # Находим и выводим компромиссный маршрут
            compromise_data = self.find_compromise_route(optimal_routes, priorities)
            if compromise_data:
                path, length, time, cost = compromise_data
                path_str = " -> ".join(path)
                output_lines.append(
                    f"КОМПРОМИСС: {path_str} | Д={length}, В={time}, С={cost}"
                )
            else:
                output_lines.append("КОМПРОМИСС: Маршрут не найден")
            
            output_lines.append("")  # Пустая строка между запросами
        
        # Записываем результаты в файл
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(output_lines))


def main():
    """Точка входа в программу"""
    try:
        planner = RoutePlanner()
        planner.process_requests("input.txt", "output.txt")
        print("Обработка завершена. Результаты записаны в output.txt")
    except FileNotFoundError:
        print("Ошибка: Файл input.txt не найден")
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")


if __name__ == "__main__":
    main()