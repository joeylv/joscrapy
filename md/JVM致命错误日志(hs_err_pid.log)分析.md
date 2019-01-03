  * 1 日志头文件
  * 2 导致 crash 的线程信息
  * 3 线程信息
  * 4 安全点和锁信息
  * 5 堆信息
  * 6 本地代码缓存
  * 7 编译事件
  * 8 gc 日志
  * 9 jvm 内存映射
  * 10 jvm 启动参数
  * 11 参考资料

最近两天测试环境有一个服务总是会挂（两到三天一次），JVM虚拟机总是会崩溃。所以有必要了解JVM崩溃的原因是什么。

当JVM发生致命错误导致崩溃时，会生成一个hs_err_pid_xxx.log这样的文件，该文件包含了导致 JVM crash
的重要信息，我们可以通过分析该文件定位到导致 JVM Crash 的原因，从而修复保证系统稳定。

默认情况下，该文件是生成在工作目录下的，当然也可以通过 JVM 参数指定生成路径：

    
    
    -XX:ErrorFile=/var/log/hs_err_pid<pid>.log
    

这个文件主要包含如下内容：

  * 日志头文件
  * 导致 crash 的线程信息
  * 所有线程信息
  * 安全点和锁信息
  * 堆信息
  * 本地代码缓存
  * 编译事件
  * gc 相关记录
  * jvm 内存映射
  * jvm 启动参数
  * 服务器信息

下面就根据这个文件内容逐步解析。

## 日志头文件

内容如下

    
    
    #
    # A fatal error has been detected by the Java Runtime Environment:
    #
    #  SIGSEGV (0xb) at pc=0x0000003797807a91, pid=29071, tid=139901421901568
    #
    # JRE version: Java(TM) SE Runtime Environment (8.0_45-b14) (build 1.8.0_45-b14)
    # Java VM: Java HotSpot(TM) 64-Bit Server VM (25.45-b02 mixed mode linux-amd64 compressed oops)
    # Problematic frame:
    # C  [libresolv.so.2+0x7a91]  __libc_res_nquery+0x1c1
    #
    # Failed to write core dump. Core dumps have been disabled. To enable core dumping, try "ulimit -c unlimited" before starting Java again
    #
    # If you would like to submit a bug report, please visit:
    #   http://bugreport.java.com/bugreport/crash.jsp
    # The crash happened outside the Java Virtual Machine in native code.
    # See problematic frame for where to report the bug.
    #
    

这段内容主要简述了导致 JVM Crash 的原因。常见的原因有 JVM 自身的 bug，应用程序错误，JVM 参数，服务器资源不足，JNI
调用错误等。当然还有一些版本和配置信息，

    
    
    SIGSEGV (0xb) at pc=0x0000003797807a91, pid=29071, tid=139901421901568
    

非预期的错误被 JRE 检测到了，其中

  * SIGSEGV ：信号量
  * 0xb ：信号码
  * pc=0x0000003797807a91 ：程序计数器的值
  * pid=29071 ：进程号
  * tid=139901421901568 ：线程号

SIGSEGV(0xb) 表示 JVM Crash 时正在执行 JNI
代码，常见的描述还有`EXCEPTION_ACCESS_VIOLATION`，该描述表示 JVM Crash 时正在执行 JVM 自身的代码，这往往是因为
JVM 的 Bug 导致的
Crash；另一种常见的描述是`EXCEPTION_STACK_OVERFLOW`，该描述表示这是个栈溢出导致的错误，这往往是应用程序中存在深层递归导致的。

    
    
    # JRE version: Java(TM) SE Runtime Environment (8.0_45-b14) (build 1.8.0_45-b14)
    # Java VM: Java HotSpot(TM) 64-Bit Server VM (25.45-b02 mixed mode linux-amd64 compressed oops)
    

JRE 和 JVM 的版本信息

    
    
    # Problematic frame:
    # C  [libresolv.so.2+0x7a91]  __libc_res_nquery+0x1c1
    

这个信息比较重要，问题帧信息：

**C** 表示帧类型为本地帧，还有其他类型：

  * j ： 解释的Java帧
  * V : 虚拟机帧
  * v ：虚拟机生成的存根栈帧
  * J：其他帧类型，包括编译后的Java帧

`[libresolv.so.2+0x7a91]
__libc_res_nquery+0x1c1`和程序计数器（pc）表达的含义一样，但是用的是本地so库+偏移量的方式。

## 导致 crash 的线程信息

内容如下：

    
    
    ---------------  T H R E A D  ---------------
    
    Current thread (0x0000000001e94800):  JavaThread "pool-1-thread-2" [_thread_in_native, id=30111, stack(0x00007f3d567e5000,0x00007f3d568e6000)]
    
    siginfo: si_signo: 11 (SIGSEGV), si_code: 1 (SEGV_MAPERR), si_addr: 0x0000000000000003
    
    Registers:
    RAX=0x0000000000000000, RBX=0x0000000000000000, RCX=0x0000000000000000, RDX=0x0000000000000050
    RSP=0x00007f3d568e2280, RBP=0x00007f3d568e2570, RSI=0x0000000000000000, RDI=0x00000000ffffffff
    R8 =0x0000000000000000, R9 =0x0000000000000000, R10=0x000000000007a337, R11=0x0000000000000213
    R12=0x00007f3d568e2ef0, R13=0x00007f3d568e22b0, R14=0x0000000000000000, R15=0x00007f3d568e5db8
    RIP=0x0000003797807a91, EFLAGS=0x0000000000010246, CSGSFS=0x0000000000000033, ERR=0x0000000000000004
      TRAPNO=0x000000000000000e
    
    Top of Stack: (sp=0x00007f3d568e2280)
    0x00007f3d568e2280:   b8e4bfb900000800 00007f3d568e3760
    0x00007f3d568e2290:   00007f3d568e3758 00007f3d568e377c
    0x00007f3d568e22a0:   00007f3d568e3778 6f6e6b6e56a88a58
    0x00007f3d568e22b0:   00000100000149a0 7a68710800000000
    0x00007f3d568e22c0:   6970067363642d78 6d6f63036e61676e
    ....省略
    
    Instructions: (pc=0x0000003797807a91)
    0x0000003797807a71:   48 89 45 b8 48 8b 4d b8 0f b6 51 03 89 d3 83 e3
    0x0000003797807a81:   0f 75 0d 0f b7 49 06 66 c1 c9 08 66 85 c9 75 4f
    0x0000003797807a91:   0f b6 48 03 bf 0f 00 00 00 40 20 cf 75 0d 0f b7
    0x0000003797807aa1:   70 06 66 c1 ce 08 66 85 f6 75 34 83 e1 0f 83 e2 
    
    Register to memory mapping:
    
    RAX=0x0000000000000000 is an unknown value
    RBX=0x0000000000000000 is an unknown value
    RCX=0x0000000000000000 is an unknown value
    RDX=0x0000000000000050 is an unknown value
    RSP=0x00007f3d568e2280 is pointing into the stack for thread: 0x0000000001e94800
    RBP=0x00007f3d568e2570 is pointing into the stack for thread: 0x0000000001e94800
    ... 省略
    
    
    Stack: [0x00007f3d567e5000,0x00007f3d568e6000],  sp=0x00007f3d568e2280,  free space=1012k
    Native frames: (J=compiled Java code, j=interpreted, Vv=VM code, C=native code)
    C  [libresolv.so.2+0x7a91]  __libc_res_nquery+0x1c1
    C  [libresolv.so.2+0x7fd1]
    
    Java frames: (J=compiled Java code, j=interpreted, Vv=VM code)
    J 15056  java.net.Inet6AddressImpl.lookupAllHostAddr(Ljava/lang/String;)[Ljava/net/InetAddress; (0 bytes) @ 0x00007f3d7492af8c [0x00007f3d7492af40+0x4c]
    J 14966 C1 java.net.InetAddress.getAddressesFromNameService(Ljava/lang/String;Ljava/net/InetAddress;)[Ljava/net/InetAddress; (245 bytes) @ 0x00007f3d75466754 [0x00007f3d754662c0+0x494]
    J 14291 C2 java.net.InetAddress.getAllByName(Ljava/lang/String;Ljava/net/InetAddress;)[Ljava/net/InetAddress; (387 bytes) @ 0x00007f3d7534b718 [0x00007f3d7534ae20+0x8f8]
    J 14178 C1 java.net.InetSocketAddress.<init>(Ljava/lang/String;I)V (47 bytes) @ 0x00007f3d752ce0f4 [0x00007f3d752cdec0+0x234]
    j  sun.security.ssl.SSLSocketImpl.<init>(Lsun/security/ssl/SSLContextImpl;Ljava/lang/String;ILjava/net/InetAddress;I)V+144
    j  sun.security.ssl.SSLSocketFactoryImpl.createSocket(Ljava/lang/String;ILjava/net/InetAddress;I)Ljava/net/Socket;+13
    j  com.ufclub.daq.qhzx.utils.SSLProtocolSocketFactory.createSocket(Ljava/lang/String;ILjava/net/InetAddress;I)Ljava/net/Socket;+15
    .... 省略代码
    

这部分内容包含出发 JVM 致命错误的线程详细信息和线程栈。

**线程信息**

    
    
    Current thread (0x0000000001e94800):  JavaThread "pool-1-thread-2" [_thread_in_native, id=30111, stack(0x00007f3d567e5000,0x00007f3d568e6000)]
    

  * 0x0000000001e94800：出错的线程指针
  * JavaThread：线程类型，可能的类型包括 
    1. JavaThread：Java线程
    2. VMThread : JVM 的内部线程
    3. CompilerThread：用来调用JITing，实时编译装卸class 。 通常，jvm会启动多个线程来处理这部分工作，线程名称后面的数字也会累加，例如：CompilerThread1
    4. GCTaskThread：执行gc的线程
    5. WatcherThread：JVM 周期性任务调度的线程，是一个单例对象
    6. ConcurrentMarkSweepThread：jvm在进行CMS GC的时候，会创建一个该线程去进行GC，该线程被创建的同时会创建一个SurrogateLockerThread（简称SLT）线程并且启动它，SLT启动之后，处于等待阶段。CMST开始GC时，会发一个消息给SLT让它去获取Java层Reference对象的全局锁：Lock
  * pool-1-thread-2：线程名称
  * _thread_in_native：当前线程状态。该描述还包含有： 
    1. _thread_in_native：线程当前状态，状态枚举包括：
    2. _thread_uninitialized：线程还没有创建，它只在内存原因崩溃的时候才出现
    3. _thread_new：线程已经被创建，但是还没有启动
    4. _thread_in_native：线程正在执行本地代码，一般这种情况很可能是本地代码有问题
    5. _thread_in_vm：线程正在执行虚拟机代码
    6. _thread_in_Java：线程正在执行解释或者编译后的Java代码
    7. _thread_blocked：线程处于阻塞状态
    8. …_trans：以_trans结尾，线程正处于要切换到其它状态的中间状态
  * id=30111：线程ID
  * stack(0x00007f3d567e5000,0x00007f3d568e6000)：栈区间

    
    
    siginfo: si_signo: 11 (SIGSEGV), si_code: 1 (SEGV_MAPERR), si_addr: 0x0000000000000003
    

表示导致虚拟机终止的非预期的信号信息。

    
    
    Top of Stack: (sp=0x00007f3d568e2280)
    0x00007f3d568e2280:   b8e4bfb900000800 00007f3d568e3760
    0x00007f3d568e2290:   00007f3d568e3758 00007f3d568e377c
    0x00007f3d568e22a0:   00007f3d568e3778 6f6e6b6e56a88a58
    0x00007f3d568e22b0:   00000100000149a0 7a68710800000000
    0x00007f3d568e22c0:   6970067363642d78 6d6f63036e61676e
    ....省略
    
    Instructions: (pc=0x0000003797807a91)
    0x0000003797807a71:   48 89 45 b8 48 8b 4d b8 0f b6 51 03 89 d3 83 e3
    0x0000003797807a81:   0f 75 0d 0f b7 49 06 66 c1 c9 08 66 85 c9 75 4f
    0x0000003797807a91:   0f b6 48 03 bf 0f 00 00 00 40 20 cf 75 0d 0f b7
    0x0000003797807aa1:   70 06 66 c1 ce 08 66 85 f6 75 34 83 e1 0f 83 e2 
    

栈顶程序计数器旁的操作码，它们可以被反汇编成系统崩溃前执行的指令。

    
    
    Stack: [0x00007f3d567e5000,0x00007f3d568e6000],  sp=0x00007f3d568e2280,  free space=1012k
    Native frames: (J=compiled Java code, j=interpreted, Vv=VM code, C=native code)
    C  [libresolv.so.2+0x7a91]  __libc_res_nquery+0x1c1
    C  [libresolv.so.2+0x7fd1]
    
    Java frames: (J=compiled Java code, j=interpreted, Vv=VM code)
    J 15056  java.net.Inet6AddressImpl.lookupAllHostAddr(Ljava/lang/String;)[Ljava/net/InetAddress; (0 bytes) @ 0x00007f3d7492af8c [0x00007f3d7492af40+0x4c]
    J 14966 C1 java.net.InetAddress.getAddressesFromNameService(Ljava/lang/String;Ljava/net/InetAddress;)[Ljava/net/InetAddress; (245 bytes) @ 0x00007f3d75466754 [0x00007f3d754662c0+0x494]
    J 14291 C2 java.net.InetAddress.getAllByName(Ljava/lang/String;Ljava/net/InetAddress;)[Ljava/net/InetAddress; (387 bytes) @ 0x00007f3d7534b718 [0x00007f3d7534ae20+0x8f8]
    J 14178 C1 java.net.InetSocketAddress.<init>(Ljava/lang/String;I)V (47 bytes) @ 0x00007f3d752ce0f4 [0x00007f3d752cdec0+0x234]
    j  sun.security.ssl.SSLSocketImpl.<init>(Lsun/security/ssl/SSLContextImpl;Ljava/lang/String;ILjava/net/InetAddress;I)V+144
    j  sun.security.ssl.SSLSocketFactoryImpl.createSocket(Ljava/lang/String;ILjava/net/InetAddress;I)Ljava/net/Socket;+13
    j  com.ufclub.daq.qhzx.utils.SSLProtocolSocketFactory.createSocket(Ljava/lang/String;ILjava/net/InetAddress;I)Ljava/net/Socket;+15
    .... 省略代码
    

线程栈信息。包含了地址、栈顶、栈计数器和线程尚未使用的栈信息。到这里就基本上已经确定了问题所在原因了。

## 线程信息

    
    
    Java Threads: ( => current thread )
      0x00007f3d5d0a0800 JavaThread "logback-8" daemon [_thread_blocked, id=489, stack(0x00007f3d56de7000,0x00007f3d56ee8000)]
      0x00007f3d5d09f800 JavaThread "logback-7" daemon [_thread_blocked, id=30974, stack(0x00007f3d53fc3000,0x00007f3d540c4000)]
      0x00007f3d5c47f800 JavaThread "logback-6" daemon [_thread_blocked, id=25662, stack(0x00007f3d545c9000,0x00007f3d546ca000)]
      0x00007f3d5c2a4000 JavaThread "logback-5" daemon [_thread_blocked, id=20922, stack(0x00007f3d552d2000,0x00007f3d553d3000)]
      0x0000000003291800 JavaThread "logback-4" daemon [_thread_blocked, id=16768, stack(0x00007f3d542c6000,0x00007f3d543c7000)]
      0x0000000002320000 JavaThread "logback-3" daemon [_thread_blocked, id=14730, stack(0x00007f3d54bcd000,0x00007f3d54cce000)]
      0x0000000002d05000 JavaThread "logback-2" daemon [_thread_blocked, id=6569, stack(0x00007f3d549cb000,0x00007f3d54acc000)]
    

所有线程信息，一目了然。_thread_blocked表示阻塞。

## 安全点和锁信息

    
    
    VM state:not at safepoint (normal execution)
    

虚拟机状态。not at safepoint 表示正常运行。其余状态：  
– at safepoint：所有线程都因为虚拟机等待状态而阻塞，等待一个虚拟机操作完成；  
– synchronizing：一个特殊的虚拟机操作，要求虚拟机内的其它线程保持等待状态。

    
    
    VM Mutex/Monitor currently owned by a thread: None
    

虚拟机的 Mutex 和 Monito r目前没有被线程持有。Mutex 是虚拟机内部的锁，而 Monitor 则关联到了 Java 对象。

## 堆信息

    
    
    Heap:
     PSYoungGen      total 178688K, used 25522K [0x00000000eab00000, 0x00000000f8d80000, 0x0000000100000000)
      eden space 177664K, 13% used [0x00000000eab00000,0x00000000ec343d30,0x00000000f5880000)
      from space 1024K, 65% used [0x00000000f8c80000,0x00000000f8d28d20,0x00000000f8d80000)
      to   space 1024K, 0% used [0x00000000f8b80000,0x00000000f8b80000,0x00000000f8c80000)
     ParOldGen       total 360448K, used 47193K [0x00000000c0000000, 0x00000000d6000000, 0x00000000eab00000)
      object space 360448K, 13% used [0x00000000c0000000,0x00000000c2e16518,0x00000000d6000000)
     Metaspace       used 79300K, capacity 80628K, committed 80936K, reserved 1120256K
      class space    used 9401K, capacity 9645K, committed 9768K, reserved 1048576K
    
    Card table byte_map: [0x00007f3d729f1000,0x00007f3d72bf2000] byte_map_base: 0x00007f3d723f1000
    

新生代、老年代、元空间一目了然。

`Card table`表示一种卡表，是 jvm 维护的一种数据结构，用于记录更改对象时的引用，以便 gc 时遍历更少的 table 和 root。

## 本地代码缓存

    
    
    CodeCache: size=245760Kb used=41374Kb max_used=41402Kb free=204385Kb
     bounds [0x00007f3d72fb2000, 0x00007f3d75872000, 0x00007f3d81fb2000]
     total_blobs=12767 nmethods=12130 adapters=549
     compilation: enabled
    

一块用于编译和保存本地代码的内存。

## 编译事件

    
    
    Compilation events (10 events):
    Event: 501041.566 Thread 0x0000000001b6e000 16334       3       sun.security.rsa.RSAKeyFactory::<init> (5 bytes)
    Event: 501041.566 Thread 0x0000000001b6e000 nmethod 16334 0x00007f3d74985790 code [0x00007f3d74985900, 0x00007f3d74985b10]
    Event: 501041.569 Thread 0x0000000001b6e000 16335       3       sun.security.pkcs.PKCS8Key::<init> (5 bytes)
    Event: 501041.570 Thread 0x0000000001b6e000 nmethod 16335 0x00007f3d74736290 code [0x00007f3d74736400, 0x00007f3d747365b0]
    Event: 501041.575 Thread 0x0000000001b6e000 16336       3       sun.security.ssl.BaseSSLSocketImpl::<init> (15 bytes)
    Event: 501041.576 Thread 0x0000000001b6e000 nmethod 16336 0x00007f3d73f9b450 code [0x00007f3d73f9b5c0, 0x00007f3d73f9b7e8]
    Event: 501041.578 Thread 0x0000000001b6e000 16337       3       javax.net.ssl.SSLSocket::<init> (5 bytes)
    Event: 501041.580 Thread 0x0000000001b6e000 nmethod 16337 0x00007f3d739c7210 code [0x00007f3d739c7380, 0x00007f3d739c7508]
    Event: 501041.582 Thread 0x0000000001b6e000 16338       3       javax.net.ssl.SNIServerName::<init> (66 bytes)
    Event: 501041.583 Thread 0x0000000001b6e000 nmethod 16338 0x00007f3d74c15cd0 code [0x00007f3d74c15ea0, 0x00007f3d74c164f8]
    

记录10次编译事件。这里的信息也印证了上面的结论。

## gc 日志

    
    
    GC Heap History (10 events):
    Event: 476166.948 GC heap before
    {Heap before GC invocations=149 (full 3):
     PSYoungGen      total 194560K, used 193984K [0x00000000eab00000, 0x00000000f8e80000, 0x0000000100000000)
      eden space 193536K, 100% used [0x00000000eab00000,0x00000000f6800000,0x00000000f6800000)
      from space 1024K, 43% used [0x00000000f8c80000,0x00000000f8cf0000,0x00000000f8d80000)
      to   space 1024K, 0% used [0x00000000f8d80000,0x00000000f8d80000,0x00000000f8e80000)
     ParOldGen       total 360448K, used 47161K [0x00000000c0000000, 0x00000000d6000000, 0x00000000eab00000)
      object space 360448K, 13% used [0x00000000c0000000,0x00000000c2e0e518,0x00000000d6000000)
     Metaspace       used 79243K, capacity 80500K, committed 80680K, reserved 1120256K
      class space    used 9400K, capacity 9645K, committed 9768K, reserved 1048576K
    Event: 476166.985 GC heap after
    Heap after GC invocations=149 (full 3):
     PSYoungGen      total 190464K, used 448K [0x00000000eab00000, 0x00000000f8e00000, 0x0000000100000000)
      eden space 189952K, 0% used [0x00000000eab00000,0x00000000eab00000,0x00000000f6480000)
      from space 512K, 87% used [0x00000000f8d80000,0x00000000f8df0000,0x00000000f8e00000)
      to   space 1024K, 0% used [0x00000000f8c00000,0x00000000f8c00000,0x00000000f8d00000)
     ParOldGen       total 360448K, used 47161K [0x00000000c0000000, 0x00000000d6000000, 0x00000000eab00000)
      object space 360448K, 13% used [0x00000000c0000000,0x00000000c2e0e518,0x00000000d6000000)
     Metaspace       used 79243K, capacity 80500K, committed 80680K, reserved 1120256K
      class space    used 9400K, capacity 9645K, committed 9768K, reserved 1048576K
    }
    ... 省略
    

同样是记录10次 GC。

## jvm 内存映射

    
    
    Dynamic libraries:
    00400000-00401000 r-xp 00000000 fd:00 2108521                            /usr/java/jdk1.8.0_45/bin/java
    00600000-00601000 rw-p 00000000 fd:00 2108521                            /usr/java/jdk1.8.0_45/bin/java
    019e9000-04f5e000 rw-p 00000000 00:00 0                                  [heap]
    c0000000-d6000000 rw-p 00000000 00:00 0 
    d6000000-eab00000 ---p 00000000 00:00 0 
    ... 
    7f3d6df48000-7f3d6df6a000 r--s 0038e000 fd:00 2108900                    /usr/java/jdk1.8.0_45/jre/lib/ext/cldrdata.jar
    7f3d6df6a000-7f3d6df73000 r--s 07db3000 fd:00 2374798                    /opt/risk/service/xxx-xxx-container/xxx-xxxx-container.jar
    ... 
    
    

这些信息是虚拟机崩溃时的虚拟内存列表区域。它可以告诉你崩溃原因时哪些类库正在被使用，位置在哪里，还有堆栈和守护页信息。

  * 00400000-00401000：内存区域
  * r-xp：权限，r/w/x/p/s分别表示读/写/执行/私有/共享
  * 00000000：文件内的偏移量
  *     * fd:00：文件位置的majorID和minorID
  * 2108521：索引节点号
  * /usr/java/jdk1.8.0_45/bin/java：文件位置

从`/opt/risk/service/xxx-xxx-container/xxx-xxxx-container.jar`我们可以确认是那个jar出问题了。

## jvm 启动参数

    
    
    VM Arguments:
    jvm_args: -Xmx1024M -Xms512M -XX:PermSize=128M -XX:MaxPermSize=256M 
    java_command: /opt/risk/service/xxx-xxx-xxx-container/xxx-xxx-xxx-container.jar
    java_class_path (initial): /opt/risk/service/xxx-xxx-xxx-container/xxx-xxx-xxx-container.jar
    Launcher Type: SUN_STANDARD
    
    Environment Variables:
    JAVA_HOME=/usr/java/jdk1.8.0_45
    CLASSPATH=.:/usr/java/jdk1.8.0_45/lib/dt.jar:/usr/java/jdk1.8.0_45/lib/tools.jar
    PATH=/usr/java/jdk1.8.0_45/bin:/bin:/usr/local/erlang/bin:/usr/local/maven3/bin:/usr/local/git/bin:/usr/java/jdk1.8.0_45/bin:/bin:/usr/local/erlang/bin:/usr/local/maven3/bin:/usr/local/git/bin:/usr/lib64/qt-3.3/bin:/usr/local/sbin:/usr/bin:/bin:/usr/sbin:/sbin:/root/bin
    SHELL=/bin/bash
    

jvm 虚拟机参数和环境变量。

## 参考资料

  * [JVM致命错误日志（hs_err_pid.log）解读](http://www.raychase.net/1459)
  * [JVM致命错误日志(hs_err_pid.log)分析](http://blog.csdn.net/github_32521685/article/details/50355661)

