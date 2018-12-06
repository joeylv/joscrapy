##【环境搭建】使用Jekyll搭建Github博客前言

##
##昨天花了差不多一天的时间，使用Jekyll搭建起了一套Github博客，感觉不错，也特将搭建过程记录下来，方便有需要的朋友自行搭建。搭建步骤

##
##本环境是在Linux环境下搭建完成的安装前建议使用命令sudo apt-get update更新源安装Ruby使用命令sudo apt-get install ruby安装ruby。使用命令ruby -v查看ruby是否安装成功(成功会出现类似如下字符串：ruby 1.9.3p484 (2013-11-22 revision 43786) [x86_64-linux])。安装Nodejs使用命令sudo apt-get install nodejs安装nodejs。使用命令nodejs -v查看nodejs是否安装成功(成功会出现类似如下字符串:v0.10.25)。安装Jekyll使用命令sudo apt-get install jekyll安装jekyll。使用命令jekyll -v查看jekyll是否安装成功(成功会出现类似如下字符串：Jekyll 0.11.2)。

##
##Linux会自带python和Git，所以不用安装。新建Github Page

##
##下面均以本人Github名leesf为基础，读者需要自行修改在Github新建Repository，命名为leesf.github.io。使用命令git clone https://github.com/leesf/leesf.github.io.git克隆远程仓库至本地。使用命令cd leesf.github.io进入leesf.github.io目录。设置Github Page主题

##
##至此，环境基本搭建完成，现需要设置主题，可点击此处，Jekyll主题，自选主题。自选主题后，如本人选的NextT主题，然后download/clone该主题至本地。将文件夹中所有内容复制到leesf.github.io目录下。使用命令git add .添加所有文件。使用命令git commit -m "first commit"提交添加的文件。使用命令git push -u origin master提交至远程仓库。访问leesf.github.io即可查看主题(初始化可能需要等待几分钟)。主题改造支持中文

##
##上述主题是英文的，现需要将其改造成中文的，由于其是支持中文的，所以只需要将配置文件_config.yml中的language改成zh-Hans即可。添加about

##
##上述主题中并未展示about内容，需要在配置文件_config.yml中menu下的about注释取消，并且自己使用markdown修改about目录下的index.md文件。写博客

##
##经过上述处理后，环境基本搭建完成，可以开始写博客了，写博客建议使用markdown，并将文件以年-月-日-标题.md的格式命名后存放至_post目录下，然后再使用git add -> git commit -> git push命令添加至远程仓库。总结

##
##使用jekyll搭建github博客已经全部完成，经过本人改造后的主题存放在github中，有需要的读者可以直接使用，同时也非常感谢该主题的制作者。

##
##有了一副好皮囊，是时候注入灵魂了。