##Hibernate读书笔记-----hibernate的批量处理

##
## Hibernate完全以面向对象的方式来操作数据库，当程序里以面向对象的方式操作持久化对象，将被自动转换为对数据库的操作。但存在这样一个问题，如果我们想同时更新100000条记录，是不是要逐一加载100000条记录，然后依次调用setter方法。采用这种方法实在是太繁琐了，而且严重影响了数据的访问性能。Hibernate提供的批量处理的方案来解决这个问题。

##
##

##
##一、批量插入

##
##

##
## 如果我们需要插入100000条记录，通过hibernate可能会采用如下的方式处理：

##
##	 1         Session session = HibernateUtil.getSession(); 2         Transaction tx = session.beginTransaction(); 3         for (int i = 0; i < 100000; i++) { 4             User user = new User(); 5             user.setName("userName"+i); 6             user.setAge(i); 7             session.save(session); 8         	} 9         tx.commit();10         session.close();

##
##

##
##

##
## 但是这个程序存在一个问题：当程序运行到某个地方，总是会抛出OutOfMemoryException内存溢出异常。这是因为Hibernate的Session持有一个必选的一级缓存，所有的User实例都会Session级别的缓存区进行缓存的缘故。

##
## 如果你要执行批量处理并且想要达到一个理想的性能，那么使用JDBC的批量（batching）功能是至关重要。将JDBC的批量抓取数量（batchsize）参数设置到一个合适值。	1 <property name="jdbc.batch_size">20</property>

##
##

##
## 可能也会想到关闭二级缓存：	1 hibernate.cache.use_second_level_cache false

##
##

##
##但这个并不是必须的。

##
##解决这个问题的方案就是：定时的将session的缓存数据刷入数据库，同时通过调用clear()来控制一级缓存的大小。如下：	 1 static void addUser() throws Exception{ 2         Session session = HibernateUtil.getSession(); 3         Transaction tx = session.beginTransaction(); 4         //循环1000次，插入1000条记录 5         for(int i = 0;i < 100000;i++){ 6             //创建User对象 7             User user = new User(); 8             user.setName("userName"+i); 9             user.setAge(i);10             11             //在session级别缓存User实例12             session.save(user);13             14             //每当累加器是20的倍数的时候，将session中数据刷入数据库，并且情况session缓存15             if(i%20==0){16                 session.flush();17                 session.clear();18             	}19         	}

##
## 

##
## 二、批量更新

##
##上面介绍的方法同样也适用于批量更新。在进行会返回很多行数据的查询时，你需要使用scroll()方法以便充分利用服务器端游标所带来的好处。	 1 static void updateUser() throws Exception { 2         Session session = HibernateUtil.getSession(); 3         Transaction tx = session.beginTransaction(); 4         //查询出User表中所有的记录 5         ScrollableResults re = session.createQuery("from User").setCacheMode(CacheMode.IGNORE).scroll(ScrollMode.FORWARD_ONLY); 6         int count = 1; 7         while(re.next()){ 8             User user = (User) re.get(0); 9             //当count=20的倍数时，将更新的结果从session中flush到数据库10             user.setName("新用户:"+count);11             if(++count%20==0){12                 session.flush();13                 session.clear();14             	}15         	}16         tx.commit();17         session.close();18     	}

##
##

##
##通过这种方式，虽然可以进行批量更新，但由于它需要先执行数据查询，然后才能执行数据更新，所以执行效率不高。为了避免这种情况，我们可以使用DML风格进行数据的批量更新。

##
##

##
##三、DML风格的批量更新/删除

##
##Hibernate提供通过Hibernate查询语言（HQL）来执行大批量SQL风格的DML语句的方法。

##
##批量update、delete语句的语法格式如下：(UPDATE|DELETE)FROM?EntityName(WHEREwhere_conditions）。

##
##这里需要注意如下几点：

##
##1、在FROM子句中，FROM关键字是可选的。

##
##2、在FROM子句（from-clause）中只能有一个实体名，它可以是别名。如果实体名是别名，那么任何被引用的属性都必须加上此别名的前缀；如果不是别名，那么任何有前缀的属性引用都是非法的。

##
##3、不能在批量HQL语句中使用连接，显式或者隐式的都不行。不过在WHERE子句中可以使用子查询。可以在where子句中使用子查询，子查询本身可以包含join。

##
##4、整个WHERE子句是可选的。

##
##实例：使用Query.executeUpdate()方法执行一个HQLUPDATE语句

##
##	 1 static void updateUser() throws Exception{ 2         Session session = HibernateUtil.getSession(); 3         Transaction tx = session.beginTransaction(); 4          5         //定义批量更新的HQL语句 6         String hql = "update User as user set user.name = :name"; 7         //执行更新 8         session.createQuery(hql).setString("name", "name").executeUpdate(); 9         10         tx.commit();11         session.close();    12     	}

##
##

##
##使用这种批量更新语法时，通常只需要执行一次SQL的update语句，就可以完成所有满足条件记录的更新。但也有可能需要执行多条update语句，这是因为有继承映射等情况。

##
##执行一个HQLDELETE，同样使用Query.executeUpdate()方法:	 1 //使用DML风格的批量删除 2     static void deleteUser() throws Exception{ 3         Session session = HibernateUtil.getSession(); 4         Transaction tx = session.beginTransaction(); 5          6         //定义批量更新的HQL语句 7         String hql = "delete User"; 8          9         //执行删除10         session.createQuery(hql).executeUpdate();11         12         tx.commit();13         session.close();    14     	}

##
##

##
##Query.executeUpdate()方法返回一个整型值，该值是受此操作影响的记录数量。