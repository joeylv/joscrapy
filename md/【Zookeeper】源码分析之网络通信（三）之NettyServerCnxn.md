**一、前言**

前面已经学习了NIOServerCnxn，接着继续学习NettyServerCnxn。

**二、NettyServerCnxn源码分析**

2.1 类的继承关系

    
    
     public class NettyServerCnxn extends ServerCnxn {}

说明：NettyServerCnxn继承了ServerCnxn抽象类，使用Netty框架来高效处理与客户端之间的通信。

2.2 类的内部类

1\. SendBufferWriter类

![]()![]()

    
    
        private class SendBufferWriter extends Writer {
            private StringBuffer sb = new StringBuffer();
            
            /**
             * Check if we are ready to send another chunk.
             * @param force force sending, even if not a full chunk
             */
            // 是否准备好发送另一块
            private void checkFlush(boolean force) {
                if ((force && sb.length() > 0) || sb.length() > 2048) { // 当强制发送并且sb大小大于0，或者sb大小大于2048即发送缓存
                    sendBuffer(ByteBuffer.wrap(sb.toString().getBytes()));
                    // clear our internal buffer
                    sb.setLength(0);
                }
            }
    
            @Override
            public void close() throws IOException {
                if (sb == null) return;
                // 关闭之前需要强制性发送缓存
                checkFlush(true);
                sb = null; // clear out the ref to ensure no reuse
            }
    
            @Override
            public void flush() throws IOException {
                checkFlush(true);
            }
    
            @Override
            public void write(char[] cbuf, int off, int len) throws IOException {
                sb.append(cbuf, off, len);
                checkFlush(false);
            }
        }

SendBufferWriter

说明：与NIOServerCnxn中相同，该类用来将给客户端的响应进行分块，不再累赘。

2\. ResumeMessageEvent类

![]()![]()

    
    
        static class ResumeMessageEvent implements MessageEvent {
            // 通道
            Channel channel;
            
            // 构造函数
            ResumeMessageEvent(Channel channel) {
                this.channel = channel;
            }
            @Override
            public Object getMessage() {return null;}
            @Override
            public SocketAddress getRemoteAddress() {return null;}
            @Override
            public Channel getChannel() {return channel;}
            @Override
            public ChannelFuture getFuture() {return null;}
        };

ResumeMessageEvent

说明：ResumeMessageEvent继承MessageEvent，其表示消息的传输或接收。

3\. CommandThread类

![]()![]()

    
    
        private abstract class CommandThread /*extends Thread*/ {
            PrintWriter pw;
            
            CommandThread(PrintWriter pw) {
                this.pw = pw;
            }
            
            public void start() {
                run();
            }
    
            public void run() {
                try {
                    commandRun();
                } catch (IOException ie) {
                    LOG.error("Error in running command ", ie);
                } finally {
                    cleanupWriterSocket(pw);
                }
            }
            
            public abstract void commandRun() throws IOException;
        }

CommandThread

说明：其与NIOServerCnxn中类似，也是每个子类对应着一个命令，值得注意的是针对每个CMD命令，其仅仅使用一个线程来处理。

2.3 类的属性

![]()![]()

    
    
    public class NettyServerCnxn extends ServerCnxn {
        // 日志
        Logger LOG = LoggerFactory.getLogger(NettyServerCnxn.class);
        
        // 通道
        Channel channel;
        
        // 通道缓存
        ChannelBuffer queuedBuffer;
        
        // 节流与否
        volatile boolean throttled;
        
        // Byte缓冲区
        ByteBuffer bb;
        
        // 四个字节的缓冲区
        ByteBuffer bbLen = ByteBuffer.allocate(4);
        
        // 会话ID
        long sessionId;
        
        // 会话超时时间
        int sessionTimeout;
        
        // 计数
        AtomicLong outstandingCount = new AtomicLong();
    
        /** The ZooKeeperServer for this connection. May be null if the server
         * is not currently serving requests (for example if the server is not
         * an active quorum participant.
         */
        // Zookeeper服务器
        private volatile ZooKeeperServer zkServer;
    
        // NettyServerCnxn工厂
        NettyServerCnxnFactory factory;
        
        // 初始化与否
        boolean initialized;
        
        // 四个字节
        private static final byte[] fourBytes = new byte[4];
        
        private static final String ZK_NOT_SERVING =
            "This ZooKeeper instance is not currently serving requests";
    }

类的属性

说明：NettyServerCnxn维护了与客户端之间的通道缓冲、缓冲区及会话的相关属性。

2.4 类的构造函数

![]()![]()

    
    
        NettyServerCnxn(Channel channel, ZooKeeperServer zks, NettyServerCnxnFactory factory) {
            // 给属性赋值
            this.channel = channel;
            this.zkServer = zks;
            this.factory = factory;
            if (this.factory.login != null) { // 需要登录信息(用户名和密码登录)
                this.zooKeeperSaslServer = new ZooKeeperSaslServer(factory.login);
            }
        }

构造函数

说明：构造函数对NettyServerCnxn中的部分重要属性进行了赋值，其中还涉及到是否需要用户登录。

2.5 核心函数分析

1\. receiveMessage函数

![]()![]()

    
    
        public void receiveMessage(ChannelBuffer message) {
            try {
                while(message.readable() && !throttled) { // 当writerIndex > readerIndex，并且不节流时，满足条件
                    if (bb != null) { // 不为null
                        if (LOG.isTraceEnabled()) {
                            LOG.trace("message readable " + message.readableBytes()
                                    + " bb len " + bb.remaining() + " " + bb);
                            ByteBuffer dat = bb.duplicate();
                            dat.flip();
                            LOG.trace(Long.toHexString(sessionId)
                                    + " bb 0x"
                                    + ChannelBuffers.hexDump(
                                            ChannelBuffers.copiedBuffer(dat)));
                        }
    
                        if (bb.remaining() > message.readableBytes()) { // bb剩余空间大于message中可读字节大小
                            // 确定新的limit
                            int newLimit = bb.position() + message.readableBytes();
                            bb.limit(newLimit);
                        }
                        // 将message写入bb中
                        message.readBytes(bb);
                        // 重置bb的limit
                        bb.limit(bb.capacity());
    
                        if (LOG.isTraceEnabled()) {
                            LOG.trace("after readBytes message readable "
                                    + message.readableBytes()
                                    + " bb len " + bb.remaining() + " " + bb);
                            ByteBuffer dat = bb.duplicate();
                            dat.flip();
                            LOG.trace("after readbytes "
                                    + Long.toHexString(sessionId)
                                    + " bb 0x"
                                    + ChannelBuffers.hexDump(
                                            ChannelBuffers.copiedBuffer(dat)));
                        }
                        if (bb.remaining() == 0) { // 已经读完message，表示内容已经全部接收
                            // 统计接收信息
                            packetReceived();
                            // 翻转，可读
                            bb.flip();
    
                            ZooKeeperServer zks = this.zkServer;
                            if (zks == null) { // Zookeeper服务器为空
                                throw new IOException("ZK down");
                            }
                            if (initialized) { // 未被初始化
                                // 处理bb中包含的包信息
                                zks.processPacket(this, bb);
    
                                if (zks.shouldThrottle(outstandingCount.incrementAndGet())) { // 是否已经节流
                                    // 不接收数据
                                    disableRecvNoWait();
                                }
                            } else { // 已经初始化
                                LOG.debug("got conn req request from "
                                        + getRemoteSocketAddress());
                                // 处理连接请求
                                zks.processConnectRequest(this, bb);
                                initialized = true;
                            }
                            bb = null;
                        }
                    } else { // bb为null
                        if (LOG.isTraceEnabled()) {
                            LOG.trace("message readable "
                                    + message.readableBytes()
                                    + " bblenrem " + bbLen.remaining());
                            // 复制bbLen缓冲
                            ByteBuffer dat = bbLen.duplicate();
                            // 翻转
                            dat.flip();
                            LOG.trace(Long.toHexString(sessionId)
                                    + " bbLen 0x"
                                    + ChannelBuffers.hexDump(
                                            ChannelBuffers.copiedBuffer(dat)));
                        }
    
                        if (message.readableBytes() < bbLen.remaining()) { // bb剩余空间大于message中可读字节大小
                            // 重设bbLen的limit
                            bbLen.limit(bbLen.position() + message.readableBytes());
                        }
                        // 将message内容写入bbLen中
                        message.readBytes(bbLen);
                        // 重置bbLen的limit
                        bbLen.limit(bbLen.capacity());
                        if (bbLen.remaining() == 0) { // 已经读完message，表示内容已经全部接收
                            // 翻转
                            bbLen.flip();
    
                            if (LOG.isTraceEnabled()) {
                                LOG.trace(Long.toHexString(sessionId)
                                        + " bbLen 0x"
                                        + ChannelBuffers.hexDump(
                                                ChannelBuffers.copiedBuffer(bbLen)));
                            }
                            // 读取position后四个字节
                            int len = bbLen.getInt();
                            if (LOG.isTraceEnabled()) {
                                LOG.trace(Long.toHexString(sessionId)
                                        + " bbLen len is " + len);
                            }
                            
                            // 清除缓存
                            bbLen.clear();
                            if (!initialized) { // 未被初始化
                                if (checkFourLetterWord(channel, message, len)) { // 是否是四个字母的命令
                                    return;
                                }
                            }
                            if (len < 0 || len > BinaryInputArchive.maxBuffer) {
                                throw new IOException("Len error " + len);
                            }
                            // 根据len重新分配缓冲，以便接收内容
                            bb = ByteBuffer.allocate(len);
                        }
                    }
                }
            } catch(IOException e) {
                LOG.warn("Closing connection to " + getRemoteSocketAddress(), e);
                close();
            }
        }

receiveMessage

说明：该函数用于接收ChannelBuffer中的数据，函数在while循环体中，当writerIndex大于readerIndex(表示ChannelBuffer中还有可读内容)且throttled为false时执行while循环体，该函数大致可以分为两部分，首先是当bb不为空时，表示已经准备好读取ChannelBuffer中的内容，其流程如下

    
    
                    if (bb != null) { // 不为null，表示已经准备好读取message
                        if (LOG.isTraceEnabled()) {
                            LOG.trace("message readable " + message.readableBytes()
                                    + " bb len " + bb.remaining() + " " + bb);
                            ByteBuffer dat = bb.duplicate();
                            dat.flip();
                            LOG.trace(Long.toHexString(sessionId)
                                    + " bb 0x"
                                    + ChannelBuffers.hexDump(
                                            ChannelBuffers.copiedBuffer(dat)));
                        }
    
                        if (bb.remaining() > message.readableBytes()) { // bb剩余空间大于message中可读字节大小
                            // 确定新的limit
                            int newLimit = bb.position() + message.readableBytes();
                            bb.limit(newLimit);
                        }
                        // 将message写入bb中
                        message.readBytes(bb);
                        // 重置bb的limit
                        bb.limit(bb.capacity());
    
                        if (LOG.isTraceEnabled()) {
                            LOG.trace("after readBytes message readable "
                                    + message.readableBytes()
                                    + " bb len " + bb.remaining() + " " + bb);
                            ByteBuffer dat = bb.duplicate();
                            dat.flip();
                            LOG.trace("after readbytes "
                                    + Long.toHexString(sessionId)
                                    + " bb 0x"
                                    + ChannelBuffers.hexDump(
                                            ChannelBuffers.copiedBuffer(dat)));
                        }
                        if (bb.remaining() == 0) { // 已经读完message，表示内容已经全部接收
                            // 统计接收信息
                            packetReceived();
                            // 翻转，可读
                            bb.flip();
    
                            ZooKeeperServer zks = this.zkServer;
                            if (zks == null) { // Zookeeper服务器为空
                                throw new IOException("ZK down");
                            }
                            if (initialized) { // 未被初始化
                                // 处理bb中包含的包信息
                                zks.processPacket(this, bb);
    
                                if (zks.shouldThrottle(outstandingCount.incrementAndGet())) { // 是否已经节流
                                    // 不接收数据
                                    disableRecvNoWait();
                                }
                            } else { // 已经初始化
                                LOG.debug("got conn req request from "
                                        + getRemoteSocketAddress());
                                // 处理连接请求
                                zks.processConnectRequest(this, bb);
                                initialized = true;
                            }
                            bb = null;
                        }
                    }

其中主要的部分是判断bb的剩余空间是否大于message中的内容，简单而言，就是判断bb是否还有足够空间存储message内容，然后设置bb的limit，之后将message内容读入bb缓冲中，之后再次确定时候已经读完message内容，统计接收信息，再根据是否已经初始化来处理包或者是连接请求，其中的请求内容都存储在bb中。而当bb为空时，其流程如下

    
    
                    else { // bb为null
                        if (LOG.isTraceEnabled()) {
                            LOG.trace("message readable "
                                    + message.readableBytes()
                                    + " bblenrem " + bbLen.remaining());
                            // 复制bbLen缓冲
                            ByteBuffer dat = bbLen.duplicate();
                            // 翻转
                            dat.flip();
                            LOG.trace(Long.toHexString(sessionId)
                                    + " bbLen 0x"
                                    + ChannelBuffers.hexDump(
                                            ChannelBuffers.copiedBuffer(dat)));
                        }
    
                        if (message.readableBytes() < bbLen.remaining()) { // bb剩余空间大于message中可读字节大小
                            // 重设bbLen的limit
                            bbLen.limit(bbLen.position() + message.readableBytes());
                        }
                        // 将message内容写入bbLen中
                        message.readBytes(bbLen);
                        // 重置bbLen的limit
                        bbLen.limit(bbLen.capacity());
                        if (bbLen.remaining() == 0) { // 已经读完message，表示内容已经全部接收
                            // 翻转
                            bbLen.flip();
    
                            if (LOG.isTraceEnabled()) {
                                LOG.trace(Long.toHexString(sessionId)
                                        + " bbLen 0x"
                                        + ChannelBuffers.hexDump(
                                                ChannelBuffers.copiedBuffer(bbLen)));
                            }
                            // 读取position后四个字节
                            int len = bbLen.getInt();
                            if (LOG.isTraceEnabled()) {
                                LOG.trace(Long.toHexString(sessionId)
                                        + " bbLen len is " + len);
                            }
                            
                            // 清除缓存
                            bbLen.clear();
                            if (!initialized) { // 未被初始化
                                if (checkFourLetterWord(channel, message, len)) { // 是否是四个字母的命令
                                    return;
                                }
                            }
                            if (len < 0 || len > BinaryInputArchive.maxBuffer) {
                                throw new IOException("Len error " + len);
                            }
                            // 根据len重新分配缓冲，以便接收内容
                            bb = ByteBuffer.allocate(len);
                        }
                    }

当bb为空时，表示还没有给bb分配足够的内存空间来读取message，首先还是将message内容（后续内容的长度）读入bbLen中，然后再确定读入的内容代表后续真正内容的长度len，然后再根据len来为bb分配存储空间，方便后续读取真正的内容。

2\. sendResponse函数

    
    
        public void sendResponse(ReplyHeader h, Record r, String tag)
                throws IOException {
            if (!channel.isOpen()) {
                return;
            }
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            // Make space for length
            BinaryOutputArchive bos = BinaryOutputArchive.getArchive(baos);
            try {
                // 向baos中写入四个字节(空)
                baos.write(fourBytes);
                // 写入记录
                bos.writeRecord(h, "header");
                if (r != null) { 
                    // 写入记录
                    bos.writeRecord(r, tag);
                }
                // 关闭
                baos.close();
            } catch (IOException e) {
                LOG.error("Error serializing response");
            }
            
            // 转化为Byte Array
            byte b[] = baos.toByteArray();
            // 将Byte Array封装成ByteBuffer
            ByteBuffer bb = ByteBuffer.wrap(b);
            bb.putInt(b.length - 4).rewind();
            // 发送缓冲
            sendBuffer(bb);
            if (h.getXid() > 0) {
                // zks cannot be null otherwise we would not have gotten here!
                if (!zkServer.shouldThrottle(outstandingCount.decrementAndGet())) {
                    enableRecv();
                }
            }
        }

说明：其首先会将header和record都写入baos，之后再将baos转化为ByteBuffer，之后在调用sendBuffer来发送缓冲，而sendBuffer完成的操作是将ByteBuffer写入ChannelBuffer中。

3\. process函数

    
    
        public void process(WatchedEvent event) {
            // 创建响应头
            ReplyHeader h = new ReplyHeader(-1, -1L, 0);
            if (LOG.isTraceEnabled()) {
                ZooTrace.logTraceMessage(LOG, ZooTrace.EVENT_DELIVERY_TRACE_MASK,
                                         "Deliver event " + event + " to 0x"
                                         + Long.toHexString(this.sessionId)
                                         + " through " + this);
            }
    
            // Convert WatchedEvent to a type that can be sent over the wire
            WatcherEvent e = event.getWrapper();
    
            try {
                // 发送响应
                sendResponse(h, e, "notification");
            } catch (IOException e1) {
                if (LOG.isDebugEnabled()) {
                    LOG.debug("Problem sending to " + getRemoteSocketAddress(), e1);
                }
                close();
            }
        }

说明：首先创建ReplyHeader，然后再调用sendResponse来发送响应，最后调用close函数进行后续关闭处理。

**三、总结**

本篇博文讲解了基于Netty完成服务端与客户端之间的通信，其效率相对较高，也谢谢各位园友的观看~

