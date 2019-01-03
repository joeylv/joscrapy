WARN util.NativeCodeLoader: Unable to load native-hadoop library for your
platform... using builtin-java classes where applicable

解决方案是在文件hadoop-env.sh中增加：

export HADOOP_OPTS="-Djava.library.path=${HADOOP_HOME}/lib/native"  

