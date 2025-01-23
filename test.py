import json
js = '{"test": "test", "test 2": "test two", "test list": {"intest": "yay", "intest 2": 123}, "testa": ["a", "b"]}'
out = json.loads(js)
#print(out)
print(js)


f = open(r'test.json', 'r')
r = f.read()
print(r)
print(js == r)
out = json.loads(r)
f.close()
print(out)
print(out[1]["test"])
test = 0
test2 = 'test'
test3 = ['a', 'b']
print(str(test2))

json1 = '{[{"test": '+str(test)+', "test2": "'+str(test2)+'", "test3": '+str(test3)+'}, {"test": 1}]}'
print(json1)

#f = open('test.json', 'w')
#f.write(str(json1).replace("'", '"'))
#f.close()