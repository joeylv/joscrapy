  * 1 服务端创建流程
  * 2 服务端源码分析
  * 3 参考资料

> 原文出处<http://cmsblogs.com/> 『chenssy』  
> 转载请注明原创出处，谢谢！

上篇博客([【死磕Netty】—-Netty的核心组件及其设计](http://cmsblogs.com/?p=2467))，了解了 Netty
的核心组件及其设计，但是这些都是零散的，不成体系。那么 Netty 是如何利用这些组件构建成一个高性能的异步通信框架。通过这篇博客可以初步了解。

下面先来一段 Netty 服务端的代码：

    
    
    public class NettyServer {
    
        public void bind(int port){
            // 创建EventLoopGroup
            EventLoopGroup bossGroup = new NioEventLoopGroup();        //创建BOSS线程组 用于服务端接受客户端的连接
            EventLoopGroup workerGroup = new NioEventLoopGroup();      //创建WORK线程组 用于进行SocketChannel的网络读写
    
            try {
                // 创建ServerBootStrap实例
                // ServerBootstrap 用于启动NIO服务端的辅助启动类，目的是降低服务端的开发复杂度
                ServerBootstrap b = new ServerBootstrap();
                // 绑定Reactor线程池
                b.group(bossGroup, workerGroup)
                        // 设置并绑定服务端Channel
                        // 指定所使用的NIO传输的Channel
                        .channel(NioServerSocketChannel.class)
                        .option(ChannelOption.SO_BACKLOG, 1024)
                        .handler(new LoggingServerHandler())
                        .childHandler(new ChannelInitializer(){
    
                            @Override
                            protected void initChannel(Channel ch) throws Exception {
                                //do something
                            }
                        });
    
                // 绑定端口，同步等待成功
                ChannelFuture future = b.bind(port).sync();
                // 等待服务端监听端口关闭
                future.channel().closeFuture().sync();
    
            } catch (InterruptedException e) {
                e.printStackTrace();
            } finally {
                // 优雅地关闭
                bossGroup.shutdownGracefully();
                workerGroup.shutdownGracefully();
            }
        }
    
        private class LoggingServerHandler extends ChannelInboundHandlerAdapter{
            @Override
            public void channelActive(ChannelHandlerContext ctx) throws Exception {
                System.out.println("loggin-channelActive");
            }
    
            @Override
            public void channelRegistered(ChannelHandlerContext ctx) throws Exception {
                System.out.println("loggin-channelRegistered");
            }
    
            @Override
            public void handlerAdded(ChannelHandlerContext ctx) throws Exception {
                System.out.println("loggin-handlerAdded");
            }
        }
    
        public static void main(String[] args){
                new NettyServer().bind(8899);
        }
    }
    

上面代码为 Netty 服务器端的完整代码，在整个服务端代码中会涉及如下几个核心类。

**ServerBootstrap**

ServerBootstrap 为 Netty 服务端的启动辅助类，它提供了一系列的方法用于设置服务端启动相关的参数。

**Channel**

Channel 为 Netty 网络操作抽象类，它定义了一组功能，其提供的 API 大大降低了直接使用 Socket
类的复杂性。当然它也不仅仅只是包括了网络 IO 操作的基本功能，还包括一些与 Netty 框架相关的功能，包括获取该 Channel 的 EventLoop
等等。

**EventLoopGroup**

EventLoopGroup 为 Netty 的 Reactor 线程池，它实际上就是 EventLoop 的容器，而 EventLoop 为 Netty
的核心抽象类，它的主要职责是处理所有注册到本线程多路复用器 Selector 上的 Channel。

**ChannelHandler**

ChannelHandler 作为 Netty 的主要组件，它主要负责 I/O 事件或者 I/O
操作进行拦截和处理，它可以选择性地拦截和处理自己感觉兴趣的事件，也可以透传和终止事件的传递。

**ChannelPipeline**

ChannelPipeline 是 ChannelHandler 链的容器，它负责 ChannelHandler 的管理和事件拦截与调度。每当新建一个
Channel 都会分配一个新的 ChannelPepeline，同时这种关联是永久性的。

> 以上是简要介绍，详细介绍请参考([【死磕Netty】—–Netty的核心组件及其设计](http://cmsblogs.com/?p=2467))

## 服务端创建流程

Netty 服务端创建的时序图，如下（摘自《Netty权威指南（第二版）》）

![Netty
服务端创建的时序图](http://img.blog.csdn.net/20171204211824475?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvY2hlbnNzeQ==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

主要步骤为：

  1. 创建 ServerBootstrap 实例
  2. 设置并绑定 Reactor 线程池
  3. 设置并绑定服务端 Channel
  4. 创建并初始化 ChannelPipeline
  5. 添加并设置 ChannelHandler
  6. 绑定并启动监听端口

## 服务端源码分析

**1、创建两个EventLoopGroup**

    
    
            EventLoopGroup bossGroup = new NioEventLoopGroup();
            EventLoopGroup workerGroup = new NioEventLoopGroup();
    

bossGroup 为 BOSS 线程组，用于服务端接受客户端的连接, workerGroup 为 worker 线程组，用于进行
SocketChannel 的网络读写。当然也可以创建一个并共享。

**2、创建ServerBootstrap实例**

    
    
    ServerBootstrap b = new ServerBootstrap();
    

ServerBootStrap为Netty服务端的启动引导类，用于帮助用户快速配置、启动服务端服务。提供的方法如下：  
  
<table>  
<tr>  
<th>

方法名称

</th>  
<th>

方法描述

</th> </tr>  
<tr>  
<td>

`group`

</td>  
<td>

设置 ServerBootstrap 要用的 EventLoopGroup

</td> </tr>  
<tr>  
<td>

`channel`

</td>  
<td>

设置将要被实例化的 ServerChannel 类

</td> </tr>  
<tr>  
<td>

`option`

</td>  
<td>

实例化的 ServerChannel 的配置项

</td> </tr>  
<tr>  
<td>

`childHandler`

</td>  
<td>

设置并添加 ChannelHandler

</td> </tr>  
<tr>  
<td>

`bind`

</td>  
<td>

绑定 ServerChannel

</td> </tr> </table>

ServerBootStrap底层采用装饰者模式。

关于 ServerBootStrap 我们后续做详细分析。

**3、设置并绑定Reactor线程池**

调用 `group()` 方法，为 ServerBootstrap 实例设置并绑定 Reactor 线程池。

    
    
    b.group(bossGroup, workerGroup)
    

EventLoopGroup 为 Netty 线程池，它实际上就是 EventLoop 的数组容器。EventLoop
的职责是处理所有注册到本线程多路复用器 Selector 上的 Channel，Selector 的轮询操作由绑定的 EventLoop 线程 run
方法驱动，在一个循环体内循环执行。通俗点讲就是一个死循环，不断的检测 I/O 事件、处理 I/O 事件。

这里设置了两个group，这个其实有点儿像我们工作一样。需要两类型的工人，一个老板（bossGroup）,一个工人（workerGroup），老板负责从外面接活，工人则负责死命干活（尼玛，和我上家公司一模一样）。所以这里
bossGroup 的作用就是不断地接收新的连接，接收之后就丢给 workerGroup 来处理，workerGroup 负责干活就行（负责客户端连接的
IO 操作）。

源码如下：

    
    
        public ServerBootstrap group(EventLoopGroup parentGroup, EventLoopGroup childGroup) {
            super.group(parentGroup);        // 绑定boosGroup
            if (childGroup == null) {
                throw new NullPointerException("childGroup");
            }
            if (this.childGroup != null) {
                throw new IllegalStateException("childGroup set already");
            }
            this.childGroup = childGroup;    // 绑定workerGroup
            return this;
        }
    

其中父 EventLoopGroup 传递到父类的构造函数中：

    
    
        public B group(EventLoopGroup group) {
            if (group == null) {
                throw new NullPointerException("group");
            }
            if (this.group != null) {
                throw new IllegalStateException("group set already");
            }
            this.group = group;
            return (B) this;
        }
    

**4、设置并绑定服务端Channel**  
绑定线程池后，则需要设置 channel 类型，服务端用的是 NioServerSocketChannel 。

    
    
    .channel(NioServerSocketChannel.class)
    

调用 `ServerBootstrap.channel` 方法用于设置服务端使用的 Channel，传递一个 NioServerSocketChannel
Class对象，Netty通过工厂类，利用反射创建NioServerSocketChannel 对象，如下：

    
    
        public B channel(Class<? extends C> channelClass) {
            if (channelClass == null) {
                throw new NullPointerException("channelClass");
            }
            return channelFactory(new ReflectiveChannelFactory<C>(channelClass));
        }
    

`channelFactory()` 用于设置 Channel 工厂的：

    
    
        public B channelFactory(io.netty.channel.ChannelFactory<? extends C> channelFactory) {
            return channelFactory((ChannelFactory<C>) channelFactory);
        }
    
        public B channelFactory(ChannelFactory<? extends C> channelFactory) {
            if (channelFactory == null) {
                throw new NullPointerException("channelFactory");
            }
            if (this.channelFactory != null) {
                throw new IllegalStateException("channelFactory set already");
            }
    
            this.channelFactory = channelFactory;
            return (B) this;
        }
    

这里传递的是 ReflectiveChannelFactory，其源代码如下：

    
    
    public class ReflectiveChannelFactory<T extends Channel> implements ChannelFactory<T> {
    
        private final Class<? extends T> clazz;
    
        public ReflectiveChannelFactory(Class<? extends T> clazz) {
            if (clazz == null) {
                throw new NullPointerException("clazz");
            }
            this.clazz = clazz;
        }
        //需要创建 channel 的时候，该方法将被调用
        @Override
        public T newChannel() {
            try {
                // 反射创建对应 channel
                return clazz.newInstance();
            } catch (Throwable t) {
                throw new ChannelException("Unable to create Channel from class " + clazz, t);
            }
        }
    
        @Override
        public String toString() {
            return StringUtil.simpleClassName(clazz) + ".class";
        }
    }
    

确定服务端的 Channel（NioServerSocketChannel）后，调用 `option()`方法设置 Channel
参数，作为服务端，主要是设置TCP的backlog参数，如下：

    
    
    .option(ChannelOption.SO_BACKLOG, 1024)
    

`option()`源码如下：

    
    
        public <T> B option(ChannelOption<T> option, T value) {
            if (option == null) {
                throw new NullPointerException("option");
            }
            if (value == null) {
                synchronized (options) {
                    options.remove(option);
                }
            } else {
                synchronized (options) {
                    options.put(option, value);
                }
            }
            return (B) this;
        }
    
        private final Map<ChannelOption<?>, Object> options = new LinkedHashMap<ChannelOption<?>, Object>();
    

**五、添加并设置ChannelHandler**

设置完 Channel 参数后，用户可以为启动辅助类和其父类分别指定 Handler。

    
    
     .handler(new LoggingServerHandler())
    .childHandler(new ChannelInitializer(){
        //省略代码
    })
    

这两个 Handler 不一样，前者（`handler()`）设置的 Handler 是服务端
NioServerSocketChannel的，后者（`childHandler()`）设置的 Handler 是属于每一个新建的
NioSocketChannel 的。跟踪源代码会发现两种所处的类不一样，handler 位于 AbstractBootstrap
中，childHandler 位于 ServerBootstrap 中，如下：

    
    
        // AbstractBootstrap
        public B handler(ChannelHandler handler) {
            if (handler == null) {
                throw new NullPointerException("handler");
            }
            this.handler = handler;
            return (B) this;
        }
    
        // ServerBootstrap
        public ServerBootstrap childHandler(ChannelHandler childHandler) {
            if (childHandler == null) {
                throw new NullPointerException("childHandler");
            }
            this.childHandler = childHandler;
            return this;
        }
    

ServerBootstrap 中的 Handler 是 NioServerSocketChannel 使用的，所有连接该监听端口的客户端都会执行它，父类
AbstractBootstrap 中的 Handler 是一个工厂类，它为每一个新接入的客户端都创建一个新的
Handler。如下图（《Netty权威指南（第二版）》）：

![这里写图片描述](http://img.blog.csdn.net/20171204211923932?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvY2hlbnNzeQ==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)**六、绑定端口，启动服务**

服务端最后一步，绑定端口并启动服务，如下：

    
    
    ChannelFuture future = b.bind(port).sync();
    

调用 ServerBootstrap 的 `bind()` 方法进行端口绑定：

    
    
        public ChannelFuture bind(int inetPort) {
            return bind(new InetSocketAddress(inetPort));
        }
    
        public ChannelFuture bind(SocketAddress localAddress) {
            validate();
            if (localAddress == null) {
                throw new NullPointerException("localAddress");
            }
            return doBind(localAddress);
        }    
    

首先调用 `validate()` 方法进行参数校验，然后调用 `doBind()` 方法：

    
    
        private ChannelFuture doBind(final SocketAddress localAddress) {
            // 初始化并注册一个Channel
            final ChannelFuture regFuture = initAndRegister();
    
            final Channel channel = regFuture.channel();
            if (regFuture.cause() != null) {
                return regFuture;
            }
    
            // 注册成功
            if (regFuture.isDone()) {
                // At this point we know that the registration was complete and successful.
                ChannelPromise promise = channel.newPromise();
                // 调用doBind0绑定
                doBind0(regFuture, channel, localAddress, promise);
                return promise;
            } else {
                // Registration future is almost always fulfilled already, but just in case it"s not.
                final AbstractBootstrap.PendingRegistrationPromise promise = new AbstractBootstrap.PendingRegistrationPromise(channel);
                regFuture.addListener(new ChannelFutureListener() {
                    @Override
                    public void operationComplete(ChannelFuture future) throws Exception {
                        Throwable cause = future.cause();
                        if (cause != null) {
                            // Registration on the EventLoop failed so fail the ChannelPromise directly to not cause an
                            // IllegalStateException once we try to access the EventLoop of the Channel.
                            promise.setFailure(cause);
                        } else {
                            // Registration was successful, so set the correct executor to use.
                            // See https://github.com/netty/netty/issues/2586
                            promise.registered();
    
                            doBind0(regFuture, channel, localAddress, promise);
                        }
                    }
                });
                return promise;
            }
        }
    

该方法涉及内容较多，我们分解来看，如下：

  1. 首先通过 `initAndRegister()` 得到一个 ChannelFuture 对象 regFuture；
  2. 根据得到的 regFuture 对象判断该对象是否抛出异常 （`regFuture.cause()`），如果是，直接返回；
  3. 根据 `regFuture.isDone()`判断 `initAndRegister()`是否执行完毕，如果执行完成，则调用 `doBind0`；
  4. 若 `initAndRegister()` 没有执行完毕，则向 regFuture 对象添加一个 ChannelFutureListener 监听，当 `initAndRegister()` 执行完毕后会调用 `operationComplete()`，在 `operationComplete()` 中依然会判断 ChannelFuture 是否抛出异常，如果没有则调用 `doBind0`进行绑定。

按照上面的步骤我们一步一步来剖析 `doBind()` 方法。

**initAndRegister()**

执行 `initAndRegister()` 会得到一个 ChannelFuture 对象 regFuture，代码如下：

    
    
        final ChannelFuture initAndRegister() {
            Channel channel = null;
            try {
                // 新建一个Channel
                channel = channelFactory.newChannel();
                // 初始化Channel
                init(channel);
            } catch (Throwable t) {
                if (channel != null) {
                    channel.unsafe().closeForcibly();
                }
                return new DefaultChannelPromise(channel, GlobalEventExecutor.INSTANCE).setFailure(t);
            }
    
            // /向EventLoopGroup中注册一个channel
            ChannelFuture regFuture = config().group().register(channel);
            if (regFuture.cause() != null) {
                if (channel.isRegistered()) {
                    channel.close();
                } else {
                    channel.unsafe().closeForcibly();
                }
            }
            return regFuture;
        }
    

首先调用 `newChannel()` 新建一个Channel，这里是NioServerSocketChannel，还记前面
**4、设置并绑定服务端Channel（`.channel(NioServerSocketChannel.class)`）** 中
设置的Channel工厂类么？在这里派上用处了。在上面提到了通过反射的机制我们可以得到一个 NioServerSocketChannel 类的实例。那么
NioServerSocketChannel 到底是一个什么东西呢？如下图：

![这里写图片描述](http://img.blog.csdn.net/20171204211954815?watermark/2/text/aHR0cDovL2Jsb2cuY3Nkbi5uZXQvY2hlbnNzeQ==/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70/gravity/SouthEast)

上图是 NioServerSocketChannel 的继承体系结构图， NioServerSocketChannel
在构造函数中会依靠父类来完成一项一项的初始化工作。先看 NioServerSocketChannel 构造函数。

    
    
        public NioServerSocketChannel() {
            this(newSocket(DEFAULT_SELECTOR_PROVIDER));
        }
    

`newSocket()` 方法较为简单，它是利用 `SelectorProvider.openServerSocketChannel()`，产生一个
ServerSocketChannel 对象。

    
    
        public NioServerSocketChannel(ServerSocketChannel channel) {
            super(null, channel, SelectionKey.OP_ACCEPT);
            config = new NioServerSocketChannelConfig(this, javaChannel().socket());
        }
    

该构造函数首先是调用父类的构造方法，然后设置 config属性。父类构造方法如下：

    
    
        // AbstractNioMessageChannel
        protected AbstractNioMessageChannel(Channel parent, SelectableChannel ch, int readInterestOp) {
            super(parent, ch, readInterestOp);
        }
    
        // AbstractNioChannel
        protected AbstractNioChannel(Channel parent, SelectableChannel ch, int readInterestOp) {
            super(parent);
            this.ch = ch;
            this.readInterestOp = readInterestOp;
            try {
                ch.configureBlocking(false);
            } catch (IOException e) {
                try {
                    ch.close();
                } catch (IOException e2) {
                    if (logger.isWarnEnabled()) {
                        logger.warn(
                                "Failed to close a partially initialized socket.", e2);
                    }
                }
    
                throw new ChannelException("Failed to enter non-blocking mode.", e);
            }
        }
    
        // AbstractChannel
        protected AbstractChannel(Channel parent) {
            this.parent = parent;
            id = newId();
            unsafe = newUnsafe();
            pipeline = newChannelPipeline();
        }
    

通过 `super()` ，一层一层往上，直到 AbstractChannel。我们从最上层解析。

  * AbstractChannel 设置了 unsafe (`unsafe = newUnsafe()`)和 pipeline(`pipeline = newChannelPipeline()`)；
  * AbstractNioChannel 将当前 ServerSocketChannel 设置成了非阻塞（`ch.configureBlocking(false);`），同时设置SelectionKey.OP_ACCEPT事件(`this.readInterestOp = readInterestOp;` readInterestOp 值由 NioServerSocketChannel 中传递)；
  * NioServerSocketChannel 设置 config属性（`config = new NioServerSocketChannelConfig(this, javaChannel().socket())`）。

> 所以 `channel = channelFactory.newChannel()` 通过反射机制产生了 NioServerSocketChannel
类实例。同时该实例设置了NioMessageUnsafe、DefaultChannelPipeline、非阻塞、SelectionKey.OP_ACCEPT事件
和 NioServerSocketChannelConfig 属性。

看完了 `channelFactory.newChannel();`，我们再看 `init()`。

    
    
        void init(Channel channel) throws Exception {
             // 设置配置的option参数
            final Map<ChannelOption<?>, Object> options = options0();
            synchronized (options) {
                channel.config().setOptions(options);
            }
    
            final Map<AttributeKey<?>, Object> attrs = attrs0();
            synchronized (attrs) {
                for (Entry<AttributeKey<?>, Object> e: attrs.entrySet()) {
                    @SuppressWarnings("unchecked")
                    AttributeKey<Object> key = (AttributeKey<Object>) e.getKey();
                    channel.attr(key).set(e.getValue());
                }
            }
    
            // 获取绑定的pipeline
            ChannelPipeline p = channel.pipeline();
    
            // 准备child用到的4个part
            final EventLoopGroup currentChildGroup = childGroup;
            final ChannelHandler currentChildHandler = childHandler;
            final Entry<ChannelOption<?>, Object>[] currentChildOptions;
            final Entry<AttributeKey<?>, Object>[] currentChildAttrs;
            synchronized (childOptions) {
                currentChildOptions = childOptions.entrySet().toArray(newOptionArray(childOptions.size()));
            }
            synchronized (childAttrs) {
                currentChildAttrs = childAttrs.entrySet().toArray(newAttrArray(childAttrs.size()));
            }
    
            // 为NioServerSocketChannel的pipeline添加一个初始化Handler,
            // 当NioServerSocketChannel在EventLoop注册成功时，该handler的init方法将被调用
            p.addLast(new ChannelInitializer<Channel>() {
                @Override
                public void initChannel(Channel ch) throws Exception {
                    final ChannelPipeline pipeline = ch.pipeline();
                    ChannelHandler handler = config.handler();
                    //如果用户配置过Handler
                    if (handler != null) {
                        pipeline.addLast(handler);
                    }
    
                    ch.eventLoop().execute(new Runnable() {
                        @Override
                        public void run() {
                            // 为NioServerSocketChannel的pipeline添加ServerBootstrapAcceptor处理器
                            // 该Handler主要用来将新创建的NioSocketChannel注册到EventLoopGroup中
                            pipeline.addLast(new ServerBootstrapAcceptor(
                                    currentChildGroup, currentChildHandler, currentChildOptions, currentChildAttrs));
                        }
                    });
                }
            });
        }
    

其实整个过程可以分为三个步骤：

  1. 设置 Channel 的 option 和 attr；
  2. 获取绑定的 pipeline，然后为 NioServerSocketChanne l绑定的 pipeline 添加 Handler；
  3. 将用于服务端注册的 Handler ServerBootstrapAcceptor 添加到 ChannelPipeline 中。ServerBootstrapAcceptor 为一个接入器，专门接受新请求，把新的请求扔给某个事件循环器。

至此初始化部分已经结束，我们再看注册部分，

    
    
            // /向EventLoopGroup中注册一个channel
            ChannelFuture regFuture = config().group().register(channel);
    

注册方法的调用位于 `initAndRegister()` 方法中。注意这里的 `group()` 返回的是前面的 boss
NioEvenLoopGroup，它继承 MultithreadEventLoopGroup，调用的 `register()`，也是
MultithreadEventLoopGroup 中的。如下：

    
    
        public ChannelFuture register(Channel channel) {
            return next().register(channel);
        }
    

调用 `next()` 方法从 EventLoopGroup 中获取下一个 EventLoop，调用 `register()` 方法注册：

    
    
        public ChannelFuture register(Channel channel) {
            return register(new DefaultChannelPromise(channel, this));
        }
    

将Channel和EventLoop封装成一个DefaultChannelPromise对象，然后调用register()方法。DefaultChannelPromis为ChannelPromise的默认实现，而ChannelPromisee继承Future，具备异步执行结构，绑定Channel，所以又具备了监听的能力，故而ChannelPromis是Netty异步执行的核心接口。

    
    
        public ChannelFuture register(ChannelPromise promise) {
            ObjectUtil.checkNotNull(promise, "promise");
            promise.channel().unsafe().register(this, promise);
            return promise;
        }
    

首先获取 channel 的 unsafe 对象，该 unsafe 对象就是在之前设置过得。然后调用 `register()` 方法，如下：

    
    
            public final void register(EventLoop eventLoop, final ChannelPromise promise) {
                if (eventLoop == null) {
                    throw new NullPointerException("eventLoop");
                }
                if (isRegistered()) {
                    promise.setFailure(new IllegalStateException("registered to an event loop already"));
                    return;
                }
                if (!isCompatible(eventLoop)) {
                    promise.setFailure(
                            new IllegalStateException("incompatible event loop type: " + eventLoop.getClass().getName()));
                    return;
                }
    
                AbstractChannel.this.eventLoop = eventLoop;
    
                // 必须要保证注册是由该EventLoop发起的
                if (eventLoop.inEventLoop()) {
                    register0(promise);        // 注册
                } else {
                    // 如果不是单独封装成一个task异步执行
                    try {
                        eventLoop.execute(new Runnable() {
                            @Override
                            public void run() {
                                register0(promise);
                            }
                        });
                    } catch (Throwable t) {
                        logger.warn(
                                "Force-closing a channel whose registration task was not accepted by an event loop: {}",
                                AbstractChannel.this, t);
                        closeForcibly();
                        closeFuture.setClosed();
                        safeSetFailure(promise, t);
                    }
                }
            }
    

过程如下：

  1. 首先通过`isRegistered()` 判断该 Channel 是否已经注册到 EventLoop 中；
  2. 通过 `eventLoop.inEventLoop()` 来判断当前线程是否为该 EventLoop 自身发起的，如果是，则调用 `register0()` 直接注册；
  3. 如果不是，说明该 EventLoop 中的线程此时没有执行权，则需要新建一个线程，单独封装一个 Task，而该 Task 的主要任务则是执行 `register0()`。

无论当前 EventLoop 的线程是否拥有执行权，最终都会要执行 `register0()`，如下：

    
    
            private void register0(ChannelPromise promise) {
                try {
                    // 确保 Channel 处于 open
                    if (!promise.setUncancellable() || !ensureOpen(promise)) {
                        return;
                    }
                    boolean firstRegistration = neverRegistered;
    
                    // 真正的注册动作
                    doRegister();
    
                    neverRegistered = false;
                    registered = true;        
    
                    pipeline.invokeHandlerAddedIfNeeded();    
                    safeSetSuccess(promise);        //设置注册结果为成功
    
                    pipeline.fireChannelRegistered();
    
                    if (isActive()) { 
                        //如果是首次注册,发起 pipeline 的 fireChannelActive
                        if (firstRegistration) {
                            pipeline.fireChannelActive();
                        } else if (config().isAutoRead()) {
                            beginRead();
                        }
                    }
                } catch (Throwable t) {
                    closeForcibly();
                    closeFuture.setClosed();
                    safeSetFailure(promise, t);
                }
            }
    

如果 Channel 处于 open 状态，则调用 `doRegister()`
方法完成注册，然后将注册结果设置为成功。最后判断如果是首次注册且处于激活状态，则发起 pipeline 的 `fireChannelActive()`。

    
    
        protected void doRegister() throws Exception {
            boolean selected = false;
            for (;;) {
                try {
                    // 注册到NIOEventLoop的Selector上
                    selectionKey = javaChannel().register(eventLoop().selector, 0, this);
                    return;
                } catch (CancelledKeyException e) {
                    if (!selected) {
                        eventLoop().selectNow();
                        selected = true;
                    } else {
                        throw e;
                    }
                }
            }
        }
    

这里注册时 ops 设置的是 0，也就是说 ServerSocketChannel
仅仅只是表示了注册成功，还不能监听任何网络操作，这样做的目的是（摘自《Netty权威指南（第二版）》）：

  1. 注册方式是多态的，它既可以被 NIOServerSocketChannel 用来监听客户端的连接接入，也可以注册 SocketChannel 用来监听网络读或者写操作。
  2. 通过 `SelectionKey.interestOps(int ops)` 方法可以方便地修改监听操作位。所以，此处注册需要获取 SelectionKey 并给 AbstractNIOChannel 的成员变量 selectionKey 赋值。

由于这里 ops 设置为 0，所以还不能监听读写事件。调用
`doRegister()`后，然后调用`pipeline.invokeHandlerAddedIfNeeded();`，这个时候控制台会出现
`loggin-handlerAdded`，内部如何调用，我们在剖析 pipeline
时再做详细分析。然后将注册结果设置为成功（`safeSetSuccess(promise)`）。调用
`pipeline.fireChannelRegistered();` 这个时候控制台会打印 `loggin-
channelRegistered`。这里简单分析下该方法。

    
    
        public final ChannelPipeline fireChannelRegistered() {
            AbstractChannelHandlerContext.invokeChannelRegistered(head);
            return this;
        }
    
        static void invokeChannelRegistered(final AbstractChannelHandlerContext next) {
            EventExecutor executor = next.executor();
            if (executor.inEventLoop()) {
                next.invokeChannelRegistered();
            } else {
                executor.execute(new Runnable() {
                    @Override
                    public void run() {
                        next.invokeChannelRegistered();
                    }
                });
            }
        }
    

pipeline 维护着 handle 链表，事件会在 NioServerSocketChannel 的 pipeline 中传播。最终都会调用
`next.invokeChannelRegistered()`，如下：

    
    
        private void invokeChannelRegistered() {
            if (invokeHandler()) {
                try {
                    ((ChannelInboundHandler) handler()).channelRegistered(this);
                } catch (Throwable t) {
                    notifyHandlerException(t);
                }
            } else {
                fireChannelRegistered();
            }
        }
    

在 `invokeChannelRegistered()` 会调用我们在前面设置的 handler （还记得签名的 `handler(new
LoggingServerHandler()` )么）的 `channelRegistered()`，这个时候控制台应该会打印 `loggin-
channelRegistered`。

到这里`initAndRegister() (final ChannelFuture regFuture =
initAndRegister();)`就分析完毕了，该方法主要做如下三件事：

  1. 通过反射产生了一个 NioServerSocketChannle 对象；
  2. 调用 `init(channel)`完成初始化工作；
  3. 将NioServerSocketChannel进行了注册。

`initAndRegister()`篇幅较长，分析完毕了，我们再返回到`doBind(final SocketAddress
localAddress)`。在 `doBind(final SocketAddress localAddress)` 中如果
`initAndRegister()`执行完成，则 `regFuture.isDone()` 则为 true，执行
`doBind0()`。如果没有执行完成，则会注册一个监听 ChannelFutureListener，当 `initAndRegister()`
完成后，会调用该监听的 `operationComplete()`方法，最终目的还是执行 `doBind0()`。故而我们下面分析
`doBind0()`到底做了些什么。源码如下：

    
    
        private static void doBind0(
                final ChannelFuture regFuture, final Channel channel,
                final SocketAddress localAddress, final ChannelPromise promise) {
    
            channel.eventLoop().execute(new Runnable() {
                @Override
                public void run() {
                    if (regFuture.isSuccess()) {
                        channel.bind(localAddress, promise).addListener(ChannelFutureListener.CLOSE_ON_FAILURE);
                    } else {
                        promise.setFailure(regFuture.cause());
                    }
                }
            });
        }
    

`doBind0()` 较为简单，首先new 一个线程 task，然后将该任务提交到 NioEventLoop 中进行处理，我们先看
`execute()`。

    
    
      public void execute(Runnable task) {
            if (task == null) {
                throw new NullPointerException("task");
            }
    
            boolean inEventLoop = inEventLoop();
            if (inEventLoop) {
                addTask(task);
            } else {
                startThread();
                addTask(task);
                if (isShutdown() && removeTask(task)) {
                    reject();
                }
            }
    
            if (!addTaskWakesUp && wakesUpForTask(task)) {
                wakeup(inEventLoop);
            }
        }
    

调用 `inEventLoop()` 判断当前线程是否为该 NioEventLoop 所关联的线程，如果是，则调用 `addTask()` 将任务 task
添加到队列中，如果不是，则先启动线程，在调用 `addTask()` 将任务 task 添加到队列中。`addTask()` 如下：

    
    
        protected void addTask(Runnable task) {
            if (task == null) {
                throw new NullPointerException("task");
            }
            if (!offerTask(task)) {
                reject(task);
            }
        }
    

`offerTask()`添加到队列中：

    
    
        final boolean offerTask(Runnable task) {
            if (isShutdown()) {
                reject();
            }
            return taskQueue.offer(task);
        }
    

task 添加到任务队列 taskQueue成功后，执行任务会调用如下方法：

    
    
     channel.bind(localAddress, promise).addListener(ChannelFutureListener.CLOSE_ON_FAILURE);
    

channel 首先调用 `bind()` 完成 channel 与端口的绑定，如下：

    
    
        public ChannelFuture bind(SocketAddress localAddress, ChannelPromise promise) {
            return pipeline.bind(localAddress, promise);
        }
    
        public final ChannelFuture bind(SocketAddress localAddress, ChannelPromise promise) {
            return tail.bind(localAddress, promise);
        }
    

tail 在 DefaultChannelPipeline 中定义：`final AbstractChannelHandlerContext tail;`
有 tail 就会有 head ，在 DefaultChannelPipeline 中维护这一个 AbstractChannelHandlerContext
节点的双向链表，该链表是实现 Pipeline 机制的关键，更多详情会在 ChannelPipeline 中做详细说明。`bind()` 最终会调用
DefaultChannelPipeline 的 `bind()` 方法。如下：

    
    
        public ChannelFuture bind(final SocketAddress localAddress, final ChannelPromise promise) {
            if (localAddress == null) {
                throw new NullPointerException("localAddress");
            }
            if (!validatePromise(promise, false)) {
                // cancelled
                return promise;
            }
    
            final AbstractChannelHandlerContext next = findContextOutbound();
            EventExecutor executor = next.executor();
            if (executor.inEventLoop()) {
                next.invokeBind(localAddress, promise);
            } else {
                safeExecute(executor, new Runnable() {
                    @Override
                    public void run() {
                        next.invokeBind(localAddress, promise);
                    }
                }, promise, null);
            }
            return promise;
        }
    

首先对 localAddress 、 promise 进行校验，符合规范则调用 `findContextOutbound()` ，该方法用于在
pipeline 中获取 AbstractChannelHandlerContext 双向链表中的一个节点，如下：

    
    
        private AbstractChannelHandlerContext findContextOutbound() {
            AbstractChannelHandlerContext ctx = this;
            do {
                ctx = ctx.prev;
            } while (!ctx.outbound);
            return ctx;
        }
    

从该方法可以看出，所获取的节点是从 tail 开始遍历，获取第一个节点属性 outbound 为 true 的节点。其实该节点是
AbstractChannelHandlerContext 双向链表的 head 节点。获取该节点后，调用 `invokeBind()`，如下：

    
    
        private void invokeBind(SocketAddress localAddress, ChannelPromise promise) {
            if (invokeHandler()) {
                try {
                    ((ChannelOutboundHandler) handler()).bind(this, localAddress, promise);
                } catch (Throwable t) {
                    notifyOutboundHandlerException(t, promise);
                }
            } else {
                bind(localAddress, promise);
            }
        }
    

`handler()` 返回的是 HeadContext 对象，然后调用其`bind()`，如下：

    
    
            public void bind(
                    ChannelHandlerContext ctx, SocketAddress localAddress, ChannelPromise promise)
                    throws Exception {
                unsafe.bind(localAddress, promise);
            }
    

unsafe 定义在 HeadContext 中，在构造函数中初始化（`unsafe = pipeline.channel().unsafe();`），调用
`bind()` 如下：

    
    
            public final void bind(final SocketAddress localAddress, final ChannelPromise promise) {
                assertEventLoop();
    
                if (!promise.setUncancellable() || !ensureOpen(promise)) {
                    return;
                }
    
                if (Boolean.TRUE.equals(config().getOption(ChannelOption.SO_BROADCAST)) &&
                    localAddress instanceof InetSocketAddress &&
                    !((InetSocketAddress) localAddress).getAddress().isAnyLocalAddress() &&
                    !PlatformDependent.isWindows() && !PlatformDependent.isRoot()) {
    
                    logger.warn(
                            "A non-root user can"t receive a broadcast packet if the socket " +
                            "is not bound to a wildcard address; binding to a non-wildcard " +
                            "address (" + localAddress + ") anyway as requested.");
                }
    
                boolean wasActive = isActive();
                try {
                    // 最核心方法
                    doBind(localAddress);
                } catch (Throwable t) {
                    safeSetFailure(promise, t);
                    closeIfClosed();
                    return;
                }
    
                if (!wasActive && isActive()) {
                    invokeLater(new Runnable() {
                        @Override
                        public void run() {
                            pipeline.fireChannelActive();
                        }
                    });
                }
    
                safeSetSuccess(promise);
            }
    

内部调用 `doBind()` ，该方法为绑定中最核心的方法，位于 NioServerSocketChannel 中，如下：

    
    
        protected void doBind(SocketAddress localAddress) throws Exception {
            if (PlatformDependent.javaVersion() >= 7) {
                javaChannel().bind(localAddress, config.getBacklog());
            } else {
                javaChannel().socket().bind(localAddress, config.getBacklog());
            }
        }
    

`javaChannel()`返回的是 NioServerSocketChannel 实例初始化时所产生的 Java NIO
ServerSocketChannel 实例（ServerSocketChannelImple实例），然后调用其 `bind()`，如下：

    
    
        public ServerSocketChannel bind(SocketAddress var1, int var2) throws IOException {
            Object var3 = this.lock;
            synchronized(this.lock) {
                if(!this.isOpen()) {
                    throw new ClosedChannelException();
                } else if(this.isBound()) {
                    throw new AlreadyBoundException();
                } else {
                    InetSocketAddress var4 = var1 == null?new InetSocketAddress(0):Net.checkAddress(var1);
                    SecurityManager var5 = System.getSecurityManager();
                    if(var5 != null) {
                        var5.checkListen(var4.getPort());
                    }
    
                    NetHooks.beforeTcpBind(this.fd, var4.getAddress(), var4.getPort());
                    Net.bind(this.fd, var4.getAddress(), var4.getPort());
                    Net.listen(this.fd, var2 < 1?50:var2);
                    Object var6 = this.stateLock;
                    synchronized(this.stateLock) {
                        this.localAddress = Net.localAddress(this.fd);
                    }
    
                    return this;
                }
            }
        }
    

该方法属于 Java NIO 层次的，该方法涉及到服务端端口的绑定，端口的监听，这些内容在后续的 Channel 时做详细介绍。

到这里就真正完成了服务端端口的绑定。

> 这篇博客比较长，大体上从源码层次稍微解读了 Netty 服务端的启动过程，当中涉及到 Netty
的各个核心组件，只能笼统来描述服务端的启动过程，具体的细节部分还需要后续做详细分析，而且其中有多个点还是懵懵懂懂，相信在后面对 Netty
的分析过程会一一解答。

>

> 谢谢阅读，祝好!!!

## 参考资料

  * 《Netty权威指南（第二版）》
  * 《Netty IN ACTION》
  * [Netty源码分析：服务端启动全过程(篇幅很长)](http://blog.csdn.net/u010412719/article/details/78077183)

