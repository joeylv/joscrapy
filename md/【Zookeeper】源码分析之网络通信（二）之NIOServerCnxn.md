**一、前言**

前面介绍了ServerCnxn，下面开始学习NIOServerCnxn。

**二、NIOServerCnxn源码分析**

2.1 类的继承关系

    
    
    public class NIOServerCnxn extends ServerCnxn {}

说明：NIOServerCnxn继承了ServerCnxn抽象类，使用NIO来处理与客户端之间的通信，使用单线程处理。

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
                    sendBufferSync(ByteBuffer.wrap(sb.toString().getBytes()));
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

说明：该类用来将给客户端的响应进行分块，其核心方法是checkFlush方法，其源码如下

    
    
            private void checkFlush(boolean force) {
                if ((force && sb.length() > 0) || sb.length() > 2048) { // 当强制发送并且sb大小大于0，或者sb大小大于2048即发送缓存
                    sendBufferSync(ByteBuffer.wrap(sb.toString().getBytes()));
                    // clear our internal buffer
                    sb.setLength(0);
                }
            }

说明：当需要强制发送时，sb缓冲中只要有内容就会同步发送，或者是当sb的大小超过2048（块）时就需要发送，其会调用NIOServerCnxn的sendBufferSync方法，该之后会进行分析，然后再清空sb缓冲。

2\. CommandThread类

![]()![]()

    
    
        private abstract class CommandThread extends Thread {
            PrintWriter pw;
            
            CommandThread(PrintWriter pw) {
                this.pw = pw;
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

说明：该类用于处理ServerCnxn中的定义的命令，其主要逻辑定义在commandRun方法中，在子类中各自实现，这是一种典型的工厂方法，每个子类对应着一个命令，每个命令使用单独的线程进行处理。

2.3 类的属性

![]()![]()

    
    
    public class NIOServerCnxn extends ServerCnxn {
        // 日志
        static final Logger LOG = LoggerFactory.getLogger(NIOServerCnxn.class);
    
        // ServerCnxn工厂
        NIOServerCnxnFactory factory;
    
        // 针对面向流的连接套接字的可选择通道
        final SocketChannel sock;
    
        // 表示 SelectableChannel 在 Selector 中注册的标记
        private final SelectionKey sk;
    
        // 初始化标志
        boolean initialized;
    
        // 分配四个字节缓冲区
        ByteBuffer lenBuffer = ByteBuffer.allocate(4);
    
        // 赋值incomingBuffer
        ByteBuffer incomingBuffer = lenBuffer;
    
        // 缓冲队列
        LinkedBlockingQueue<ByteBuffer> outgoingBuffers = new LinkedBlockingQueue<ByteBuffer>();
    
        // 会话超时时间
        int sessionTimeout;
    
        // ZooKeeper服务器
        private final ZooKeeperServer zkServer;
    
        /**
         * The number of requests that have been submitted but not yet responded to.
         */
        // 已经被提交但还未响应的请求数量
        int outstandingRequests;
    
        /**
         * This is the id that uniquely identifies the session of a client. Once
         * this session is no longer active, the ephemeral nodes will go away.
         */
        // 会话ID
        long sessionId;
    
        // 下个会话ID
        static long nextSessionId = 1;
        int outstandingLimit = 1;
        
        private static final String ZK_NOT_SERVING =
            "This ZooKeeper instance is not currently serving requests";
        
        private final static byte fourBytes[] = new byte[4];
    }    

类的属性

说明：NIOServerCnxn维护了服务器与客户端之间的Socket通道、用于存储传输内容的缓冲区、会话ID、ZooKeeper服务器等。

2.4 类的构造函数

![]()![]()

    
    
        public NIOServerCnxn(ZooKeeperServer zk, SocketChannel sock,
                SelectionKey sk, NIOServerCnxnFactory factory) throws IOException {
            this.zkServer = zk;
            this.sock = sock;
            this.sk = sk;
            this.factory = factory;
            if (this.factory.login != null) {
                this.zooKeeperSaslServer = new ZooKeeperSaslServer(factory.login);
            }
            if (zk != null) { 
                outstandingLimit = zk.getGlobalOutstandingLimit();
            }
            sock.socket().setTcpNoDelay(true);
            /* set socket linger to false, so that socket close does not
             * block */
            // 设置linger为false，以便在socket关闭时不会阻塞
            sock.socket().setSoLinger(false, -1);
            // 获取IP地址
            InetAddress addr = ((InetSocketAddress) sock.socket()
                    .getRemoteSocketAddress()).getAddress();
            // 认证信息中添加IP地址
            authInfo.add(new Id("ip", addr.getHostAddress()));
            // 设置感兴趣的操作类型
            sk.interestOps(SelectionKey.OP_READ);
        }

构造函数

说明：在构造函数中会对Socket通道进行相应设置，如设置TCP连接无延迟、获取客户端的IP地址并将此信息进行记录，方便后续认证，最后设置SelectionKey感兴趣的操作类型为READ。

2.5 核心函数分析

1\. sendBuffer函数

![]()![]()

    
    
        public void sendBuffer(ByteBuffer bb) {
            try {
                if (bb != ServerCnxnFactory.closeConn) { // 不关闭连接
                    // We check if write interest here because if it is NOT set,
                    // nothing is queued, so we can try to send the buffer right
                    // away without waking up the selector
                    // 首先检查interestOps中是否存在WRITE操作，如果没有
                    // 则表示直接发送缓冲而不必先唤醒selector
                    if ((sk.interestOps() & SelectionKey.OP_WRITE) == 0) { // 不为write操作
                        try {
                            // 将缓冲写入socket
                            sock.write(bb);
                        } catch (IOException e) {
                            // we are just doing best effort right now
                        }
                    }
                    // if there is nothing left to send, we are done
                    if (bb.remaining() == 0) { // bb中的内容已经被全部读取
                        // 统计发送包信息（调用ServerCnxn方法）
                        packetSent();
                        return;
                    }
                }
    
                synchronized(this.factory){ // 同步块
                    // Causes the first selection operation that has not yet returned to return immediately
                    // 让第一个还没返回（阻塞）的selection操作马上返回结果
                    sk.selector().wakeup();
                    if (LOG.isTraceEnabled()) {
                        LOG.trace("Add a buffer to outgoingBuffers, sk " + sk
                                + " is valid: " + sk.isValid());
                    }
                    // 将缓存添加至队列
                    outgoingBuffers.add(bb);
                    if (sk.isValid()) { // key是否合法
                        // 将写操作添加至感兴趣的集合
                        sk.interestOps(sk.interestOps() | SelectionKey.OP_WRITE);
                    }
                }
                
            } catch(Exception e) {
                LOG.error("Unexpected Exception: ", e);
            }
        }

sendBuffer

说明：该函数将缓冲写入socket中，其大致处理可以分为两部分，首先会判断ByteBuffer是否为关闭连接的信号，并且当感兴趣的集合中没有写操作时，其会立刻将缓存写入socket，步骤如下

    
    
                if (bb != ServerCnxnFactory.closeConn) { // 不关闭连接
                    // We check if write interest here because if it is NOT set,
                    // nothing is queued, so we can try to send the buffer right
                    // away without waking up the selector
                    // 首先检查interestOps中是否存在WRITE操作，如果没有
                    // 则表示直接发送缓冲而不必先唤醒selector
                    if ((sk.interestOps() & SelectionKey.OP_WRITE) == 0) { // 不为write操作
                        try {
                            // 将缓冲写入socket
                            sock.write(bb);
                        } catch (IOException e) {
                            // we are just doing best effort right now
                        }
                    }
                    // if there is nothing left to send, we are done
                    if (bb.remaining() == 0) { // bb中的内容已经被全部读取
                        // 统计发送包信息（调用ServerCnxn方法）
                        packetSent();
                        return;
                    }
                }

当缓冲区被正常的写入到socket后，会直接返回，然而，当原本就对写操作感兴趣时，其会走如下流程

    
    
                synchronized(this.factory){ // 同步块
                    // Causes the first selection operation that has not yet returned to return immediately
                    // 让第一个还没返回（阻塞）的selection操作马上返回结果
                    sk.selector().wakeup();
                    if (LOG.isTraceEnabled()) {
                        LOG.trace("Add a buffer to outgoingBuffers, sk " + sk
                                + " is valid: " + sk.isValid());
                    }
                    // 将缓存添加至队列
                    outgoingBuffers.add(bb);
                    if (sk.isValid()) { // key是否合法
                        // 将写操作添加至感兴趣的集合
                        sk.interestOps(sk.interestOps() | SelectionKey.OP_WRITE);
                    }
                }

首先会唤醒上个被阻塞的selection操作，然后将缓冲添加至outgoingBuffers队列中，后续再进行发送。

2\. doIO函数

![]()![]()

    
    
        void doIO(SelectionKey k) throws InterruptedException {
            try {
                if (isSocketOpen() == false) { // socket未开启
                    LOG.warn("trying to do i/o on a null socket for session:0x"
                             + Long.toHexString(sessionId));
    
                    return;
                }
                if (k.isReadable()) { // key可读
                    // 将内容从socket写入incoming缓冲
                    int rc = sock.read(incomingBuffer);
                    if (rc < 0) { // 流结束异常，无法从客户端读取数据
                        throw new EndOfStreamException(
                                "Unable to read additional data from client sessionid 0x"
                                + Long.toHexString(sessionId)
                                + ", likely client has closed socket");
                    }
                    if (incomingBuffer.remaining() == 0) { // 缓冲区已经写满
                        boolean isPayload;
                        // 读取下个请求
                        if (incomingBuffer == lenBuffer) { // start of next request
                            // 翻转缓冲区，可读
                            incomingBuffer.flip();
                            // 读取lenBuffer的前四个字节，当读取的是内容长度时则为true，否则为false
                            isPayload = readLength(k);
                            // 清除缓冲
                            incomingBuffer.clear();
                        } else { // 不等，因为在readLength中根据Len已经重新分配了incomingBuffer
                            // continuation
                            isPayload = true;
                        }
                        if (isPayload) { // 不为四个字母，为实际内容    // not the case for 4letterword
                            // 读取内容
                            readPayload();
                        }
                        else { // 四个字母，为四字母的命令
                            // four letter words take care
                            // need not do anything else
                            return;
                        }
                    }
                }
                if (k.isWritable()) { // key可写
                    // ZooLog.logTraceMessage(LOG,
                    // ZooLog.CLIENT_DATA_PACKET_TRACE_MASK
                    // "outgoingBuffers.size() = " +
                    // outgoingBuffers.size());
                    if (outgoingBuffers.size() > 0) {
                        // ZooLog.logTraceMessage(LOG,
                        // ZooLog.CLIENT_DATA_PACKET_TRACE_MASK,
                        // "sk " + k + " is valid: " +
                        // k.isValid());
    
                        /*
                         * This is going to reset the buffer position to 0 and the
                         * limit to the size of the buffer, so that we can fill it
                         * with data from the non-direct buffers that we need to
                         * send.
                         */
                        // 分配的直接缓冲
                        ByteBuffer directBuffer = factory.directBuffer;
                        // 清除缓冲
                        directBuffer.clear();
    
                        for (ByteBuffer b : outgoingBuffers) { // 遍历
                            if (directBuffer.remaining() < b.remaining()) { // directBuffer的剩余空闲长度小于b的剩余空闲长度
                                /*
                                 * When we call put later, if the directBuffer is to
                                 * small to hold everything, nothing will be copied,
                                 * so we"ve got to slice the buffer if it"s too big.
                                 */
                                // 缩小缓冲至directBuffer的大小
                                b = (ByteBuffer) b.slice().limit(
                                        directBuffer.remaining());
                            }
                            /*
                             * put() is going to modify the positions of both
                             * buffers, put we don"t want to change the position of
                             * the source buffers (we"ll do that after the send, if
                             * needed), so we save and reset the position after the
                             * copy
                             */
                            // 记录b的当前position
                            int p = b.position();
                            // 将b写入directBuffer
                            directBuffer.put(b);
                            // 设置回b的原来的position
                            b.position(p);
                            if (directBuffer.remaining() == 0) { // 已经写满
                                break;
                            }
                        }
                        /*
                         * Do the flip: limit becomes position, position gets set to
                         * 0. This sets us up for the write.
                         */
                        // 翻转缓冲区，可读
                        directBuffer.flip();
    
                        // 将directBuffer的内容写入socket
                        int sent = sock.write(directBuffer);
                        ByteBuffer bb;
    
                        // Remove the buffers that we have sent
                        while (outgoingBuffers.size() > 0) { // outgoingBuffers中还存在Buffer
                            // 取队首元素，但并不移出
                            bb = outgoingBuffers.peek();
                            if (bb == ServerCnxnFactory.closeConn) { // 关闭连接，抛出异常
                                throw new CloseRequestException("close requested");
                            }
                            
                            // bb还剩余多少元素没有被发送
                            int left = bb.remaining() - sent;
                            if (left > 0) { // 存在元素未被发送
                                /*
                                 * We only partially sent this buffer, so we update
                                 * the position and exit the loop.
                                 */
                                // 更新bb的position
                                bb.position(bb.position() + sent);
                                break;
                            }
                            // 发送包，调用ServerCnxn方法
                            packetSent();
                            /* We"ve sent the whole buffer, so drop the buffer */
                            // 已经发送完buffer的所有内容，移除buffer
                            sent -= bb.remaining();
                            outgoingBuffers.remove();
                        }
                        // ZooLog.logTraceMessage(LOG,
                        // ZooLog.CLIENT_DATA_PACKET_TRACE_MASK, "after send,
                        // outgoingBuffers.size() = " + outgoingBuffers.size());
                    }
    
                    synchronized(this.factory){ // 同步块
                        if (outgoingBuffers.size() == 0) { // outgoingBuffers不存在buffer
                            if (!initialized
                                    && (sk.interestOps() & SelectionKey.OP_READ) == 0) { // 未初始化并且无读请求
                                throw new CloseRequestException("responded to info probe");
                            }
                            // 重置感兴趣的集合
                            sk.interestOps(sk.interestOps()
                                    & (~SelectionKey.OP_WRITE));
                        } else { // 重置感兴趣的集合
                            sk.interestOps(sk.interestOps()
                                    | SelectionKey.OP_WRITE);
                        }
                    }
                }
            } catch (CancelledKeyException e) {
                LOG.warn("Exception causing close of session 0x"
                        + Long.toHexString(sessionId)
                        + " due to " + e);
                if (LOG.isDebugEnabled()) {
                    LOG.debug("CancelledKeyException stack trace", e);
                }
                close();
            } catch (CloseRequestException e) {
                // expecting close to log session closure
                close();
            } catch (EndOfStreamException e) {
                LOG.warn("caught end of stream exception",e); // tell user why
    
                // expecting close to log session closure
                close();
            } catch (IOException e) {
                LOG.warn("Exception causing close of session 0x"
                        + Long.toHexString(sessionId)
                        + " due to " + e);
                if (LOG.isDebugEnabled()) {
                    LOG.debug("IOException stack trace", e);
                }
                close();
            }
        }

doIO

说明：该函数主要是进行IO处理，当传入的SelectionKey是可读时，其处理流程如下

    
    
                if (k.isReadable()) { // key可读
                    // 将内容从socket写入incoming缓冲
                    int rc = sock.read(incomingBuffer);
                    if (rc < 0) { // 流结束异常，无法从客户端读取数据
                        throw new EndOfStreamException(
                                "Unable to read additional data from client sessionid 0x"
                                + Long.toHexString(sessionId)
                                + ", likely client has closed socket");
                    }
                    if (incomingBuffer.remaining() == 0) { // 缓冲区已经写满
                        boolean isPayload;
                        // 读取下个请求
                        if (incomingBuffer == lenBuffer) { // start of next request
                            // 翻转缓冲区，可读
                            incomingBuffer.flip();
                            // 读取lenBuffer的前四个字节，当读取的是内容长度时则为true，否则为false
                            isPayload = readLength(k);
                            // 清除缓冲
                            incomingBuffer.clear();
                        } else { // 不等，因为在readLength中根据Len已经重新分配了incomingBuffer
                            // continuation
                            isPayload = true;
                        }
                        if (isPayload) { // 不为四个字母，为实际内容    // not the case for 4letterword
                            // 读取内容
                            readPayload();
                        }
                        else { // 四个字母，为四字母的命令
                            // four letter words take care
                            // need not do anything else
                            return;
                        }
                    }
                }

说明：首先从socket中将数据读入incomingBuffer中，再判断incomingBuffer是否与lenBuffer相等，若相等，则表示读取的是一个四个字母的命令，否则表示读取的是具体内容的长度，因为在readLength函数会根据socket中内容的长度重新分配incomingBuffer。其中，readLength函数的源码如下

    
    
        private boolean readLength(SelectionKey k) throws IOException {
            // Read the length, now get the buffer
            // 读取position之后的四个字节
            int len = lenBuffer.getInt();
            if (!initialized && checkFourLetterWord(sk, len)) { // 未初始化并且是四个字母组成的命令
                return false;
            }
            if (len < 0 || len > BinaryInputArchive.maxBuffer) {
                throw new IOException("Len error " + len);
            }
            if (zkServer == null) {
                throw new IOException("ZooKeeperServer not running");
            }
            // 重新分配len长度的缓冲
            incomingBuffer = ByteBuffer.allocate(len);
            return true;
        }

说明：首先会读取lenBuffer缓冲的position之后的四个字节，然后判断其是否是四字母的命令或者是长整形（具体内容的长度），之后再根据长度重新分配incomingBuffer大小。

同时，在调用完readLength后，会知道是否为内容，若为内容，则会调用readPayload函数来读取内容，其源码如下

    
    
        private void readPayload() throws IOException, InterruptedException {
            // 表示还未读取完socket中内容
            if (incomingBuffer.remaining() != 0) { // have we read length bytes?
                // 将socket的内容读入缓冲
                int rc = sock.read(incomingBuffer); // sock is non-blocking, so ok
                if (rc < 0) { // 流结束异常，无法从客户端读取数据
                    throw new EndOfStreamException(
                            "Unable to read additional data from client sessionid 0x"
                            + Long.toHexString(sessionId)
                            + ", likely client has closed socket");
                }
            }
            
            // 表示已经读取完了Socket中内容
            if (incomingBuffer.remaining() == 0) { // have we read length bytes?
                // 接收到packet
                packetReceived();
                // 翻转缓冲区
                incomingBuffer.flip();
                if (!initialized) { // 未初始化
                    // 读取连接请求
                    readConnectRequest();
                } else {
                    // 读取请求
                    readRequest();
                }
                // 清除缓冲
                lenBuffer.clear();
                // 赋值incomingBuffer，即清除incoming缓冲
                incomingBuffer = lenBuffer;
            }
        }

说明：首先会将socket中的实际内容写入incomingBuffer中（已经重新分配大小），当读取完成后，则更新接收的包统计信息，之后再根据是否初始化了还确定读取连接请求还是直接请求，最后会清除缓存，并重新让incomingBuffer与lenBuffer相等，表示该读取过程结束。

而当doIO中的key为可写时，其处理流程如下

    
    
                if (k.isWritable()) { // key可写
                    // ZooLog.logTraceMessage(LOG,
                    // ZooLog.CLIENT_DATA_PACKET_TRACE_MASK
                    // "outgoingBuffers.size() = " +
                    // outgoingBuffers.size());
                    if (outgoingBuffers.size() > 0) {
                        // ZooLog.logTraceMessage(LOG,
                        // ZooLog.CLIENT_DATA_PACKET_TRACE_MASK,
                        // "sk " + k + " is valid: " +
                        // k.isValid());
    
                        /*
                         * This is going to reset the buffer position to 0 and the
                         * limit to the size of the buffer, so that we can fill it
                         * with data from the non-direct buffers that we need to
                         * send.
                         */
                        // 分配的直接缓冲
                        ByteBuffer directBuffer = factory.directBuffer;
                        // 清除缓冲
                        directBuffer.clear();
    
                        for (ByteBuffer b : outgoingBuffers) { // 遍历
                            if (directBuffer.remaining() < b.remaining()) { // directBuffer的剩余空闲长度小于b的剩余空闲长度
                                /*
                                 * When we call put later, if the directBuffer is to
                                 * small to hold everything, nothing will be copied,
                                 * so we"ve got to slice the buffer if it"s too big.
                                 */
                                // 缩小缓冲至directBuffer的大小
                                b = (ByteBuffer) b.slice().limit(
                                        directBuffer.remaining());
                            }
                            /*
                             * put() is going to modify the positions of both
                             * buffers, put we don"t want to change the position of
                             * the source buffers (we"ll do that after the send, if
                             * needed), so we save and reset the position after the
                             * copy
                             */
                            // 记录b的当前position
                            int p = b.position();
                            // 将b写入directBuffer
                            directBuffer.put(b);
                            // 设置回b的原来的position
                            b.position(p);
                            if (directBuffer.remaining() == 0) { // 已经写满
                                break;
                            }
                        }
                        /*
                         * Do the flip: limit becomes position, position gets set to
                         * 0. This sets us up for the write.
                         */
                        // 翻转缓冲区，可读
                        directBuffer.flip();
    
                        // 将directBuffer的内容写入socket
                        int sent = sock.write(directBuffer);
                        ByteBuffer bb;
    
                        // Remove the buffers that we have sent
                        while (outgoingBuffers.size() > 0) { // outgoingBuffers中还存在Buffer
                            // 取队首元素，但并不移出
                            bb = outgoingBuffers.peek();
                            if (bb == ServerCnxnFactory.closeConn) { // 关闭连接，抛出异常
                                throw new CloseRequestException("close requested");
                            }
                            
                            // bb还剩余多少元素没有被发送
                            int left = bb.remaining() - sent;
                            if (left > 0) { // 存在元素未被发送
                                /*
                                 * We only partially sent this buffer, so we update
                                 * the position and exit the loop.
                                 */
                                // 更新bb的position
                                bb.position(bb.position() + sent);
                                break;
                            }
                            // 发送包，调用ServerCnxn方法
                            packetSent();
                            /* We"ve sent the whole buffer, so drop the buffer */
                            // 已经发送完buffer的所有内容，移除buffer
                            sent -= bb.remaining();
                            outgoingBuffers.remove();
                        }
                        // ZooLog.logTraceMessage(LOG,
                        // ZooLog.CLIENT_DATA_PACKET_TRACE_MASK, "after send,
                        // outgoingBuffers.size() = " + outgoingBuffers.size());
                    }

说明：其首先会判断outgoingBuffers中是否还有Buffer未发送，然后遍历Buffer，为提供IO效率，借助了directBuffer（64K大小），之后每次以directBuffer的大小(64K)来将缓冲的内容写入socket中发送，直至全部发送完成。

**三、总结**

本篇讲解了NIOServerCnxn的处理细节，其主要依托于Java的NIO相关接口来完成IO操作，也谢谢各位园友的观看~

