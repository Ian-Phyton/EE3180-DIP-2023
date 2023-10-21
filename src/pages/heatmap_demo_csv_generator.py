import csv
import random
import time

heatmap = [[None for _ in range(10)] for _ in range(10)]
heatmap_csv = [[None, None, None] for _ in range(100)]
heatmap_csv.insert(0, ['level', 'unit', 'temperature'])

unit_letter = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I', 9:'J'}

def hot_temp():
    return random.randint(50, 53)

def fire_temp():
    return random.randint(60, 65)

def room_temp():
    return random.randint(30, 35)

while True:
    # Generate random temperature data for 10x10 building heatmap
    for level in range(10):
        for unit in range(10):
            if level == 5-1 and (unit >= 1 and unit <= 3):
                heatmap[level][unit] = fire_temp()
            elif level == 5-1 and (unit < 1 or unit > 3):
                heatmap[level][unit] = hot_temp()
            else:
                heatmap[level][unit] = room_temp()
    time.sleep(1)
    
    # Generate csv data list
    n = 0
    for level in range(10):
        for unit in range(10):
            n += 1
            heatmap_csv[n][0] = level + 1
            heatmap_csv[n][1] = unit_letter[unit]
            heatmap_csv[n][2] = heatmap[level][unit]

    # Write csv data into csv file
    with open('heatmap_demo_data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(heatmap_csv)
