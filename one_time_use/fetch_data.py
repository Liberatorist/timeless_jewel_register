from io import BytesIO
import json
import os
from urllib.request import urlopen
from zipfile import ZipFile



if __name__ == "__main__":
    tree_data = json.loads(urlopen(
        'https://raw.githubusercontent.com/grindinggear/skilltree-export/master/data.json').read().decode('utf-8'))
    with open("data/tree_data.json", "w") as file:
        json.dump(tree_data, file)

    url = urlopen("https://raw.githubusercontent.com/Liberatorist/TimelessEmulator/master/TimelessEmulator/Build/Output/TimelessJewels/TimelessJewels.zip")
    if not os.path.exists("data/TimelessJewels"):
        os.mkdir("data/TimelessJewels")
    with ZipFile(BytesIO(url.read())) as my_zip_file:
        for contained_file in my_zip_file.namelist():
            with open(f"data/TimelessJewels/{contained_file}", "wb") as f:
                f.write(my_zip_file.read(contained_file))
