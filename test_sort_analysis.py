import os
import random
import time
import csv
import matplotlib.pyplot as plt

#  Реализация Tree Sort 

class TreeNode: # Узел бинарного дерева поиска
    __slots__ = ('key', 'left', 'right')
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None

class TreeSort: # Класс, реализующий сортировку деревом с подсчётом операций
    def __init__(self):
        self.comparisons = 0   # счётчик сравнений (итераций)

    def insert(self, root, key): # Вставка ключа в BST. Возвращает новый корень (если дерево было пустым)
        if root is None:
            return TreeNode(key)
        self.comparisons += 1
        if key < root.key:
            root.left = self.insert(root.left, key)
        else:
            root.right = self.insert(root.right, key)
        return root

    def inorder_traversal(self, root, result): # Симметричный обход, заполняет список result
        if root is not None:
            self.inorder_traversal(root.left, result)
            result.append(root.key)
            self.inorder_traversal(root.right, result)

    def sort(self, arr): # Сортирует массив arr, возвращает отсортированную копию и сбрасывает счётчик
        self.comparisons = 0
        root = None
        for key in arr:
            root = self.insert(root, key)
        sorted_arr = []
        self.inorder_traversal(root, sorted_arr)
        return sorted_arr


# Генерация входных данных 

def generate_datasets(output_dir="input_data", num_files=100, min_size=100, max_size=10000):
    """
    Генерирует num_files файлов со случайными целыми числами.
    Размер каждого файла выбирается случайно в диапазоне [min_size, max_size].
    Возвращает словарь {имя_файла: размер} для последующего использования.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    file_sizes = {}
    for i in range(num_files):
        size = random.randint(min_size, max_size)
        data = [random.randint(1, 100000) for _ in range(size)]
        filename = f"data_{i:03d}_size_{size}.txt"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w') as f:
            f.write('\n'.join(map(str, data)))
        file_sizes[filename] = size
    
    print(f"Сгенерировано {num_files} файлов в папке '{output_dir}'.")
    return file_sizes


# Измерения 

def measure_sorting_from_file(filename, sorter): # Читает массив из файла, измеряет время и итерации только сортировки
    with open(filename, 'r') as f:
        arr = [int(line.strip()) for line in f if line.strip()]
    start_time = time.perf_counter()
    sorted_arr = sorter.sort(arr)
    end_time = time.perf_counter()
    elapsed = end_time - start_time
    comparisons = sorter.comparisons
    return elapsed, comparisons

def extract_size_from_filename(filename): # Извлекает размер массива из имени файла
    # Ищем часть между 'size_' и '.txt'
    import re
    match = re.search(r'size_(\d+)\.txt', filename)
    if match:
        return int(match.group(1))
    # Альтернативный метод: разбиваем по '_' и ищем число
    parts = filename.replace('.txt', '').split('_')
    for part in parts:
        if part.isdigit():
            # Проверяем, что это размер, а не номер файла
            # Размер обычно больше номера файла
            num = int(part)
            if num >= 100:  # минимальный размер по условию
                return num
    raise ValueError(f"Не удалось извлечь размер из имени файла: {filename}")

def run_experiments(data_dir="input_data"): # Обрабатывает все файлы в data_dir, собирает результаты
    sorter = TreeSort()
    results = []   # список кортежей: (size, time, comparisons)
    
    files = sorted([f for f in os.listdir(data_dir) if f.endswith('.txt')])
    
    if not files:
        print(f"В папке '{data_dir}' нет файлов .txt. Запустите генерацию данных.")
        return results
    
    for file in files:
        filepath = os.path.join(data_dir, file)
        try:
            size = extract_size_from_filename(file)
        except ValueError as e:
            print(f"Ошибка при обработке файла {file}: {e}")
            continue
        
        t, comps = measure_sorting_from_file(filepath, sorter)
        results.append((size, t, comps))
        print(f"Файл: {file}, размер: {size}, время: {t:.6f} с, сравнений: {comps}")
    
    return results

def save_results_to_csv(results, csv_filename="results.csv"): # Сохраняет таблицу результатов в CSV
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Size", "Time_sec", "Comparisons"])
        writer.writerows(results)
    print(f"Результаты сохранены в '{csv_filename}'.")


# Построение графиков 

def plot_results(results): # Строит графики зависимости времени и числа сравнений от размера
    if not results:
        print("Нет данных для построения графиков.")
        return
    
    sizes = [r[0] for r in results]
    times = [r[1] for r in results]
    comps = [r[2] for r in results]

    # Сортировка по размеру для корректного отображения
    sorted_indices = sorted(range(len(sizes)), key=lambda k: sizes[k])
    sizes = [sizes[i] for i in sorted_indices]
    times = [times[i] for i in sorted_indices]
    comps = [comps[i] for i in sorted_indices]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    ax1.scatter(sizes, times, alpha=0.6, edgecolors='k', s=30)
    ax1.set_xlabel('Размер массива')
    ax1.set_ylabel('Время выполнения, с')
    ax1.set_title('Зависимость времени от размера')
    ax1.grid(True, linestyle='--', alpha=0.7)

    # Добавляем линию тренда для времени
    if len(sizes) > 1:
        import numpy as np
        z = np.polyfit(sizes, times, 2)
        p = np.poly1d(z)
        x_trend = np.linspace(min(sizes), max(sizes), 100)
        ax1.plot(x_trend, p(x_trend), "r--", alpha=0.8, label="Тренд O(n log n)")
        ax1.legend()

    ax2.scatter(sizes, comps, alpha=0.6, edgecolors='k', s=30, color='orange')
    ax2.set_xlabel('Размер массива')
    ax2.set_ylabel('Количество сравнений')
    ax2.set_title('Зависимость числа сравнений от размера')
    ax2.grid(True, linestyle='--', alpha=0.7)

    # Добавляем теоретическую кривую n*log2(n) для сравнения
    if len(sizes) > 1:
        import numpy as np
        x_theory = np.linspace(min(sizes), max(sizes), 100)
        y_theory = x_theory * np.log2(x_theory)
        # Масштабируем для визуального сравнения
        scale_factor = max(comps) / max(y_theory) if max(y_theory) > 0 else 1
        ax2.plot(x_theory, y_theory * scale_factor, "g--", alpha=0.8, 
                label=f"Теоретическая n·log₂(n) (масштаб ×{scale_factor:.2f})")
        ax2.legend()

    plt.tight_layout()
    plt.savefig('tree_sort_plots.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("Графики сохранены в 'tree_sort_plots.png' и отображены на экране.")


# Главная функция 

def main():
    # 1. Генерация данных
    if not os.path.exists("input_data") or len([f for f in os.listdir("input_data") if f.endswith('.txt')]) == 0:
        print("Генерация новых входных данных...")
        generate_datasets()
    else:
        print("Папка 'input_data' уже содержит файлы .txt")
        response = input("Сгенерировать новые данные? (y/n): ").strip().lower()
        if response == 'y':
            # Очищаем папку от старых файлов
            for f in os.listdir("input_data"):
                if f.endswith('.txt'):
                    os.remove(os.path.join("input_data", f))
            generate_datasets()

    # 2. Проведение экспериментов
    print("\nЗапуск измерений...")
    results = run_experiments()

    if not results:
        print("Не удалось получить результаты измерений.")
        return

    # 3. Сохранение таблицы
    save_results_to_csv(results)

    # 4. Построение графиков
    plot_results(results)

    # 5. Вывод статистики
    print("\n--- Статистика ---")
    sizes = [r[0] for r in results]
    times = [r[1] for r in results]
    comps = [r[2] for r in results]
    print(f"Количество файлов: {len(results)}")
    print(f"Размеры: от {min(sizes)} до {max(sizes)}")
    print(f"Время: от {min(times):.6f} до {max(times):.6f} сек")
    print(f"Сравнения: от {min(comps)} до {max(comps)}")
    print("\nЭксперимент завершён успешно!")

if __name__ == "__main__":
    main()