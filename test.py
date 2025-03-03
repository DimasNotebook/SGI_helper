import json
pack = {
  "name": "A lot of items",
  "version": "2.0",
  "author": "Dima's Notebook",
  "items": [
    {"id": "0", "texture": "custom", "name": "Thing", "maxstack": 1}
  ]
}
a = pack["items"][0]
for i in range(1, 100):
    a.update({"id": str(i)})
    pack["items"].append(a.copy())
file = open("pack.json", 'w')
file.write(json.dumps(pack, indent=4))