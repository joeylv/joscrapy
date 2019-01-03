今天做项目的时候，有两个实体：款式、品牌两者关系是多对多的关联关系，实现的功能是：通过选择款式，显示出该款式的所有品牌。HQL语句如下：

    
    
    1 from Brand as b where b.styles.styleId=?

运行时出现这个异常错误：org.hibernate.QueryException: illegal attempt to dereference
collection 。

通过查资料发现，在上面的HQL语句中，Brand的关联实体styles是一个Set集合，而不是一个Style实体。在
Hibernate3.2.2以前的版本，Hibernate会对关联实体自动使用隐式的inner join，也就是说使用上面的HQL语句是毫无问题的。

但是在Hibernate3.2.2版本以后，Hibernate改变了这种策略。它使用如下策略来关联实体。

同样对于上面的HQL语句。如果styles是一个单个的关联实体或者是一个普通的属性，那么hibernate就会自动使用隐式的inner
join。但是如果styles 是一个集合，那么对不起，统将会出现 org.hibernate.QueryException: illegal
attempt to dereference collection异常。  
对于解决方案就是，要么你退回hibernate3.2.2版本以前，要么使用如下形式的HQL语句：

    
    
    1 from Brand as b inner join fetch b.styles as s where s.styleId=?

