filepath = "creatures_image_urls.json"
new_file =  "creatures_image_urls1.json"
with open(filepath, "r", encoding="utf-8") as f:
    data = f.read().strip()
    arr = data.split()
    arr_1 = ""
    for i in range(len(arr)):
        if arr[i] == "\"Sunmane":
            arr_1 = arr[i:len(arr): 1]
            finished = "".join(arr_1)
            with open(new_file, "w") as new:
                new.write(finished)
                exit()
