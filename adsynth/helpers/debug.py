import json


def log(key, value):
    print(f"======================")
    print(f"{key} - {value}")
    print(f"======================\n")

def logs(keys, values):
    print(f"======================")
    
    for i in range(len(keys)):
        print(f"{keys[i]} - {values[i]}")
        
    print(f"======================\n")

def export_array(array):
    with open('output.txt', 'w') as file:
        # Write each element of the array to the file
        for element in array:
            file.write(str(element) + '\n')

def export_json(dictionary):
    with open('output.json', "w") as json_file:
        json.dump(dictionary, json_file)