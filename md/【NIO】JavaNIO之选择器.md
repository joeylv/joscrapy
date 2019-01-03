**一、前言**

前面已经学习了缓冲和通道，接着学习选择器。

**二、选择器**

2.1 选择器基础

选择器管理一个被注册的通道集合的信息和它们的就绪状态，通道和选择器一起被注册，并且选择器可更新通道的就绪状态，也可将被唤醒的线程挂起，直到有通道就绪。

SelectableChannel 可被注册到 Selector
对象上，同时可以指定对那个选择器而言，哪种操作是感兴趣的。一个通道可以被注册到多个选择器上，但对每个选择器而言，只能被注册一次，通道在被注册到一个选择器上之前，必须先设置为非阻塞模式，通过调用通道的configureBlocking(false)方法即可。这意味着不能将FileChannel与Selector一起使用，因为FileChannel不能切换到非阻塞模式，而套接字通道都可以。

选择键封装了特定的通道与特定的选择器的注册关系，选择键对象被SelectableChannel.register( )
方法返回并提供一个表示这种注册关系的标记。选择键包含了两个比特集（以整数的形式进行编码），指示了该注册关系所关心的通道操作及通道已经准备好的操作。

如下代码演示了通道与选择器之间的关系

    
    
    Selector selector = Selector.open( );
    channel1.register (selector, SelectionKey.OP_READ);
    channel2.register (selector, SelectionKey.OP_WRITE);
    channel3.register (selector, SelectionKey.OP_READ | SelectionKey.OP_WRITE);
    // Wait up to 10 seconds for a channel to become ready
    readyCount = selector.select (10000);

三个通道注册到了选择器上，并且感兴趣的操作各不相同， **select( )方法在将线程置于睡眠状态**
，直到感兴趣的操作中的一个发生或者等待10秒钟的时间。

现有的可选操作有读(read)，写(write)，连接(connect)和接受(accept)等四种操作，并非所有的操作都在所有的可选择通道上被支持。例如SocketChannel
不支持 accept。

2.2 使用选择键

一个键表示了一个特定的通道对象和一个特定的选择器对象之间的注册关系。当键被取消时，它将被放在相关的选择器的已取消的键的集合里。注册不会立即被取消，但键会立即失效。

通道不会在键被取消的时候立即注销。直到下一次操作发生为止，它们仍然会处于被注册的状态。

一个 SelectionKey 对象包含两个以整数形式进行编码的比特掩码： **一个用于指示那些通道/选择器组合体所关心的操作(insterest
集合)，另一个表示通道准备好要执行的操作（ ready 集合）** 。可以通过调用键的 readyOps(
)方法来获取相关的通道的已经就绪的操作，ready集合是interest集合的子集，表示interest集合中从上次调用select(
)以来已经就绪的那些操作。

2.3 使用选择器

已注册的键的集合：与选择器关联的已经注册的键的集合，并非所有注册过的键都仍然有效。这个集合通过keys(
)方法返回，可能为空。这个已注册的键的集合不可直接修改。  

已选择的键的集合：已注册的键的集合的子集。该集合的每个成员都是相关的通道被选择器（在前一个select操作中）判断为已为就绪状态，并且包含于键的
interest 集合中的操作。  

已取消的键的集合：已注册的键的集合的子集，这个集合包含了 cancel( )方法被调用过的键（这个键已经被无效化），但它们还没有被注销。  

有如下三种方式可以唤醒在 select( )方法中睡眠的线程。  

① wakeup方法，wakeup( )方法将使得选择器上的第一个还没有返回的选择操作立即返回。如果当前没有在进行中的选择，那么下一次对 select(
)方法的调用将立即返回，后续的选择操作将正常进行。有时并不想要这种延迟的唤醒行为，而只想唤醒一个睡眠中的线程，后续的选择继续正常地进行，此时可以通过在调用
wakeup( )方法后调用 selectNow( )方法解决该问题。

② close方法，close( )方法会使得任何一个在select操作中阻塞的线程都将被唤醒，如同调用wakeup(
)方法，与选择器相关的通道将被注销，而键将被取消。

③ interrupt方法，如果睡眠中的线程的 interrupt( )方法被调用，它的返回状态将被设置。如果被唤醒的线程之后将试图在通道上执行 I/O
操作，通道将立即关闭，然后线程将捕捉到一个异常。

下面示例展示了Selector和通道的基本使用方法

    
    
    import java.nio.ByteBuffer;
    import java.nio.channels.ServerSocketChannel;
    import java.nio.channels.SocketChannel;
    import java.nio.channels.Selector;
    import java.nio.channels.SelectionKey;
    import java.nio.channels.SelectableChannel;
    import java.net.ServerSocket;
    import java.net.InetSocketAddress;
    import java.util.Iterator;
    
    /**
     * Created by LEESF on 2017/4/24.
     */
    public class SelectorDemo {
        public static int PORT_NUMBER = 1234;
    
        public static void main(String[] argv) throws Exception {
            new SelectorDemo().go(argv);
        }
    
        private void go(String[] argv) throws Exception {
            int port = PORT_NUMBER;
            if (argv.length > 0) {
                port = Integer.parseInt(argv[0]);
            }
            System.out.println("Listening on port " + port);
    
            ServerSocketChannel serverChannel = ServerSocketChannel.open();
            ServerSocket serverSocket = serverChannel.socket();
            Selector selector = Selector.open();
            serverSocket.bind(new InetSocketAddress(port));
            serverChannel.configureBlocking(false);
            serverChannel.register(selector, SelectionKey.OP_ACCEPT);
            while (true) {
                int n = selector.select();
                if (n == 0) {
                    continue;
                }
                Iterator it = selector.selectedKeys().iterator();
                while (it.hasNext()) {
                    SelectionKey key = (SelectionKey) it.next();
                    if (key.isAcceptable()) {
                        ServerSocketChannel server =
                                (ServerSocketChannel) key.channel();
                        SocketChannel channel = server.accept();
                        registerChannel(selector, channel,
                                SelectionKey.OP_READ);
                        sayHello(channel);
                    }
                    if (key.isReadable()) {
                        readDataFromSocket(key);
                    }
                    it.remove();
                }
            }
        }
    
        private void registerChannel(Selector selector,
                                       SelectableChannel channel, int ops) throws Exception {
            if (channel == null) {
                return;
            }
            channel.configureBlocking(false);
            channel.register(selector, ops);
        }
    
        private ByteBuffer buffer = ByteBuffer.allocateDirect(1024);
    
        private void readDataFromSocket(SelectionKey key) throws Exception {
            SocketChannel socketChannel = (SocketChannel) key.channel();
            int count;
            buffer.clear();
            while ((count = socketChannel.read(buffer)) > 0) {
                buffer.flip();
                while (buffer.hasRemaining()) {
                    socketChannel.write(buffer);
                }
                buffer.clear();
            }
            if (count < 0) {
                socketChannel.close();
            }
        }
    
        private void sayHello(SocketChannel channel) throws Exception {
            buffer.clear();
            buffer.put("Hi there!\r\n".getBytes());
            buffer.flip();
            channel.write(buffer);
        }
    }

在多线程的场景中，如果需要对任何一个键的集合进行更改，不管是直接更改还是其他操作带来的副作用，都需要首先以相同的顺序，在同一对象上进行同步。

2.4 选择过程的可扩展性

如下示例使用线程池来为通道提供服务。

    
    
    import java.nio.ByteBuffer;
    import java.nio.channels.SocketChannel;
    import java.nio.channels.SelectionKey;
    import java.util.List;
    import java.util.LinkedList;
    import java.io.IOException;
    
    /**
     * Created by LEESF on 2017/4/24.
     */
    public class SelectSocketsThreadPool extends SelectorDemo{
        private static final int MAX_THREADS = 5;
        private ThreadPool pool = new ThreadPool(MAX_THREADS);
        public static void main(String[] argv) throws Exception {
            new SelectSocketsThreadPool().go(argv);
        }
    
        protected void readDataFromSocket(SelectionKey key) throws Exception {
            WorkerThread worker = pool.getWorker();
            if (worker == null) {
                return;
            }
            worker.serviceChannel(key);
        }
        private class ThreadPool {
            List idle = new LinkedList();
            ThreadPool(int poolSize) {
                for (int i = 0; i < poolSize; i++) {
                    WorkerThread thread = new WorkerThread(this);
                    thread.setName("Worker" + (i + 1));
                    thread.start();
                    idle.add(thread);
                }
            }
    
            WorkerThread getWorker() {
                WorkerThread worker = null;
                synchronized (idle) {
                    if (idle.size() > 0) {
                        worker = (WorkerThread) idle.remove(0);
                    }
                }
                return (worker);
            }
    
            void returnWorker(WorkerThread worker) {
                synchronized (idle) {
                    idle.add(worker);
                }
            }
        }
    
        private class WorkerThread extends Thread {
            private ByteBuffer buffer = ByteBuffer.allocate(1024);
            private ThreadPool pool;
            private SelectionKey key;
            WorkerThread(ThreadPool pool) {
                this.pool = pool;
            }
            public synchronized void run() {
                System.out.println(this.getName() + " is ready");
                while (true) {
                    try {
                        this.wait();
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                        this.interrupted();
                    }
                    if (key == null) {
                        continue; // just in case
                    }
                    System.out.println(this.getName() + " has been awakened");
                    try {
                        drainChannel(key);
                    } catch (Exception e) {
                        System.out.println("Caught "" + e
                                + "" closing channel");
                        try {
                            key.channel().close();
                        } catch (IOException ex) {
                            ex.printStackTrace();
                        }
                        key.selector().wakeup();
                    }
                    key = null;
                    this.pool.returnWorker(this);
                }
            }
    
            synchronized void serviceChannel(SelectionKey key) {
                this.key = key;
                key.interestOps(key.interestOps() & (~SelectionKey.OP_READ));
                this.notify();
            }
            void drainChannel(SelectionKey key) throws Exception {
                SocketChannel channel = (SocketChannel) key.channel();
                int count;
                buffer.clear();
                while ((count = channel.read(buffer)) > 0) {
                    buffer.flip();
                    while (buffer.hasRemaining()) {
                        channel.write(buffer);
                    }
                    buffer.clear();
                }
                if (count < 0) {
                    channel.close();
                    return;
                }
                key.interestOps(key.interestOps() | SelectionKey.OP_READ);
                key.selector().wakeup();
            }
        }
    }

下面示例使用Selector完成客户端与服务端的通信，其中SelectorServerSocketChannel为服务端，SelectorSocketChannel为客户端，先启动服务端，然后启动客户端，连接成功后，客户端发送信息至服务端，服务端收到信息后，反馈信息给客户端。

SelectorServerSocketChannel

    
    
    import java.net.InetSocketAddress;
    import java.net.ServerSocket;
    import java.nio.ByteBuffer;
    import java.nio.CharBuffer;
    import java.nio.channels.*;
    import java.nio.charset.Charset;
    import java.nio.charset.CharsetDecoder;
    import java.util.Iterator;
    
    /**
     * Created by LEESF on 2017/4/24.
     */
    public class SelectorServerSocketChannel {
        public static void main(String[] args) throws Exception{
            ServerSocketChannel serverSocketChannel = ServerSocketChannel.open();
            ServerSocket serverSocket = serverSocketChannel.socket();
            serverSocketChannel.configureBlocking(false);
            serverSocket.bind(new InetSocketAddress("localhost", 1234));
    
            Selector selector = Selector.open();
            serverSocketChannel.register(selector, SelectionKey.OP_ACCEPT);
            while (true) {
                selector.select();
                Iterator it = selector.selectedKeys().iterator();
                while (it.hasNext()) {
                    SelectionKey key = (SelectionKey) it.next();
                    if (key.isAcceptable()) {
                        ServerSocketChannel server =
                                (ServerSocketChannel) key.channel();
                        SocketChannel channel = server.accept();
                        channel.configureBlocking(false);
                        channel.register(selector, SelectionKey.OP_READ);
                        System.out.println("Connected: " + channel.socket().getRemoteSocketAddress());
                    }
                    if (key.isReadable()) {
                        ByteBuffer byteBuffer = ByteBuffer.allocate(512);
                        SocketChannel socketChannel = (SocketChannel) key.channel();
                        socketChannel.read(byteBuffer);
                        byteBuffer.flip();
                        System.out.println("server received message: " + getString(byteBuffer));
                        byteBuffer.clear();
                        String message = "server sending message " + System.currentTimeMillis();
                        System.out.println("server sending message: " + message);
                        byteBuffer.put(message.getBytes());
                        byteBuffer.flip();
                        socketChannel.write(byteBuffer);
                    }
    
                    it.remove();
                }
            }
        }
    
        private static String getString(ByteBuffer buffer) {
            Charset charset;
            CharsetDecoder decoder;
            CharBuffer charBuffer;
            try {
                charset = Charset.forName("UTF-8");
                decoder = charset.newDecoder();
                charBuffer = decoder.decode(buffer.asReadOnlyBuffer());
                return charBuffer.toString();
            } catch (Exception ex) {
                ex.printStackTrace();
                return "";
            }
        }
    }

SelectorSocketChannel客户端

    
    
    import java.net.InetSocketAddress;
    import java.nio.ByteBuffer;
    import java.nio.CharBuffer;
    import java.nio.channels.SelectionKey;
    import java.nio.channels.SocketChannel;
    import java.nio.charset.Charset;
    import java.nio.charset.CharsetDecoder;
    import java.nio.channels.Selector;
    import java.util.Iterator;
    
    /**
     * Created by LEESF on 2017/4/24.
     */
    public class SelectorSocketChannel {
        public static void main(String[] args) throws Exception {
            SocketChannel socketChannel = SocketChannel.open();
            socketChannel.configureBlocking(false);
            Selector selector = Selector.open();
            socketChannel.connect(new InetSocketAddress("localhost",1234));
            socketChannel.register(selector, SelectionKey.OP_CONNECT);
    
            while (true) {
                selector.select();
                Iterator it = selector.selectedKeys().iterator();
                while (it.hasNext()) {
                    SelectionKey key = (SelectionKey) it.next();
                    it.remove();
                    if (key.isConnectable()) {
                        if (socketChannel.isConnectionPending()) {
                            if (socketChannel.finishConnect()) {
                                key.interestOps(SelectionKey.OP_READ);
                                sendMessage(socketChannel);
                            } else {
                                key.cancel();
                            }
                        }
                    }
                    if(key.isReadable()) {
                        ByteBuffer byteBuffer = ByteBuffer.allocate(512);
                        while (true) {
                            byteBuffer.clear();
                            int count = socketChannel.read(byteBuffer);
                            if (count > 0) {
                                byteBuffer.flip();
                                System.out.println("client receive message: " + getString(byteBuffer));
                                break;
                            }
                        }
                    }
                }
            }
        }
    
        private static void sendMessage(SocketChannel socketChannel) throws Exception {
            String message = "client sending message " + System.currentTimeMillis();
            ByteBuffer byteBuffer = ByteBuffer.allocate(512);
            byteBuffer.clear();
            System.out.println("client sending message: " + message);
            byteBuffer.put(message.getBytes());
            byteBuffer.flip();
            socketChannel.write(byteBuffer);
        }
    
        private static String getString(ByteBuffer buffer) {
            Charset charset;
            CharsetDecoder decoder;
            CharBuffer charBuffer;
            try {
                charset = Charset.forName("UTF-8");
                decoder = charset.newDecoder();
                charBuffer = decoder.decode(buffer.asReadOnlyBuffer());
                return charBuffer.toString();
            } catch (Exception ex) {
                ex.printStackTrace();
                return "";
            }
        }
    }

客户端输出结果：

    
    
    client sending message: client sending message 1493032984099
    client receive message: server sending message 1493032984101

服务端输出结果：

    
    
    Connected: /127.0.0.1:49859
    server received message: client sending message 1493032984099
    server sending message: server sending message 1493032984101

**三、总结**

本篇博文讲解了选择器的基础知识点，使用选择器可以大幅度的提升系统的性能，使得开发更为便捷，至此，整个NIO的内容就学到这里，之后会学习Netty，同时，所有源码已经上传至[github](https://github.com/leesf/java_nio_examples)，欢迎star，也谢谢各位园友的观看~

