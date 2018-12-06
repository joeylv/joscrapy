##bernate读书笔记-----条件查询

##
## 条件查询一般是通过以下三个类完成的：

##
## 1、Criteria:代表一次查询

##
## 2、Criterion：代表一个查询条件

##
## 3、Restriction：代表查询条件的工具类

##
## 执行条件查询的步骤如下：

##
## 1、获得Hibernate的Session对象

##
## 2、以Session对象创建Criteria对象

##
##3、使用Restriction的静态方法创建Criterion查询条件

##
## 4、向Criteria查询中添加Criterion查询条件

##
## 5、执行Criterion的list()方法或者uniqueResult()方法返回结果集

##
## 示例：

##
##	 1     public void query(){ 2         Session session = HibernateUtil.getSession(); 3         Transaction tx = session.beginTransaction(); 4         //使用ctiteria进行条件查询 5         List list = session.createCriteria(Person.class) 6                     .add(Restrictions.eq("id", 1)) 7                     .list(); 8         for (Iterator iterator = list.iterator();iterator.hasNext();) { 9             Person person = (Person) iterator.next();10             System.out.println(person.getName());11         	}12     	}

##
##

##
##

##
## Criteria对象本身并不具备任何数据过滤筛选功能，但程序可以通过向Criteria对象中组合多个Criterion（每一个Criterion对象代表了一个数据过滤条件）即可实现数据过滤。

##
## Criteria包含如下两个方法：

##
##setFristResult(intfirstResult):设置查询返回的第一行记录

##
## setMaxResult(intmaxResult):设置查询返回的记录数

##
## 这两个方法用于查询分页

##
## Criteria还包含如下几个常用的方法：

##
## add(Criterioncriterion)：增加查询条件

##
## addOrder(Orderorder)：增加排序规则

##
##	1         List list = session.createCriteria(Person.class)2                     .add(Restrictions.like("name", "李%"))        //增加查询条件3                     .addOrder(Order.desc("name"))                 //结果集排序4                     .setMaxResults(50)                            //返回的记录数最多为50条5                     .list();                                     //返回结果集

##
##

##
##

##
## Criterion接口代表了一个查询条件，该查询条件有Restrictions负责产生。Restrictions是专门用于产生查询条件的工具类，它的方法大部分是静态方法。

##
##

##
##一、关联

##
## 如果需要使用关联实体的属性来增加查询条件，则应该对该属性再次使用createCriteria方法。

##
##	1         List list = session.createCriteria(Person.class)2                     .createAlias("myEvent", "e")3                     .add(Restrictions.like("e.title", "工业大学%"))4                     .list();

##
##

##
##

##
## 第二个createCriteria返回一个新的Criteria实例，该实例引用Person类中的myEvent关联属性。title是MyEvent类中的属性。

##
##接下来，替换形态在某些情况下也是很有用的。	1         List list = session.createCriteria(Person.class)2                     .add(Restrictions.like("name", "李%"))3                     .setFetchMode("myEvent", FetchMode.JOIN)4                     .list();

##
##

##
## createAlias()方法并不创建一个新的Criteria实例，它只是给关联实体起一个别名，让后面的过滤条件可根据该关联实体进行筛选。

##
## 

##
## 二、动态关联

##
## 在默认情况下，条件查询将根据映射文件指定的延迟加载策略来加载关联实体，如果希望在条件查询中改变延迟加载策略，可以通过setFetchMode()方法来控制。setFetchMode()方法接受一个FetchMode参数。

##
## DEFAULT：使用配置文件指定的延迟加载策略处理

##
## JOIN：使用外连接、预初始化所有关联实体

##
## SELECT：启用延迟加载，系统将使用单独的select语句来初始化关联实体。只有当真正访问关联实体的时候，才会执行第二条select语句。

##
## 使用外连接方式抓取Myevent。

##
##

##
## 三、投影、聚合、分组

##
##Hibernate的条件过滤中使用Projection代表投影运算，Projection是一个接口，而Projections作为Projection的工厂，负责生成Projection对象。

##
## 一旦产生了Projection对象之后，就可以通过setProjection(Projectionprojection)方法来进行投影运算了。

##
##	1         List list = session.createCriteria(Person.class)2                     .setProjection(Projections.projectionList()3                     .add( Projections.avg("age"))4                     .add(Projections.groupProperty("name")))5                     .list();

##
##

##
##

##
## 在一个条件查询中没有必要显式的使用"groupby"。某些投影类型就是被定义为分组投影，他们也出现在SQL的groupby子句中。

##
## 如果我们希望对分组后属性进行排序，那就需要为投影运算指定一个别名了，有两种方法可以为投影运算指定别名

##
##1、使用alias()方法	1         List list = session.createCriteria(Person.class)2                .setProjection(Projections.alias(Projections.groupProperty("name"), "name"))3                .addOrder(Order.asc("age"))4                .list();

##
##

##
##2、使用as()方法为自身指定别名

##
##	1         List list = session.createCriteria(Person.class)2                     .setProjection(Projections.groupProperty("name").as("name"))3                     .addOrder(Order.asc("age"))4                     .list();

##
##

##
## 也可以使用Property.forName()来表示投影：	1         List list = session.createCriteria(Person.class)2                .setProjection(Projections.projectionList()3                .add(Property.forName("name")))4                .list();

##
##

##
##

##
## 四、离线查询和子查询

##
## 条件查询的离线查询有DetachedCriteria来代表，DetachedCriteria类允许在一个session范围外创建一个查询，并且可以使用任意Session来执行它。	 1     public void detachedCriteriaTest(){ 2         //定义一个离线查询 3         DetachedCriteria query = DetachedCriteria.forClass(Person.class).setProjection(Property.forName("name")); 4         Session session = HibernateUtil.getSession(); 5         Transaction tx = session.beginTransaction(); 6         //执行离线查询 7         List list = query.getExecutableCriteria(session).list(); 8          9         for (Iterator iterator = list.iterator();iterator.hasNext();) {10             Person person = (Person) iterator.next();11             System.out.println(person.getName());12         	}13     	}

##
##

##
## 另外DetachedCriteria还可以代表子查询，当我们把DetachedCriteria传入Criteria中作为查询条件时，DetachedCriteria就变成了子查询。	 1     public void subQuery(){ 2         //定义一个离线查询 3         DetachedCriteria query = DetachedCriteria.forClass(Person.class).setProjection(Property.forName("name")); 4         Session session = HibernateUtil.getSession(); 5         Transaction tx = session.beginTransaction(); 6         //执行子查询 7         List list = session.createCriteria(Person.class) 8                     .add(Property.forName("name").in(query)) 9                     .list();10         for (Iterator iterator = list.iterator();iterator.hasNext();) {11             Person person = (Person) iterator.next();12             System.out.println(person.getName());13         	}14     	}

##
##