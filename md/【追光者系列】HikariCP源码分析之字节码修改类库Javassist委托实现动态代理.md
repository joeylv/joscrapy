  * 1 概述
  * 2 源码纲要
  * 3 JavassistProxyFactory
    * 3.1 javassist
    * 3.2 源码解析
  * 4 ProxyResultSet
  * 5 ProxyStatement
  * 6 ProxyConnection
  * 7 参考资料

> 摘自【工匠小猪猪的技术世界】  
>  1.这是一个系列，有兴趣的朋友可以持续关注  
>  2.如果你有HikariCP使用上的问题，可以给我留言，我们一起沟通讨论  
>  3.希望大家可以提供我一些案例，我也希望可以支持你们做一些调优

![WechatIMG12424](http://cmsblogs.qiniudn.com/WechatIMG12424.jpeg)

* * *

# 概述

很多人都会问HikariCP为什么那么快？之前的两篇文章[【追光者系列】HikariCP源码分析之FastList](http://mp.weixin.qq.com/s?__biz=MzUzNTY4NTYxMA==&mid=2247483807&idx=1&sn=e2987a302680f2b41950e3b32d7c0679&chksm=fa80f11acdf7780c467985fed0c6261c07cc3610205e2ce7f0739ad7755b4422516ada8caf3b&scene=21#wechat_redirect)
和
[【追光者系列】HikariCP源码分析之ConcurrentBag](http://mp.weixin.qq.com/s?__biz=MzUzNTY4NTYxMA==&mid=2247483799&idx=1&sn=73794ef10f6c1b529d50657a2f975598&chksm=fa80f112cdf77804a4aa3418c89400f90a32954873aa0701ebb784cc2d082be16d80ce539f1b&scene=21#wechat_redirect)
是第一第二弹，本文就是第三弹。

在Down-the-Rabbit-Hole中，作者提到了We’re in your bytecodez的字节码优化

> In order to make HikariCP as fast as it is, we went down to bytecode-level
engineering, and beyond. We pulled out every trick we know to help the JIT
help you. We studied the bytecode output of the compiler, and even the
assembly output of the JIT to limit key routines to less than the JIT inline-
threshold. We flattened inheritance hierarchies, shadowed member variables,
eliminated casts.

字节码优化这块作者还提到了 this change removed a static field access, a push and pop from
the stack, and made the invocation easier for the JIT to optimize because the
callsite is guaranteed not to change.感兴趣的可以看一下
https://github.com/brettwooldridge/HikariCP/wiki/Down-the-Rabbit-Hole。

作者提升性能的秘方是：大量的性能收益来自于代理的优化，如包装Connection，Statement等。那么本文就来带读者揭开这神秘的面纱。

# 源码纲要

hikariCP主要对java.sql.*提供了五个代理类

  * **ProxyConnection** (proxy class for java.sql.Connection) 
  * **ProxyStatement** (proxy class for java.sql.Statement)

  * **ProxyPreparedStatement** (proxy class for java.sql.PreparedStatement)

  * **ProxyCallableStatement** (proxy class for java.sql.CallableStatement)

  * **ProxyResultSet** (proxy class for java.sql.ResultSet)

紧密结合以上五个代理类的还有两个类 **ProxyFactory** (A factory class that produces proxies
around instances of the standard JDBC interfaces)和 **JavassistProxyFactory**
(This class generates the proxy objects for {@link Connection}, {@link
Statement},{@link PreparedStatement}, and {@link
CallableStatement}.Additionally it injects method bodies into the {@link
ProxyFactory} class methods that can instantiate instances of the generated
proxies.)。

我们看一下ProxyFactory这个工厂类，大家是不是可以看到对上面的五个代理类提供的方法只有一行直接抛异常IllegalStateException的代码，并且提示你
**You need to run the CLI build and you need target/classes in your classpath
to run** 。

注释写着“Body is replaced (injected) by
JavassistProxyFactory”，其实方法body中的代码是在编译时调用JavassistProxyFactory才生成的。

    
    
    package com.zaxxer.hikari.pool;
    import java.sql.CallableStatement;
    import java.sql.Connection;
    import java.sql.PreparedStatement;
    import java.sql.ResultSet;
    import java.sql.Statement;
    import com.zaxxer.hikari.util.FastList;
    /**
     * A factory class that produces proxies around instances of the standard
     * JDBC interfaces.
     *
     * @author Brett Wooldridge
     */
    @SuppressWarnings("unused")
    public final class ProxyFactory {
       private ProxyFactory() {
          // unconstructable
       }
       /**
        * Create a proxy for the specified {@link Connection} instance.
        * @param poolEntry the PoolEntry holding pool state
        * @param connection the raw database Connection
        * @param openStatements a reusable list to track open Statement instances
        * @param leakTask the ProxyLeakTask for this connection
        * @param now the current timestamp
        * @param isReadOnly the default readOnly state of the connection
        * @param isAutoCommit the default autoCommit state of the connection
        * @return a proxy that wraps the specified {@link Connection}
        */
       static ProxyConnection getProxyConnection(final PoolEntry poolEntry, final Connection connection, final FastList<Statement> openStatements, final ProxyLeakTask leakTask, final long now, final boolean isReadOnly, final boolean isAutoCommit) {
          // Body is replaced (injected) by JavassistProxyFactory
          throw new IllegalStateException("You need to run the CLI build and you need target/classes in your classpath to run.");
       }
       static Statement getProxyStatement(final ProxyConnection connection, final Statement statement) {
          // Body is replaced (injected) by JavassistProxyFactory
          throw new IllegalStateException("You need to run the CLI build and you need target/classes in your classpath to run.");
       }
       static CallableStatement getProxyCallableStatement(final ProxyConnection connection, final CallableStatement statement) {
          // Body is replaced (injected) by JavassistProxyFactory
          throw new IllegalStateException("You need to run the CLI build and you need target/classes in your classpath to run.");
       }
       static PreparedStatement getProxyPreparedStatement(final ProxyConnection connection, final PreparedStatement statement) {
          // Body is replaced (injected) by JavassistProxyFactory
          throw new IllegalStateException("You need to run the CLI build and you need target/classes in your classpath to run.");
       }
       static ResultSet getProxyResultSet(final ProxyConnection connection, final ProxyStatement statement, final ResultSet resultSet) {
          // Body is replaced (injected) by JavassistProxyFactory
          throw new IllegalStateException("You need to run the CLI build and you need target/classes in your classpath to run.");
       }
    }
    

# JavassistProxyFactory

JavassistProxyFactory存在于工具包里com.zaxxer.hikari.util里，之所以使用Javassist生成动态代理，是因为其速度更快，相比于JDK
Proxy生成的字节码更少，精简了很多不必要的字节码。

## javassist

javassist是一个字节码类库，可以用他来动态生成类，动态修改类等等，还有一个比较常见的用途是AOP，比如对一些类统一加权限过滤，加日志监控等等。

Javassist 不仅是一个处理字节码的库，还有一项优点：可以用 Javassist 改变 Java 类的字节码，而无需真正了解关于字节码或者 Java
虚拟机(Java virtual machine JVM)结构的任何内容。比起在单条指令水平上工作的框架，它确实使字节码操作更可具有可行性了。

Javassist 使您可以检查、编辑以及创建 Java 二进制类。检查方面基本上与通过 Reflection API 直接在 Java
中进行的一样，但是当想要修改类而不只是执行它们时，则另一种访问这些信息的方法就很有用了。这是因为 JVM 设计上并没有提供在类装载到 JVM
中后访问原始类数据的任何方法，这项工作需要在 JVM 之外完成。

Javassist 使用 javassist.ClassPool 类跟踪和控制所操作的类。这个类的工作方式与 JVM
类装载器非常相似，但是有一个重要的区别是它不是将装载的、要执行的类作为应用程序的一部分链接，类池使所装载的类可以通过 Javassist API
作为数据使用。可以使用默认的类池，它是从 JVM
搜索路径中装载的，也可以定义一个搜索您自己的路径列表的类池。甚至可以直接从字节数组或者流中装载二进制类，以及从头开始创建新类。

装载到类池中的类由 javassist.CtClass 实例表示。与标准的 Java java.lang.Class 类一样， CtClass
提供了检查类数据（如字段和方法）的方法。不过，这只是 CtClass
的部分内容，它还定义了在类中添加新字段、方法和构造函数、以及改变类、父类和接口的方法。奇怪的是，Javassist
没有提供删除一个类中字段、方法或者构造函数的任何方法。

字段、方法和构造函数分别由 javassist.CtField、javassist.CtMethod 和 javassist.CtConstructor
的实例表示。这些类定义了修改由它们所表示的对象的所有方法的方法，包括方法或者构造函数中的实际字节码内容。

这篇来自阿里的文章做了一个动态代理的性能对比（http://javatar.iteye.com/blog/814426），得出的结论如下：

  1. ASM和JAVAASSIST字节码生成方式不相上下，都很快，是CGLIB的5倍。
  2. CGLIB次之，是JDK自带的两倍。
  3. JDK自带的再次之，因JDK1.6对动态代理做了优化，如果用低版本JDK更慢，要注意的是JDK也是通过字节码生成来实现动态代理的，而不是反射。
  4. JAVAASSIST提供者动态代理接口最慢，比JDK自带的还慢。   
(这也是为什么网上有人说JAVAASSIST比JDK还慢的原因，用JAVAASSIST最好别用它提供的动态代理接口，而可以考虑用它的字节码生成方式)

差异的原因是各方案生成的字节码不一样，像JDK和CGLIB都考虑了很多因素，以及继承或包装了自己的一些类，所以生成的字节码非常大，而我们很多时候用不上这些，而手工生成的字节码非常小，所以速度快。

最终该阿里团队决定使用JAVAASSIST的字节码生成代理方式，虽然ASM稍快，但并没有快一个数量级，而JAVAASSIST的字节码生成方式比ASM方便，JAVAASSIST只需用字符串拼接出Java源码，便可生成相应字节码，而ASM需要手工写字节码。

该测试可能还是有些问题的。其实性能的根本原因还是在于反射。JdkHandler中的 return method.invoke(delegate,
objects); 是影响性能的关键。如果JAVAASSIST Bytecode
Proxy生成的代理类，也是通过JdkHanlder去实现的话，性能就和JDK自身的动态代理没什么区别了。  
javassit采用的是直接调用，而cglib走了methodProxy.invoke()，说白了还是反射调用。如果实施cglib的直接调用，比如使用的Dispatcher或则LazyLoader。最后的生成的字节就是一个直接调用，性能上就可以和javassist持平。

但是综上所述，javassist相比于JDK Proxy生成的字节码更少，精简了很多不必要的字节码。通过优化并精简字节码，提升了hikariCP的性能。

## 源码解析

我们看一下JavassistProxyFactory的源码

    
    
    /**
     * This class generates the proxy objects for {@link Connection}, {@link Statement},
     * {@link PreparedStatement}, and {@link CallableStatement}.  Additionally it injects
     * method bodies into the {@link ProxyFactory} class methods that can instantiate
     * instances of the generated proxies.
     *
     * @author Brett Wooldridge
     */
    public final class JavassistProxyFactory {
       private static ClassPool classPool;
       private static String genDirectory = "";
       public static void main(String... args) {
          classPool = new ClassPool();
          classPool.importPackage("java.sql");
          classPool.appendClassPath(new LoaderClassPath(JavassistProxyFactory.class.getClassLoader()));
          if (args.length > 0) {
             genDirectory = args[0];
          }
          try {
             // Cast is not needed for these
             String methodBody = "{ try { return delegate.method($); } catch (SQLException e) { throw checkException(e); } }";
             generateProxyClass(Connection.class, ProxyConnection.class.getName(), methodBody);
             generateProxyClass(Statement.class, ProxyStatement.class.getName(), methodBody);
             generateProxyClass(ResultSet.class, ProxyResultSet.class.getName(), methodBody);
             // For these we have to cast the delegate
             methodBody = "{ try { return ((cast) delegate).method($); } catch (SQLException e) { throw checkException(e); } }";
             generateProxyClass(PreparedStatement.class, ProxyPreparedStatement.class.getName(), methodBody);
             generateProxyClass(CallableStatement.class, ProxyCallableStatement.class.getName(), methodBody);
             modifyProxyFactory();
          }
          catch (Exception e) {
             throw new RuntimeException(e);
          }
       }
       private static void modifyProxyFactory() throws Exception {
          System.out.println("Generating method bodies for com.zaxxer.hikari.proxy.ProxyFactory");
          String packageName = ProxyConnection.class.getPackage().getName();
          CtClass proxyCt = classPool.getCtClass("com.zaxxer.hikari.pool.ProxyFactory");
          for (CtMethod method : proxyCt.getMethods()) {
             switch (method.getName()) {
             case "getProxyConnection":
                method.setBody("{return new " + packageName + ".HikariProxyConnection($);}");
                break;
             case "getProxyStatement":
                method.setBody("{return new " + packageName + ".HikariProxyStatement($);}");
                break;
             case "getProxyPreparedStatement":
                method.setBody("{return new " + packageName + ".HikariProxyPreparedStatement($);}");
                break;
             case "getProxyCallableStatement":
                method.setBody("{return new " + packageName + ".HikariProxyCallableStatement($);}");
                break;
             case "getProxyResultSet":
                method.setBody("{return new " + packageName + ".HikariProxyResultSet($);}");
                break;
             default:
                // unhandled method
                break;
             }
          }
          proxyCt.writeFile(genDirectory + "target/classes");
       }
       /**
        *  Generate Javassist Proxy Classes
        */
       private static <T> void generateProxyClass(Class<T> primaryInterface, String superClassName, String methodBody) throws Exception {
          String newClassName = superClassName.replaceAll("(.+)\\.(\\w+)", "$1.Hikari$2");
          CtClass superCt = classPool.getCtClass(superClassName);
          CtClass targetCt = classPool.makeClass(newClassName, superCt);
          targetCt.setModifiers(Modifier.FINAL);
          System.out.println("Generating " + newClassName);
          targetCt.setModifiers(Modifier.PUBLIC);
          // Make a set of method signatures we inherit implementation for, so we don"t generate delegates for these
          Set<String> superSigs = new HashSet<>();
          for (CtMethod method : superCt.getMethods()) {
             if ((method.getModifiers() & Modifier.FINAL) == Modifier.FINAL) {
                superSigs.add(method.getName() + method.getSignature());
             }
          }
          Set<String> methods = new HashSet<>();
          Set<Class<?>> interfaces = getAllInterfaces(primaryInterface);
          for (Class<?> intf : interfaces) {
             CtClass intfCt = classPool.getCtClass(intf.getName());
             targetCt.addInterface(intfCt);
             for (CtMethod intfMethod : intfCt.getDeclaredMethods()) {
                final String signature = intfMethod.getName() + intfMethod.getSignature();
                // don"t generate delegates for methods we override
                if (superSigs.contains(signature)) {
                   continue;
                }
                // Ignore already added methods that come from other interfaces
                if (methods.contains(signature)) {
                   continue;
                }
                // Track what methods we"ve added
                methods.add(signature);
                // Clone the method we want to inject into
                CtMethod method = CtNewMethod.copy(intfMethod, targetCt, null);
                String modifiedBody = methodBody;
                // If the super-Proxy has concrete methods (non-abstract), transform the call into a simple super.method() call
                CtMethod superMethod = superCt.getMethod(intfMethod.getName(), intfMethod.getSignature());
                if ((superMethod.getModifiers() & Modifier.ABSTRACT) != Modifier.ABSTRACT && !isDefaultMethod(intf, intfCt, intfMethod)) {
                   modifiedBody = modifiedBody.replace("((cast) ", "");
                   modifiedBody = modifiedBody.replace("delegate", "super");
                   modifiedBody = modifiedBody.replace("super)", "super");
                }
                modifiedBody = modifiedBody.replace("cast", primaryInterface.getName());
                // Generate a method that simply invokes the same method on the delegate
                if (isThrowsSqlException(intfMethod)) {
                   modifiedBody = modifiedBody.replace("method", method.getName());
                }
                else {
                   modifiedBody = "{ return ((cast) delegate).method($); }".replace("method", method.getName()).replace("cast", primaryInterface.getName());
                }
                if (method.getReturnType() == CtClass.voidType) {
                   modifiedBody = modifiedBody.replace("return", "");
                }
                method.setBody(modifiedBody);
                targetCt.addMethod(method);
             }
          }
          targetCt.getClassFile().setMajorVersion(ClassFile.JAVA_8);
          targetCt.writeFile(genDirectory + "target/classes");
       }
       private static boolean isThrowsSqlException(CtMethod method) {
          try {
             for (CtClass clazz : method.getExceptionTypes()) {
                if (clazz.getSimpleName().equals("SQLException")) {
                   return true;
                }
             }
          }
          catch (NotFoundException e) {
             // fall thru
          }
          return false;
       }
       private static boolean isDefaultMethod(Class<?> intf, CtClass intfCt, CtMethod intfMethod) throws Exception {
          List<Class<?>> paramTypes = new ArrayList<>();
          for (CtClass pt : intfMethod.getParameterTypes()) {
             paramTypes.add(toJavaClass(pt));
          }
          return intf.getDeclaredMethod(intfMethod.getName(), paramTypes.toArray(new Class[paramTypes.size()])).toString().contains("default ");
       }
       private static Set<Class<?>> getAllInterfaces(Class<?> clazz)
       {
          Set<Class<?>> interfaces = new HashSet<>();
          for (Class<?> intf : Arrays.asList(clazz.getInterfaces())) {
             if (intf.getInterfaces().length > 0) {
                interfaces.addAll(getAllInterfaces(intf));
             }
             interfaces.add(intf);
          }
          if (clazz.getSuperclass() != null) {
             interfaces.addAll(getAllInterfaces(clazz.getSuperclass()));
          }
          if (clazz.isInterface()) {
             interfaces.add(clazz);
          }
          return interfaces;
       }
       private static Class<?> toJavaClass(CtClass cls) throws Exception
       {
          if (cls.getName().endsWith("[]")) {
             return Array.newInstance(toJavaClass(cls.getName().replace("[]", "")), 0).getClass();
          }
          else {
             return toJavaClass(cls.getName());
          }
       }
       private static Class<?> toJavaClass(String cn) throws Exception
       {
          switch (cn) {
          case "int":
             return int.class;
          case "long":
             return long.class;
          case "short":
             return short.class;
          case "byte":
             return byte.class;
          case "float":
             return float.class;
          case "double":
             return double.class;
          case "boolean":
             return boolean.class;
          case "char":
             return char.class;
          case "void":
             return void.class;
          default:
             return Class.forName(cn);
          }
       }
    }
    

generateProxyClass负责生成实际使用的代理类字节码，modifyProxyFactory对应修改工厂类中的代理类获取方法。

    
    
    private static void modifyProxyFactory() throws Exception {
          System.out.println("Generating method bodies for com.zaxxer.hikari.proxy.ProxyFactory");
          String packageName = ProxyConnection.class.getPackage().getName();
          CtClass proxyCt = classPool.getCtClass("com.zaxxer.hikari.pool.ProxyFactory");
          for (CtMethod method : proxyCt.getMethods()) {
             switch (method.getName()) {
             case "getProxyConnection":
                method.setBody("{return new " + packageName + ".HikariProxyConnection($);}");
                break;
             case "getProxyStatement":
                method.setBody("{return new " + packageName + ".HikariProxyStatement($);}");
                break;
             case "getProxyPreparedStatement":
                method.setBody("{return new " + packageName + ".HikariProxyPreparedStatement($);}");
                break;
             case "getProxyCallableStatement":
                method.setBody("{return new " + packageName + ".HikariProxyCallableStatement($);}");
                break;
             case "getProxyResultSet":
                method.setBody("{return new " + packageName + ".HikariProxyResultSet($);}");
                break;
             default:
                // unhandled method
                break;
             }
          }
          proxyCt.writeFile(genDirectory + "target/classes");
       }
    

generateProxyClass核心代码如下：

    
    
      /**
        *  Generate Javassist Proxy Classes
        */
       private static <T> void generateProxyClass(Class<T> primaryInterface, String superClassName, String methodBody) throws Exception
       {
          String newClassName = superClassName.replaceAll("(.+)\\.(\\w+)", "$1.Hikari$2");
          CtClass superCt = classPool.getCtClass(superClassName);
          CtClass targetCt = classPool.makeClass(newClassName, superCt);
          targetCt.setModifiers(Modifier.FINAL);
          System.out.println("Generating " + newClassName);
          targetCt.setModifiers(Modifier.PUBLIC);
          // Make a set of method signatures we inherit implementation for, so we don"t generate delegates for these
          Set<String> superSigs = new HashSet<>();
          for (CtMethod method : superCt.getMethods()) {
             if ((method.getModifiers() & Modifier.FINAL) == Modifier.FINAL) {
                superSigs.add(method.getName() + method.getSignature());
             }
          }
          Set<String> methods = new HashSet<>();
          Set<Class<?>> interfaces = getAllInterfaces(primaryInterface);
          for (Class<?> intf : interfaces) {
             CtClass intfCt = classPool.getCtClass(intf.getName());
             targetCt.addInterface(intfCt);
             for (CtMethod intfMethod : intfCt.getDeclaredMethods()) {
                final String signature = intfMethod.getName() + intfMethod.getSignature();
                // don"t generate delegates for methods we override
                if (superSigs.contains(signature)) {
                   continue;
                }
                // Ignore already added methods that come from other interfaces
                if (methods.contains(signature)) {
                   continue;
                }
                // Track what methods we"ve added
                methods.add(signature);
                // Clone the method we want to inject into
                CtMethod method = CtNewMethod.copy(intfMethod, targetCt, null);
                String modifiedBody = methodBody;
                // If the super-Proxy has concrete methods (non-abstract), transform the call into a simple super.method() call
                CtMethod superMethod = superCt.getMethod(intfMethod.getName(), intfMethod.getSignature());
                if ((superMethod.getModifiers() & Modifier.ABSTRACT) != Modifier.ABSTRACT && !isDefaultMethod(intf, intfCt, intfMethod)) {
                   modifiedBody = modifiedBody.replace("((cast) ", "");
                   modifiedBody = modifiedBody.replace("delegate", "super");
                   modifiedBody = modifiedBody.replace("super)", "super");
                }
                modifiedBody = modifiedBody.replace("cast", primaryInterface.getName());
                // Generate a method that simply invokes the same method on the delegate
                if (isThrowsSqlException(intfMethod)) {
                   modifiedBody = modifiedBody.replace("method", method.getName());
                }
                else {
                   modifiedBody = "{ return ((cast) delegate).method($); }".replace("method", method.getName()).replace("cast", primaryInterface.getName());
                }
                if (method.getReturnType() == CtClass.voidType) {
                   modifiedBody = modifiedBody.replace("return", "");
                }
                method.setBody(modifiedBody);
                targetCt.addMethod(method);
             }
          }
          targetCt.getClassFile().setMajorVersion(ClassFile.JAVA_8);
          targetCt.writeFile(genDirectory + "target/classes");
       }
    

以 generateProxyClass(ResultSet.class, ProxyResultSet.class.getName(),
methodBody); 来看

我看的是3.1.1-SNAPSHOT版本的源码，这段代码可以看到采用java8并放到了target/classes目录下。

通过继承ProxyResultSet来生成HikariProxyResultSet，methodBody中的method替换成对应方法的方法名。

这里展示一下生成的HikariProxyResultSet的部分代码：

    
    
    public class HikariProxyResultSet extends ProxyResultSet implements ResultSet, AutoCloseable, Wrapper {
        public boolean next() throws SQLException {
            try {
                return super.delegate.next();
            } catch (SQLException var2) {
                throw this.checkException(var2);
            }
        }
        public void close() throws SQLException {
            try {
                super.delegate.close();
            } catch (SQLException var2) {
                throw this.checkException(var2);
            }
        }
        public boolean wasNull() throws SQLException {
            try {
                return super.delegate.wasNull();
            } catch (SQLException var2) {
                throw this.checkException(var2);
            }
        }
        public String getString(int var1) throws SQLException {
            try {
                return super.delegate.getString(var1);
            } catch (SQLException var3) {
                throw this.checkException(var3);
            }
        }
    

# ProxyResultSet

该代理类主要为updateRow、insertRow、deleteRow增加了执行记录connection.markCommitStateDirty()

源码如下：

    
    
    /**
     * This is the proxy class for java.sql.ResultSet.
     *
     * @author Brett Wooldridge
     */
    public abstract class ProxyResultSet implements ResultSet {
       protected final ProxyConnection connection;
       protected final ProxyStatement statement;
       final ResultSet delegate;
       protected ProxyResultSet(ProxyConnection connection, ProxyStatement statement, ResultSet resultSet) {
          this.connection = connection;
          this.statement = statement;
          this.delegate = resultSet;
       }
       @SuppressWarnings("unused")
       final SQLException checkException(SQLException e) {
          return connection.checkException(e);
       }
       /** {@inheritDoc} */
       @Override
       public String toString() {
          return this.getClass().getSimpleName() + "@" + System.identityHashCode(this) + " wrapping " + delegate;
       }
       // **********************************************************************
       //                 Overridden java.sql.ResultSet Methods
       // **********************************************************************
       /** {@inheritDoc} */
       @Override
       public final Statement getStatement() throws SQLException {
          return statement;
       }
       /** {@inheritDoc} */
       @Override
       public void updateRow() throws SQLException {
          connection.markCommitStateDirty();
          delegate.updateRow();
       }
       /** {@inheritDoc} */
       @Override
       public void insertRow() throws SQLException {
          connection.markCommitStateDirty();
          delegate.insertRow();
       }
       /** {@inheritDoc} */
       @Override
       public void deleteRow() throws SQLException {
          connection.markCommitStateDirty();
          delegate.deleteRow();
       }
       /** {@inheritDoc} */
       @Override
       @SuppressWarnings("unchecked")
       public final <T> T unwrap(Class<T> iface) throws SQLException {
          if (iface.isInstance(delegate)) {
             return (T) delegate;
          }
          else if (delegate != null) {
              return delegate.unwrap(iface);
          }
          throw new SQLException("Wrapped ResultSet is not an instance of " + iface);
       }
    }
    

# ProxyStatement

该类主要implements了java.sql.Statement并实现了其方法。

执行过程中除了返回ResultSet的需要返回ProxyFactory.getProxyResultSet(connection, this,
resultSet);

    
    
    static ResultSet getProxyResultSet(final ProxyConnection connection, final ProxyStatement statement, final ResultSet resultSet) {
          // Body is replaced (injected) by JavassistProxyFactory
          throw new IllegalStateException("You need to run the CLI build and you need target/classes in your classpath to run.");
       }
    

就是上文提及的字节码，其他直接返回delegate代理对象。

    
    
    /** {@inheritDoc} */
       @Override
       public boolean execute(String sql) throws SQLException {
          connection.markCommitStateDirty();
          return delegate.execute(sql);
       }
       /** {@inheritDoc} */
       @Override
       public boolean execute(String sql, int autoGeneratedKeys) throws SQLException {
          connection.markCommitStateDirty();
          return delegate.execute(sql, autoGeneratedKeys);
       }
       /** {@inheritDoc} */
       @Override
       public ResultSet executeQuery(String sql) throws SQLException {
          connection.markCommitStateDirty();
          ResultSet resultSet = delegate.executeQuery(sql);
          return ProxyFactory.getProxyResultSet(connection, this, resultSet);
       }
    

关于其close方法得提一下上一节的
[【追光者系列】HikariCP源码分析之FastList](http://mp.weixin.qq.com/s?__biz=MzUzNTY4NTYxMA==&mid=2247483807&idx=1&sn=e2987a302680f2b41950e3b32d7c0679&chksm=fa80f11acdf7780c467985fed0c6261c07cc3610205e2ce7f0739ad7755b4422516ada8caf3b&scene=21#wechat_redirect)

    
    
    // **********************************************************************
       //                 Overridden java.sql.Statement Methods
       // **********************************************************************
       /** {@inheritDoc} */
       @Override
       public final void close() throws SQLException
       {
       // 放置重复关闭
     synchronized (this) {
     if (isClosed) {
     return;
     }
     isClosed = true;
     }
     // 移出缓存
     connection.untrackStatement(delegate);
     try {
     // 关闭代理
     delegate.close();
     }
     catch (SQLException e) {
     throw connection.checkException(e);
     }
       }
    

connection.untrackStatement(delegate); 这里我们可以看到源码如下

    
    
    final synchronized void untrackStatement(final Statement statement) {
          openStatements.remove(statement);
       }
       private final FastList<Statement> openStatements;
         protected ProxyConnection(final PoolEntry poolEntry, final Connection connection, final FastList<Statement> openStatements, final ProxyLeakTask leakTask, final long now, final boolean isReadOnly, final boolean isAutoCommit) {
          this.poolEntry = poolEntry;
          this.delegate = connection;
          this.openStatements = openStatements;
          this.leakTask = leakTask;
          this.lastAccess = now;
          this.isReadOnly = isReadOnly;
          this.isAutoCommit = isAutoCommit;
       }
    

FastList是一个List接口的精简实现，只实现了接口中必要的几个方法。JDK
ArrayList每次调用get()方法时都会进行rangeCheck检查索引是否越界，FastList的实现中去除了这一检查，只要保证索引合法那么rangeCheck就成为了不必要的计算开销(当然开销极小)。此外，HikariCP使用List来保存打开的Statement，当Statement关闭或Connection关闭时需要将对应的Statement从List中移除。通常情况下，同一个Connection创建了多个Statement时，后打开的Statement会先关闭。ArrayList的remove(Object)方法是从头开始遍历数组，而FastList是从数组的尾部开始遍历，因此更为高效。

简而言之就是 **自定义数组类型（FastList）代替ArrayList：避免每次get()调用都要进行range
check，避免调用remove()时的从头到尾的扫描**

#  ProxyConnection

该类主要实现了java.sql.Connection的一系列方法，凡涉及Statement、CallableStatement、PreparedStatement的方法都用到了先缓存statement，然后通过ProxyFactory工厂生成的字节码代理类

    
    
     /** {@inheritDoc} */
       @Override
       public CallableStatement prepareCall(String sql, int resultSetType, int concurrency, int holdability) throws SQLException {
          return ProxyFactory.getProxyCallableStatement(this, trackStatement(delegate.prepareCall(sql, resultSetType, concurrency, holdability)));
       }
       /** {@inheritDoc} */
       @Override
       public PreparedStatement prepareStatement(String sql) throws SQLException {
          return ProxyFactory.getProxyPreparedStatement(this, trackStatement(delegate.prepareStatement(sql)));
       }
    

其关闭代码需要注意一点的是，因为closeStatements里会evict poolEntry，所以放到判断外。

    
    
    // **********************************************************************
       //              "Overridden" java.sql.Connection Methods
       // **********************************************************************
       /** {@inheritDoc} */
       @Override
       public final void close() throws SQLException {
          // Closing statements can cause connection eviction, so this must run before the conditional below
          closeStatements();
          if (delegate != ClosedConnection.CLOSED_CONNECTION) {
             leakTask.cancel();
             try {
                if (isCommitStateDirty && !isAutoCommit) {
                   delegate.rollback();
                   lastAccess = currentTime();
                   LOGGER.debug("{} - Executed rollback on connection {} due to dirty commit state on close().", poolEntry.getPoolName(), delegate);
                }
                if (dirtyBits != 0) {
                   poolEntry.resetConnectionState(this, dirtyBits);
                   lastAccess = currentTime();
                }
                delegate.clearWarnings();
             }
             catch (SQLException e) {
                // when connections are aborted, exceptions are often thrown that should not reach the application
                if (!poolEntry.isMarkedEvicted()) {
                   throw checkException(e);
                }
             }
             finally {
                delegate = ClosedConnection.CLOSED_CONNECTION;
                poolEntry.recycle(lastAccess);
             }
          }
       }
    

ProxyConnection如下图，可以看到该类是真正使用FastList来进行优化的 private final FastList
openStatements;

![201805041001](http://cmsblogs.qiniudn.com/201805041001.jpg)

    
    
    // 用于标识连接被访问或存在可提交数据
    final void markCommitStateDirty() {
       if (isAutoCommit) {
          lastAccess = currentTime();
       }
       else {
          isCommitStateDirty = true;
       }
    }
    // 缓存statement
    private synchronized <T extends Statement> T trackStatement(final T statement) {
       openStatements.add(statement);
       return statement;
    }
    // 移出statement缓存
    final synchronized void untrackStatement(final Statement statement) {
       openStatements.remove(statement);
    }
    // 关闭全部已打开的statement（只在close方法中调用）
    @SuppressWarnings("EmptyTryBlock")
    private synchronized void closeStatements() {
       final int size = openStatements.size();
       if (size > 0) {
          for (int i = 0; i < size && delegate != ClosedConnection.CLOSED_CONNECTION; i++) {
             try (Statement ignored = openStatements.get(i)) {
                // automatic resource cleanup
             }
             catch (SQLException e) {
                LOGGER.warn("{} - Connection {} marked as broken because of an exception closing open statements during Connection.close()",
                            poolEntry.getPoolName(), delegate);
                leakTask.cancel();
                poolEntry.evict("(exception closing Statements during Connection.close())");
                delegate = ClosedConnection.CLOSED_CONNECTION;
             }
          }
          openStatements.clear();
       }
    }
    

In order to generate proxies for Connection, Statement, and ResultSet
instances HikariCP was initially using a singleton factory, held in the case
of ConnectionProxy in a static field (PROXY_FACTORY).

ClosedConnection是ProxyConnection中动态代理实现的唯一实例化对象。全局唯一变量，作为已关闭连接的代理引用，为连接关闭后外界代理连接的引用调用提供处理，同时唯一类减少了内存消耗和比对代价。

    
    
    // **********************************************************************
       //                         Private classes
       // **********************************************************************
       private static final class ClosedConnection
       {
          static final Connection CLOSED_CONNECTION = getClosedConnection();
          private static Connection getClosedConnection()
          {
             InvocationHandler handler = (proxy, method, args) -> {
              // 只保留3个方法的快速返回，其他均抛出异常
                final String methodName = method.getName();
                if ("abort".equals(methodName)) {
                   return Void.TYPE;
                }
                else if ("isValid".equals(methodName)) {
                   return Boolean.FALSE;
                }
                else if ("toString".equals(methodName)) {
                   return ClosedConnection.class.getCanonicalName();
                }
                throw new SQLException("Connection is closed");
             };
             return (Connection) Proxy.newProxyInstance(Connection.class.getClassLoader(), new Class[] { Connection.class }, handler);
          }
       }
    

这里InvocationHandler还是使用到了反射，之前提过的，多多少少对性能也会有点损失，一次全局唯一变量一次反射，个人认为，这里反射如果能优化为直接调用字节码，或许性能还能再上一个台阶。

# 参考资料

  * <http://yonglin4605.iteye.com/blog/1396494>
  * <http://www.csg.ci.i.u-tokyo.ac.jp/~chiba/javassist/>
  * <http://zhxing.iteye.com/blog/1703305>
  * <http://www.cnblogs.com/taisenki/p/7716724.html>

