json 模块提供了一种很简单的方式来编码和解码JSON数据。 其中两个主要的函数是 json.dumps() 和 json.loads() ，
要比其他序列化函数库如pickle的接口少得多。 下面演示如何将一个Python数据结构转换为JSON：

    
    
    import json
    
    data = {
        "name" : "ACME",
        "shares" : 100,
        "price" : 542.23
    }
    
    json_str = json.dumps(data)

下面演示如何将一个JSON编码的字符串转换回一个Python数据结构：

    
    
    data = json.loads(json_str)

如果你要处理的是文件而不是字符串，你可以使用 json.dump() 和 json.load() 来编码和解码JSON数据。例如：

    
    
    # Writing JSON data
    with open("data.json", "w") as f:
        json.dump(data, f)
    
    # Reading data back
    with open("data.json", "r") as f:
        data = json.load(f)

