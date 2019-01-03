# cat命令是linux下的一个文本输出命令，通常是用于观看某个文件的内容的；

_cat主要有三大功能：  
1.一次显示整个文件。  
$ cat filename  
2.从键盘创建一个文件。  
$ cat > filename  
只能创建新文件,不能编辑已有文件.  
3.将几个文件合并为一个文件。  
$cat file1 file2 > file  
cat具体命令格式为 : cat [-AbeEnstTuv] [--help] [--version] fileName  
说明：把档案串连接后传到基本输出(屏幕或加 > fileName 到另一个档案)  
参数：  
-n 或 –number 由 1 开始对所有输出的行数编号  
-b 或 –number-nonblank 和 -n 相似，只不过对于空白行不编号  
-s 或 –squeeze-blank 当遇到有连续两行以上的空白行，就代换为一行的空白行  
-v 或 –show-nonprinting  
范例：  
cat -n linuxfile1 > linuxfile2 把 linuxfile1 的档案内容加上行号后输入 linuxfile2 这个档案里  
cat -b linuxfile1 linuxfile2 >> linuxfile3 把 linuxfile1 和 linuxfile2
的档案内容加上行号(空白行不加)之后将内容附加到linuxfile3 里。  
范例：  
把 linuxfile1 的档案内容加上行号后输入 linuxfile2 这个档案里  
cat -n linuxfile1 > linuxfile2  
把 linuxfile1 和 linuxfile2 的档案内容加上行号(空白行不加)之后将内容附加到 linuxfile3 里。  
cat -b linuxfile1 linuxfile2 >> linuxfile3  
cat /dev/null > /etc/test.txt 此为清空/etc/test.txt档案内容_

在linux shell脚本中我们经常见到类似于cat << EOF的语句，不熟悉的童鞋可能觉得很奇怪：EOF好像是文件的结束符，用在这里起到什么作用？  
EOF是“end of file”，表示文本结束符。  
 **< <EOF  
（内容）  
EOF**

**![](http://my.csdn.net/uploads/201205/11/1336716762_9053.jpg)  
**首先必须要说明的是EOF在这里没有特殊的含义，你可以使用FOE或OOO等（当然也不限制在三个字符或大写字符）。  
可以把EOF替换成其他东西，意思是把内容当作标准输入传给程  
结合这两个标识，即可避免使用多行echo命令的方式，并实现多行输出的结果。

  
接下来，简单描述一下几种常见的使用方式及其作用：  
1、cat<<EOF，以EOF输入字符为标准输入结束：  
2、cat>filename，创建文件，并把标准输入输出到filename文件中，以ctrl+d作为输入结束：  
注意：输入时是没有">"的。  
3、cat>filename<<EOF，以EOF作为输入结束，和ctrl+d的作用一样：

  
二、使用  
看例子是最快的熟悉方法：  
 **# cat << EOF > test.sh  
**> #!/bin/bash #“shell脚本”  
> #you Shell script writes here.  
> **EOF**

结果：  
引用# cat test.sh  
#!/bin/bash  
#you Shell script writes here.

可以看到，test.sh的内容就是cat生成的内容。  
cat <<EOF >test.sh 内容 EOF  
\---就是将内容写入test.sh，之前存在的内容会被覆盖掉。EOF可以换成其他符号比如EEE：cat <<EEE >test.sh 内容 EEE

三、其他写法  
1、 **追加文件  
# cat << EOF >> test.sh 内容 EOF  
**\---将内容追加到 test.sh 的后面，不会覆盖掉原有的内容  
2、换一种写法  
 **# cat > test.sh << EOF 内容 EOF  
**3、EOF只是标识，不是固定的  
# cat << HHH > iii.txt  
> sdlkfjksl  
> sdkjflk  
> asdlfj  
> HHH  
这里的“HHH”就代替了“EOF”的功能。结果是相同的。  
引用# cat iii.txt  
sdlkfjksl  
sdkjflk  
asdlfj

4、非脚本中  
如果不是在脚本中，我们可以用Ctrl-D输出EOF的标识  
# cat > iii.txt  
skldjfklj  
sdkfjkl  
kljkljklj  
kljlk  
Ctrl-D

结果：  
引用# cat iii.txt  
skldjfklj  
sdkfjkl  
kljkljklj  
kljlk

※关于“>”、“>>”、“<”、“<<”等的意思，请自行查看bash的介绍。

