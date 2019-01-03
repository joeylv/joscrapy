在SQL/92标准可以使用USING子句对连接条件进行简化，但是只有在查询满足以下两个条件时才能给使用USING进行简化：

1、查询必须是等连接的

2、等连接中的列必须是同名

如：商品表goods表和商品类型表category表中goods的外键和category的主键相同：categoryid而且是等连接，这里可以使用using

    
    
    1       select goodsname,categoryname
    2       from goods inner join category
    3       using(categoryid)

在使用using是需要注意以下几个问题

1、在select子句中只能指定该列名，不能使用表名或别名

2、在using子句中也只能单独使用列名

对于多与两个表的连接，先看这个例子

    
    
    1      select c.firstName,c.lastName,p.product_name ,pt.product_types_name 
    2      from customers c,purchase pr,products p,product_types pt
    3      where c.customer_id=pr.customer_id
    4      and p.products_id = pr.products_id
    5      and p.product_types_id=pt.product_types_id;

使用using对上面的sql语句进行重写

    
    
    1      select c.first_name,c.last_name,p.products_name as product,pt.product_types_name as typesname
    2      from customers c inner join purchases pr
    3      using(customers_id)
    4      inner join products p
    5      using(products_id)
    6      inner join product_types pt
    7      using(product_types_id);

  
  

