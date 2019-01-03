**一、前言**

前面分析了FileSnap，接着继续分析FileTxnSnapLog源码，其封装了TxnLog和SnapShot，其在持久化过程中是一个帮助类。

**二、FileTxnSnapLog源码分析**

2.1 类的属性

    
    
    public class FileTxnSnapLog {
        //the direcotry containing the 
        //the transaction logs
        // 日志文件目录
        private final File dataDir;
        //the directory containing the
        //the snapshot directory
        // 快照文件目录
        private final File snapDir;
        // 事务日志
        private TxnLog txnLog;
        // 快照
        private SnapShot snapLog;
        // 版本号
        public final static int VERSION = 2;
        // 版本
        public final static String version = "version-";
    
        // Logger
        private static final Logger LOG = LoggerFactory.getLogger(FileTxnSnapLog.class);
    }

说明：类的属性中包含了TxnLog和SnapShot接口，即对FileTxnSnapLog的很多操作都会转发给TxnLog和SnapLog进行操作，这是一种典型的组合方法。

2.2 内部类

FileTxnSnapLog包含了PlayBackListener内部类，用来接收事务应用过程中的回调，在Zookeeper数据恢复后期，会有事务修正过程，此过程会回调PlayBackListener来进行对应的数据修正。其源码如下

    
    
    public interface PlayBackListener {
        void onTxnLoaded(TxnHeader hdr, Record rec);
    }

说明：在完成事务操作后，会调用到onTxnLoaded方法进行相应的处理。

2.3 构造函数

FileTxnSnapLog的构造函数如下

    
    
        public FileTxnSnapLog(File dataDir, File snapDir) throws IOException {
            LOG.debug("Opening datadir:{} snapDir:{}", dataDir, snapDir);
            // 在datadir和snapdir下生成version-2目录
            this.dataDir = new File(dataDir, version + VERSION);
            this.snapDir = new File(snapDir, version + VERSION);
            if (!this.dataDir.exists()) { // datadir存在但无法创建目录，则抛出异常
                if (!this.dataDir.mkdirs()) {
                    throw new IOException("Unable to create data directory "
                            + this.dataDir);
                }
            }
            if (!this.snapDir.exists()) { // snapdir存在但无法创建目录，则抛出异常
                if (!this.snapDir.mkdirs()) {
                    throw new IOException("Unable to create snap directory "
                            + this.snapDir);
                }
            }
            // 给属性赋值
            txnLog = new FileTxnLog(this.dataDir);
            snapLog = new FileSnap(this.snapDir);
        }

说明：对于构造函数而言，其会在传入的datadir和snapdir目录下新生成version-2的目录，并且会判断目录是否创建成功，之后会创建txnLog和snapLog。

2.4 核心函数分析

1\. restore函数

    
    
        public long restore(DataTree dt, Map<Long, Integer> sessions, 
                PlayBackListener listener) throws IOException {
            // 根据snap文件反序列化dt和sessions
            snapLog.deserialize(dt, sessions);
            // 
            FileTxnLog txnLog = new FileTxnLog(dataDir);
            // 获取比最后处理的zxid+1大的log文件的迭代器
            TxnIterator itr = txnLog.read(dt.lastProcessedZxid+1);
            // 最大的zxid
            long highestZxid = dt.lastProcessedZxid;
            
            TxnHeader hdr;
            try {
                while (true) {
                    // iterator points to 
                    // the first valid txn when initialized
                    // itr在read函数调用后就已经指向第一个合法的事务
                    // 获取事务头
                    hdr = itr.getHeader();
                    if (hdr == null) { // 事务头为空
                        //empty logs 
                        // 表示日志文件为空
                        return dt.lastProcessedZxid;
                    }
                    if (hdr.getZxid() < highestZxid && highestZxid != 0) { // 事务头的zxid小于snapshot中的最大zxid并且其不为0，则会报错
                        LOG.error("{}(higestZxid) > {}(next log) for type {}",
                                new Object[] { highestZxid, hdr.getZxid(),
                                        hdr.getType() });
                    } else { // 重新赋值highestZxid
                        highestZxid = hdr.getZxid();
                    }
                    try {
                        // 在datatree上处理事务
                        processTransaction(hdr,dt,sessions, itr.getTxn());
                    } catch(KeeperException.NoNodeException e) {
                       throw new IOException("Failed to process transaction type: " +
                             hdr.getType() + " error: " + e.getMessage(), e);
                    }
                    // 每处理完一个事务都会进行回调
                    listener.onTxnLoaded(hdr, itr.getTxn());
                    if (!itr.next()) // 已无事务，跳出循环
                        break;
                }
            } finally {
                if (itr != null) { // 迭代器不为空，则关闭
                    itr.close();
                }
            }
            // 返回最高的zxid
            return highestZxid;
        }

说明：restore用于恢复datatree和sessions，其步骤大致如下

① 根据snapshot文件反序列化datatree和sessions，进入②

② 获取比snapshot文件中的zxid+1大的log文件的迭代器，以对log文件中的事务进行迭代，进入③

③ 迭代log文件的每个事务，并且将该事务应用在datatree中，同时会调用onTxnLoaded函数进行后续处理，进入④

④ 关闭迭代器，返回log文件中最后一个事务的zxid（作为最高的zxid）

其中会调用到FileTxnLog的read函数，read函数在FileTxnLog中已经进行过分析，会调用processTransaction函数，其源码如下

    
    
        public void processTransaction(TxnHeader hdr,DataTree dt,
                Map<Long, Integer> sessions, Record txn)
            throws KeeperException.NoNodeException {
            // 事务处理结果
            ProcessTxnResult rc;
            switch (hdr.getType()) { // 确定事务类型
            case OpCode.createSession: // 创建会话
                // 添加进会话
                sessions.put(hdr.getClientId(),
                        ((CreateSessionTxn) txn).getTimeOut());
                if (LOG.isTraceEnabled()) {
                    ZooTrace.logTraceMessage(LOG,ZooTrace.SESSION_TRACE_MASK,
                            "playLog --- create session in log: 0x"
                                    + Long.toHexString(hdr.getClientId())
                                    + " with timeout: "
                                    + ((CreateSessionTxn) txn).getTimeOut());
                }
                // give dataTree a chance to sync its lastProcessedZxid
                // 处理事务
                rc = dt.processTxn(hdr, txn);
                break;
            case OpCode.closeSession: // 关闭会话
                // 会话中移除
                sessions.remove(hdr.getClientId());
                if (LOG.isTraceEnabled()) {
                    ZooTrace.logTraceMessage(LOG,ZooTrace.SESSION_TRACE_MASK,
                            "playLog --- close session in log: 0x"
                                    + Long.toHexString(hdr.getClientId()));
                }
                // 处理事务
                rc = dt.processTxn(hdr, txn);
                break;
            default:
                // 处理事务
                rc = dt.processTxn(hdr, txn);
            }
    
            /**
             * Snapshots are lazily created. So when a snapshot is in progress,
             * there is a chance for later transactions to make into the
             * snapshot. Then when the snapshot is restored, NONODE/NODEEXISTS
             * errors could occur. It should be safe to ignore these.
             */
            if (rc.err != Code.OK.intValue()) { // 忽略处理结果中可能出现的错误
                LOG.debug("Ignoring processTxn failure hdr:" + hdr.getType()
                        + ", error: " + rc.err + ", path: " + rc.path);
            }
        }

说明：processTransaction会根据事务头中记录的事务类型（createSession、closeSession、其他类型）来进行相应的操作，对于createSession类型而言，其会将会话和超时时间添加至会话map中，对于closeSession而言，会话map会根据客户端的id号删除其会话，同时，所有的操作都会调用到dt.processTxn函数，其源码如下

![]()![]()

    
    
        public ProcessTxnResult processTxn(TxnHeader header, Record txn)
        {
            // 事务处理结果
            ProcessTxnResult rc = new ProcessTxnResult();
    
            try {
                // 从事务头中解析出相应属性并保存至rc中
                rc.clientId = header.getClientId();
                rc.cxid = header.getCxid();
                rc.zxid = header.getZxid();
                rc.type = header.getType();
                rc.err = 0;
                rc.multiResult = null;
                switch (header.getType()) { // 确定事务类型
                    case OpCode.create: // 创建结点
                        // 显示转化
                        CreateTxn createTxn = (CreateTxn) txn;
                        // 获取创建结点路径
                        rc.path = createTxn.getPath();
                        // 创建结点
                        createNode(
                                createTxn.getPath(),
                                createTxn.getData(),
                                createTxn.getAcl(),
                                createTxn.getEphemeral() ? header.getClientId() : 0,
                                createTxn.getParentCVersion(),
                                header.getZxid(), header.getTime());
                        break;
                    case OpCode.delete: // 删除结点
                        // 显示转化
                        DeleteTxn deleteTxn = (DeleteTxn) txn;
                        // 获取删除结点路径
                        rc.path = deleteTxn.getPath();
                        // 删除结点
                        deleteNode(deleteTxn.getPath(), header.getZxid());
                        break;
                    case OpCode.setData: // 写入数据
                        // 显示转化
                        SetDataTxn setDataTxn = (SetDataTxn) txn;
                        // 获取写入数据结点路径
                        rc.path = setDataTxn.getPath();
                        // 写入数据
                        rc.stat = setData(setDataTxn.getPath(), setDataTxn
                                .getData(), setDataTxn.getVersion(), header
                                .getZxid(), header.getTime());
                        break;
                    case OpCode.setACL: // 设置ACL
                        // 显示转化
                        SetACLTxn setACLTxn = (SetACLTxn) txn;
                        // 获取路径
                        rc.path = setACLTxn.getPath();
                        // 设置ACL
                        rc.stat = setACL(setACLTxn.getPath(), setACLTxn.getAcl(),
                                setACLTxn.getVersion());
                        break;
                    case OpCode.closeSession: // 关闭会话
                        // 关闭会话
                        killSession(header.getClientId(), header.getZxid());
                        break;
                    case OpCode.error: // 错误
                        // 显示转化
                        ErrorTxn errTxn = (ErrorTxn) txn;
                        // 记录错误
                        rc.err = errTxn.getErr();
                        break;
                    case OpCode.check: // 检查
                        // 显示转化
                        CheckVersionTxn checkTxn = (CheckVersionTxn) txn;
                        // 获取路径
                        rc.path = checkTxn.getPath();
                        break;
                    case OpCode.multi: // 多个事务
                        // 显示转化
                        MultiTxn multiTxn = (MultiTxn) txn ;
                        // 获取事务列表
                        List<Txn> txns = multiTxn.getTxns();
                        rc.multiResult = new ArrayList<ProcessTxnResult>();
                        boolean failed = false;
                        for (Txn subtxn : txns) { // 遍历事务列表
                            if (subtxn.getType() == OpCode.error) {
                                failed = true;
                                break;
                            }
                        }
    
                        boolean post_failed = false;
                        for (Txn subtxn : txns) { // 遍历事务列表，确定每个事务类型并进行相应操作
                            // 处理事务的数据
                            ByteBuffer bb = ByteBuffer.wrap(subtxn.getData());
                            Record record = null;
                            switch (subtxn.getType()) {
                                case OpCode.create:
                                    record = new CreateTxn();
                                    break;
                                case OpCode.delete:
                                    record = new DeleteTxn();
                                    break;
                                case OpCode.setData:
                                    record = new SetDataTxn();
                                    break;
                                case OpCode.error:
                                    record = new ErrorTxn();
                                    post_failed = true;
                                    break;
                                case OpCode.check:
                                    record = new CheckVersionTxn();
                                    break;
                                default:
                                    throw new IOException("Invalid type of op: " + subtxn.getType());
                            }
                            assert(record != null);
                            // 将bytebuffer转化为record(初始化record的相关属性)
                            ByteBufferInputStream.byteBuffer2Record(bb, record);
                           
                            if (failed && subtxn.getType() != OpCode.error){ // 失败并且不为error类型
                                int ec = post_failed ? Code.RUNTIMEINCONSISTENCY.intValue() 
                                                     : Code.OK.intValue();
    
                                subtxn.setType(OpCode.error);
                                record = new ErrorTxn(ec);
                            }
    
                            if (failed) { // 失败
                                assert(subtxn.getType() == OpCode.error) ;
                            }
                            
                            // 生成事务头
                            TxnHeader subHdr = new TxnHeader(header.getClientId(), header.getCxid(),
                                                             header.getZxid(), header.getTime(), 
                                                             subtxn.getType());
                            // 递归调用处理事务
                            ProcessTxnResult subRc = processTxn(subHdr, record);
                            // 保存处理结果
                            rc.multiResult.add(subRc);
                            if (subRc.err != 0 && rc.err == 0) {
                                rc.err = subRc.err ;
                            }
                        }
                        break;
                }
            } catch (KeeperException e) {
                if (LOG.isDebugEnabled()) {
                    LOG.debug("Failed: " + header + ":" + txn, e);
                }
                rc.err = e.code().intValue();
            } catch (IOException e) {
                if (LOG.isDebugEnabled()) {
                    LOG.debug("Failed: " + header + ":" + txn, e);
                }
            }
            /*
             * A snapshot might be in progress while we are modifying the data
             * tree. If we set lastProcessedZxid prior to making corresponding
             * change to the tree, then the zxid associated with the snapshot
             * file will be ahead of its contents. Thus, while restoring from
             * the snapshot, the restore method will not apply the transaction
             * for zxid associated with the snapshot file, since the restore
             * method assumes that transaction to be present in the snapshot.
             *
             * To avoid this, we first apply the transaction and then modify
             * lastProcessedZxid.  During restore, we correctly handle the
             * case where the snapshot contains data ahead of the zxid associated
             * with the file.
             */
            // 事务处理结果中保存的zxid大于已经被处理的最大的zxid，则重新赋值
            if (rc.zxid > lastProcessedZxid) {
                lastProcessedZxid = rc.zxid;
            }
    
            /*
             * Snapshots are taken lazily. It can happen that the child
             * znodes of a parent are created after the parent
             * is serialized. Therefore, while replaying logs during restore, a
             * create might fail because the node was already
             * created.
             *
             * After seeing this failure, we should increment
             * the cversion of the parent znode since the parent was serialized
             * before its children.
             *
             * Note, such failures on DT should be seen only during
             * restore.
             */
            if (header.getType() == OpCode.create &&
                    rc.err == Code.NODEEXISTS.intValue()) { // 处理在恢复数据过程中的结点创建操作
                LOG.debug("Adjusting parent cversion for Txn: " + header.getType() +
                        " path:" + rc.path + " err: " + rc.err);
                int lastSlash = rc.path.lastIndexOf("/");
                String parentName = rc.path.substring(0, lastSlash);
                CreateTxn cTxn = (CreateTxn)txn;
                try {
                    setCversionPzxid(parentName, cTxn.getParentCVersion(),
                            header.getZxid());
                } catch (KeeperException.NoNodeException e) {
                    LOG.error("Failed to set parent cversion for: " +
                          parentName, e);
                    rc.err = e.code().intValue();
                }
            } else if (rc.err != Code.OK.intValue()) {
                LOG.debug("Ignoring processTxn failure hdr: " + header.getType() +
                      " : error: " + rc.err);
            }
            return rc;
        }

View Code

说明：processTxn用于处理事务，即将事务操作应用到DataTree内存数据库中，以恢复成最新的数据。

2\. save函数

    
    
        public void save(DataTree dataTree,
                ConcurrentHashMap<Long, Integer> sessionsWithTimeouts)
            throws IOException {
            // 获取最后处理的zxid
            long lastZxid = dataTree.lastProcessedZxid;
            // 生成snapshot文件
            File snapshotFile = new File(snapDir, Util.makeSnapshotName(lastZxid));
            LOG.info("Snapshotting: 0x{} to {}", Long.toHexString(lastZxid),
                    snapshotFile);
            // 序列化datatree、sessionsWithTimeouts至snapshot文件
            snapLog.serialize(dataTree, sessionsWithTimeouts, snapshotFile);
            
        }

说明：save函数用于将sessions和datatree保存至snapshot文件中，其大致步骤如下

① 获取内存数据库中已经处理的最新的zxid，进入②

② 根据zxid和快照目录生成snapshot文件，进入③

③ 将datatree（内存数据库）、sessionsWithTimeouts序列化至快照文件。

其他的函数或多或少都是调用TxnLog和SnapLog中的相应函数，之前已经进行过分析，这里不再累赘。

**三、总结**

本篇博文分析了FileTxnSnapLog的源码，其主要封装了TxnLog和SnapLog来进行相应的处理，其提供了从snapshot文件和log文件中恢复内存数据库的接口，源码相对而言较为简单，也谢谢各位园友的观看~

