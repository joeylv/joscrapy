Hibernate执行持久化过程中，应用程序无法参与其中。所有的数据持久化操作，对用户都是透明的。

通过事件框架，Hibernate允许应用程能响应特定的内部事件，从而允许实现某些通用的功能或者对Hibernate功能进行扩展。

Hibernate的事件机制框架由两个部分组成：

1、拦截器机制：对于特定动作拦截，回调应用中的特定动作

2、事件系统：重写Hibernate的事件监听器。

一、拦截器

Interceptor接口提供了从会话回调应用程序的机制，这种回调机制可以允许应用程序在持久化对象被保存、更新、删除或是加载之前，检查并（或）修改其属性。

**** 通过Interceptor接口，可以在数据进入数据库之前，对数据进行最后的检查，如果数据不符合要求，可以修改数据，从而避免非法数据进入数据库。

使用拦截器按如下两个步骤进行：

1、定义实现Interceptor接口的拦截器

2、通过Session启用拦截器，或者通过Configuration启用全局拦截器

程序可以通过实现Interceptor接口来创建拦截器，也可以通过继承EmptyInterceptor来实现拦截器。

    
    
     1 public class MyIterceptor extends EmptyInterceptor {
     2     // 记录修改次数
     3     private int updates;
     4     // 记录创建次数
     5     private int creates;
     6 
     7     // 当删除实体时，onDelete方法将被调用
     8     public void onDelete(Object entity, Serializable id, Object[] state,
     9             String[] propertyNames, Type[] types) {
    10         // do nothing
    11     }
    12 
    13     // 当把持久化实体的状态同步到数据库时，onFlushDirty方法被调用
    14     public boolean onFlushDirty(Object entity, Serializable id,
    15             Object[] currentState, Object[] previousState,
    16             String[] propertyNames, Type[] types) {
    17         // 每同步一次，修改的累加器加1
    18         updates++;
    19         for (int i = 0; i < propertyNames.length; i++) {
    20             if ("lastUpdateTimestamp".equals(propertyNames[i])) {
    21                 currentState[i] = new Date();
    22                 return true;
    23             }
    24         }
    25         return false;
    26     }
    27 
    28     // 当加载持久化实体时，onLoad方法被调用
    29     public boolean onLoad(Object entity, Serializable id, Object[] state,
    30             String[] propertyNames, Type[] types) {
    31         for (int i = 0; i < propertyNames.length; i++) {
    32             if ("name".equals(propertyNames[i])) {
    33                 // 输出被装载实体的name属性值
    34                 System.out.println(state[i]);
    35                 return true;
    36             }
    37         }
    38         return false;
    39     }
    40 
    41     // 保存持久化实例时候，调用该方法
    42     public boolean onSave(Object entity, Serializable id, Object[] state,
    43             String[] propertyNames, Type[] types) {
    44         creates++;
    45         for (int i = 0; i < propertyNames.length; i++) {
    46             if ("createTimestamp".equals(propertyNames[i])) {
    47                 state[i] = new Date();
    48                 return true;
    49             }
    50         }
    51         return false;
    52     }
    53 
    54     // 持久化所做修改同步完成后，调用postFlush方法
    55     public void postFlush(Iterator entities) {
    56         System.out.println("创建的次数： " + creates + ", 更新的次数： " + updates);
    57     }
    58 
    59     // 在同步持久化所做修改之前，调用preFlush方法
    60     public void preFlush(Iterator entities) {
    61     }
    62 
    63     // 事务提交之前触发该方法
    64     public void beforeTransactionCompletion(Transaction tx) {
    65         System.out.println("事务即将结束");
    66     }
    67 
    68     // 事务提交之后触发该方法
    69     public void afterTransactionCompletion(Transaction tx) {
    70         System.out.println("事务已经结束");
    71     }
    72 }

上面拦截器没有进行实际的操作，只是打印了一些标识代码。

拦截器可以有两种:Session范围内的，和SessionFactory范围内的。

当使用某个重载的SessionFactory.openSession()使用Interceptor作为参数调用打开一个session的时候，就指定了Session范围内的拦截器。

    
    
    1 Session session = sf.openSession( new MyInterceptor() );

SessionFactory范围内的拦截器要通过Configuration中注册，而这必须在创建SessionFactory之前。在这种情况下，给出的拦截器会被这个SessionFactory所打开的所有session使用了

    
    
    1 new Configuration().setInterceptor( new MyInterceptor() );

  
示例：

    
    
    	public void newsTest(){
    		Configuration cfg = new Configuration().configure().setInterceptor(new MyIterceptor());
    		SessionFactory sf = cfg.buildSessionFactory();
    		Session  session = sf.openSession();
    	
    		Transaction tx = session.beginTransaction();
    		
    		//创建一个News对象
    		News news = new News();
    		news.setTitle("搬校区了..");
    		news.setContent("明天我们就要搬校区了，真期待啊....");
    		session.save(news);
    		
    		News news2 = (News) session.load(News.class, 1);
    		news2.setTitle("明天就要搬校区了..");
    		tx.commit();
    		session.close();
    		
    	}
    

  
程序运行结果如下：

![](http://my.csdn.net/uploads/201207/13/1342140263_1884.jpg)

二、事件机制

如果需要响应持久层的某些特殊事件，可以使用Hibernate3的事件框架。该事件系统可以用来替代拦截器，也可以作为拦截器的补充来使用。

Session接口的每个方法都有相对应的事件。比如 LoadEvent，FlushEvent，等等。当某个方法被调用时，Hibernate
Session会生成一个相对应的事件并激活所有配置好的事件监听器。

系统默认监听器实现的处理过程，完成了所有的数据持久化操作，包括插入、修改等操作。如果用户自己定义了自己的监听器，则意味着用户必须完成对象的持久化操作。

监听器是单例模式对象，即所有同类型的事件处理共享同一个监听器实例，因此监听器不应该保存任何状态，即不应该使用成员变量。

使用事件系统按如下步骤：

1、实现自己的事件监听器

2、注册自定义事件监听器，代替系统默认的事件监听器

实现用户的自定义监听器有如下三种方法：

1、实现对应的监听器接口。实现接口必须实现接口内的所有方法，关键是必须事件Hibernate对应的持久化操作，即数据库访问，这意味着程序员完全取代了Hibernate的底层操作。

2、继承事件适配器。可以选择性地实现需要关注的方法，但依然试图取代Hibernate完成数据库的访问。

3、继承系统默认的事件监听器。扩展特定方法。

下面是自定义监听器实例：

    
    
    1 public class MyLoadListener extends DefaultLoadEventListener {
    2     //在LoadEventListener接口仅仅定义了这个方法
    3     public void onLoad(LoadEvent event,LoadEventListener.LoadType loadType) throws HibernateException{
    4         System.out.println("自定义的load事件");
    5         System.out.println(event.getEntityClassName()+"------"+event.getEntityId());
    6         super.onLoad(event, loadType);
    7     }
    8 }
    
    
    1 public class MySaveListener extends DefaultSaveEventListener{
    2     protected Serializable performSaveOrUpdate(SaveOrUpdateEvent event){
    3         System.out.println("自定义的save事件");
    4         System.out.println(event.getObject());
    5         return super.performSaveOrUpdate(event);
    6     }
    7 }

注意：扩展用户自定义监听器时，别忘了在方法中调用父类的对应的方法，否则Hibernate3默认的持久化行为都会失效。

注册用户自定义监听器有两种方法：

1、编程式。通过使用Configuration对象来编程实现注册。

    
    
     1     public void newsListenerTest(){
     2         Configuration conf = new Configuration().configure();
     3         //为load事件设置监听器
     4         conf.setListener("load", "com.hibernate.filter.MyLoadListener");
     5         conf.setListener("save", "com.hibernate.filter.MySaveListener");
     6         SessionFactory  sfg = conf.buildSessionFactory();
     7         Session session = sfg.openSession();
     8         Transaction tx = session.beginTransaction();
     9         
    10         News news = new News();
    11         news.setContent("2222");
    12         news.setTitle("1111");
    13         session.save(news);           //调用save方法，触动save监听器
    14         tx.commit();
    15         
    16         session.load(News.class, 1);   //调用load方法，触动load监听器
    17         session.close();
    18     }

  
2、声明式。在hibernate.cfg.xml配置文件中进行声明。

注册事件监听器使用<listener.../>元素。该元素可以接受两个参数。type:指定该事件监听器所监听的事件类型，class:指定事件监听器的实现类

    
    
    1     <listener class="com.hibernate.listener.MyLoadListener" type="load"/>
    2     <listener class="com.hibernate.listener.MySaveListener" type="save"/>

如果需要为指定事件配置多个事件监听器，则需要使用<event.../>元素。在<event.../>元素里可以使用多个<listener.../>子元素来指定多个事件监听器。

    
    
    1        <event type="save">
    2                <listener class="com.hibernate.listener.MySaveListener"/>
    3                <listener class="com.hibernate.listener.MyLoadListener"/>
    4        </event>

  

