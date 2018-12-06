##Hibernate读书笔记-----缓存

##
##

##
## 缓存的作用主要是用来提高hibernate的性能，可以简单的理解成一个map。使用缓存涉及到三个操作：把数据放入缓存、从缓存中取数据、删除缓存中的无效数据。

##
##

##
##一、一级缓存

##
##一级缓存是Session级共享的。对于一级缓存而言，所有经过Session操作的实体，不管是使用save()、upadate()或者saveOrUpdate保存一个对象，还是使用load()、get()、list()、iterate()、scroll()方法获得一个对象时，该对象都将被放入一级缓存中。

##
##	1             session = HibernateUtil.getSession();2             Users users = (Users) session.get(Users.class, id);3             System.out.println(users.getBirthday());4             Users users2 = (Users) session.get(Users.class, id);5             System.out.println(users.getName());

##
##

##
##

##
##该程序当第一次查询Users对象时，hibernate会先到一级缓存中查找缓存中是否有该实体，如果有，就直接拿，否则就到数据库中去读取。这里缓存中没有，所以hibernate会到数据库中去读取数据。这里产生一条SQL语句。同时hibernate会将该实体对象放入到一级缓存中去。当第二次还查询该实体对象的时候，hibernate同样会先到一级缓存中去读，结果一级缓存中存在该实体对象，所以直接拿。故上面的程序实例只会产生一条SQL语句。

##
##在Session调用flush()方法或者close()方法之前，这些对象都会一直缓存在一级缓存中。

##
##由于一级缓存不能控制缓存的对象数据，所以在大批量操作数据的时候可能会造成内存溢出。

##
##清除缓存有两个方法：evil()、clear()。其中evil()用于清除一条记录，它接受一个持久化类参数。Clear用于清除session里面所有的记录。

##
##

##
##

##
##二、二级缓存

##
##SessionFactory级别的二级缓存是全局的，应用的所有Session都共享这个二级缓存。但是二级缓存默认是关闭的，必须由程序显示开启

##
##使用二级缓存一般有如下步骤：

##
##1、在hibernate.cfg.xml中开启二级缓存

##
##	1         <property name="cache.use_second_level_cache">true</property>

##
##

##
##

##
##2、设置二级缓存的实现类

##
##实际应用中一般不需要我们自己实现缓存，直接使用第三方提供的缓存即可。	1         <property name="cache.provider_class">org.hibernate.cache.EHCacheProvider</property>

##
##                                              Hibernate 3所支持的缓存实现

##
##3、复制二级缓存的JAR包。

##
##使用第三方提供的缓存就必须将相应的JAR包复制到应用的类加载路径中去。这里我采用的是EHCache。

##
##注意在使用EHCache的时候，要将入下两个JAR包也要加载到项目应用中：commons-loggin、backport-util-concurrent。

##
##4、将缓存实现所需要的配置文件添加到系统的类加载路径中。对于EHCache缓存而言，它需要一个ehcache.xml配置文件。

##
## 配置文件代码如下：	1 <ehcache>2     <defaultCache3         maxElementsInMemory="10000"                4         eternal="false"5         timeToIdleSeconds="120"6         timeToLiveSeconds="120"7         overflowToDisk="true"8         />9 </ehcache>

##
##

##
##5、设置对那些实体类。实体的那些集合属性开启二级缓存。

##
##在这里一般有如下两种方法：

##
## 1）、修改要使用缓存的映射文件。在持久化映射文件的<class.../>元素、或者<set.../>、<list.../>等集合元素内使用<cache.../>元素指定缓存策略

##
##	 1 <hibernate-mapping package="com.hibernate.domain"> 2     <class name="Users"> 3         <cache usage="read-only"/>    <!-- 缓存策略为只读 --> 4         <id name="id"> 5             <generator class="native" /> 6         </id> 7  8         <property name="birthday" /> 9         10         <!-- 映射组件元素 -->11         <component name="name">12             <!-- 映射组件的name属性指向包含实体 -->13             <property name="firstName" column="first_name"/>14             <property name="lastName" column="last_name"/>15         </component>16     </class>17 </hibernate-mapping>

##
##

##
##

##
## 2）、在hibernate.cfg.xml文件中使用<class-cache.../>或者<collection-cache.../>元素对知道那个的持久化类、集合属性启用二级缓存

##
##	1 <class-cache usage="read-only" class="com.hibernate.domain.Users"/>

##
##

##
##

##
##6、测试程序	public void query(int id){        Session session = null;        try {            session = HibernateUtil.getSession();            Users users = (Users) session.get(Users.class, id);            System.out.println(users.getBirthday());        	} finally{            if(session!=null)              session.close();        	}                try {            session = HibernateUtil.getSession();            Users users = (Users) session.get(Users.class, id);            System.out.println(users.getName());        	}finally{            if(session!=null)              session.close();        	}    	}

##
##当第一次查询Users实体之后，SessionFactory会将该实体缓存在二级缓存中，在这里先关闭session1然后重新创建session，在一次查询Users实体时，程序就可以直接使用缓存中已经存在的Users实体了。这里只产生一条SQL查询语句。

##
##

##
##2.1、缓存策略

##
##二级缓存存在如下四种缓存策略：read-only、read-write、nonstrict-read-write、transaction。

##
##read-only：只读策略。如果应用程序只需要读取持久化实体的对象，无须对其进行修改，那么就可以对其设置为"只读"缓存策略。这是最简单，也是实用性最好的方法。甚至在集群中，它也能完美地运作。

##
##read-write：读/写策略：如果应用程序需要更新数据，那么使用读/写缓存比较合适。如果应用程序要求“序列化事务”的隔离级别（serializabletransactionisolationlevel），那么就决不能使用这种缓存策略。

##
##nonstrict-read-write：非严格读/写策略。如果应用程序只偶尔需要更新数据（也就是说，两个事务同时更新同一记录的情况很不常见），也不需要十分严格的事务隔离，那么比较适合使用非严格读/写缓存策略。

##
##transaction：事物缓存。Hibernate的事务缓存策略提供了全事务的缓存支持。这样的缓存只能用于JTA环境中，你必须指定为其hibernate.transaction.manager_lookup_class属性。

##
##

##
##没有一种缓存提供商能够支持上列的所有缓存并发策略。下表中列出了各种提供器、及其各自适用的并发策略。

##
##

##
##

##
##2.2、管理缓存

##
##对于二级缓存而言，SessionFactory提供了许多方法用于清除缓存中实例、整个类、集合实例或者整个集合。	1         sessionFactory.evict(Users.class, id); //清除指定id的Users对象2 3         sessionFactory.evict(Users.class);                         // 清除所有的Users对象4 5         sessionFactory.evictCollection("Users.name",id); //清除指定id的Users所关联集合属性6 7         sessionFactory.evictCollection("Users.name"); //清除所有Users所关联集合属性

##
##

##
##SessionFactory还提供了一个getCache()方法，该方法返回一个Cache对象，通过该对象即可操作二级缓存中的实体、集合等。

##
##

##
##CacheMode参数用于控制具体的Session如何与二级缓存进行交互。

##
##CacheMode.NORMAL-从二级缓存中读、写数据。

##
##CacheMode.GET-从二级缓存中读取数据，仅在数据更新时对二级缓存写数据。

##
##CacheMode.PUT-仅向二级缓存写数据，但不从二级缓存中读数据。

##
##CacheMode.REFRESH-仅向二级缓存写数据，但不从二级缓存中读数据。通过hibernate.cache.use_minimal_puts的设置，强制二级缓存从数据库中读取数据，刷新缓存内容。

##
##

##
##如果需要查看二级缓存或查询缓存区域的内容，可以使用Hibernate的统计（Statistics）API。

##
##为了开启二级缓存的统计功能，需要在hibernate.cfg.xml文件中进行配置。

##
##	1         <property name="generate_statistics">true</property>2         <property name="cache.use_structured_entries">true</property>

##
##

##
##

##
##可以通过如下方式查看二级缓存的内容	1         Map cacheEntries = HibernateUtil.getSessionFactory().getStatistics()2                           .getSecondLevelCacheStatistics("com.hibernate.domain.Users").getEntries();3         System.out.println(cacheEntries);

##
##

##
##

##
##

##
##2.3、查询缓存

##
##一级、二级缓存都是对整个实体进行缓存，它不会缓存普通属性，如果想对普通属性进行缓存，则可以使用查询缓存。

##
##使用查询缓存时，不仅需要所使用的HQL语句、SQL语句相同，还要求所传入的参数也相同。

##
##要使用查询缓存就需要在hibernate.cfg.xml中开启查询缓存：

##
##	1         <property name="cache.use_query_cache">true</property>

##
##

##
##

##
##该设置将会创建两个缓存区域-一个用于保存查询结果集；另一个则用于保存最近查询的一系列表的时间戳。

##
##如若需要进行缓存，请调用Query.setCacheable(true)方法，该方法用于开启查询缓存。这个调用会让查询在执行过程中时先从缓存中查找结果，并将自己的结果集放到缓存中去。

##
##如果你要对查询缓存的失效政策进行精确的控制，你必须调用Query.setCacheRegion()方法，为每个查询指定其命名的缓存区域。	1     public void cacheQuery(){2         Session  session = HibernateUtil.getSession();3         List list = session.createQuery("from User u where u.id=:id")4                     .setInteger("id", 2)5                     .setCacheable(true)6                     .setCacheRegion("name")7                     .list();8 9     	}

##
##

##
##