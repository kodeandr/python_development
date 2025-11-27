from collections import defaultdict

# Reading data from a file
data = []
with open(r'C:\Users\Денис\Documents\Python\Algorithms and data structures\DZ1\input.txt', 'r') as file:
    next(file)
    for line in file:
        parts = line.strip().split(';')
        data.append({
            'Country': parts[0],
            'Region': parts[1],
            'Population': int(parts[2]),
            'Area': float(parts[3]),
            'GDP': float(parts[4]),
            'Literacy': float(parts[5])
            })
        

# Counting the number of countries with literacy >= 90%     
region_stats = defaultdict(lambda: {'total_count': 0, 'high_literacy_count': 0})
for country_data in data:
    region = country_data['Region']
    literacy = country_data['Literacy']

    region_stats[region]['total_count'] += 1
    if literacy >= 90:
        region_stats[region]['high_literacy_count'] += 1

# Counting the ratio
max_ratio = 0
best_regions = set()

for region, stats in region_stats.items():
    total_count = stats['total_count']
    high_literacy_count = stats['high_literacy_count']
    ratio = high_literacy_count / total_count if total_count != 0 else 0

    if ratio > max_ratio:
        max_ratio = ratio
        best_regions.clear()
        best_regions.add(region)
    elif ratio == max_ratio:
        best_regions.add(region)

with open('output.txt', 'w') as out_file:
    for region in sorted(best_regions):
        out_file.write(f'{region}\n')