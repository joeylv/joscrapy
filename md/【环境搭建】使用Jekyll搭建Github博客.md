## 前言

> 昨天花了差不多一天的时间，使用`Jekyll`搭建起了一套`Github`博客，感觉不错，也特将搭建过程记录下来，方便有需要的朋友自行搭建。

## 搭建步骤

> **本环境是在Linux环境下搭建完成的**  
>  **安装前建议使用命令`sudo apt-get update`更新源**

### 安装Ruby

  * 使用命令`sudo apt-get install ruby`安装ruby。
  * 使用命令`ruby -v`查看`ruby`是否安装成功(成功会出现类似如下字符串：`ruby 1.9.3p484 (2013-11-22 revision 43786) [x86_64-linux]`)。

### 安装Nodejs

  * 使用命令`sudo apt-get install nodejs`安装`nodejs`。
  * 使用命令`nodejs -v`查看`nodejs`是否安装成功(成功会出现类似如下字符串:`v0.10.25`)。

### 安装Jekyll

  * 使用命令`sudo apt-get install jekyll`安装`jekyll`。
  * 使用命令`jekyll -v`查看`jekyll`是否安装成功(成功会出现类似如下字符串：`Jekyll 0.11.2`)。

> `Linux`会自带`python`和`Git`，所以不用安装。

### 新建Github Page

> **下面均以本人`Github`名`leesf`为基础，读者需要自行修改**

  * 在`Github`新建`Repository`，命名为`leesf.github.io`。
  * 使用命令`git clone https://github.com/leesf/leesf.github.io.git`克隆远程仓库至本地。
  * 使用命令`cd leesf.github.io`进入`leesf.github.io`目录。

### 设置Github Page主题

> 至此，环境基本搭建完成，现需要设置主题，可点击此处，[Jekyll主题](http://jekyllthemes.org/)，自选主题。

  * 自选主题后，如本人选的[NextT主题](http://jekyllthemes.org/themes/jekyll-theme-next/)，然后`download/clone`该主题至本地。
  * 将文件夹中所有内容复制到`leesf.github.io`目录下。
  * 使用命令`git add .`添加所有文件。
  * 使用命令`git commit -m "first commit"`提交添加的文件。
  * 使用命令`git push -u origin master`提交至远程仓库。
  * 访问`leesf.github.io`即可查看主题(初始化可能需要等待几分钟)。

### 主题改造

#### 支持中文

上述主题是英文的，现需要将其改造成中文的，由于其是支持中文的，所以只需要将配置文件`_config.yml`中的`language`改成`zh-
Hans`即可。

#### 添加about

上述主题中并未展示`about`内容，需要在配置文件`_config.yml`中`menu`下的`about`注释取消，并且自己使用`markdown`修改`about`目录下的`index.md`文件。

### 写博客

> 经过上述处理后，环境基本搭建完成，可以开始写博客了，写博客建议使用`markdown`，并将文件以`年-月-日-
标题.md`的格式命名后存放至`_post`目录下，然后再使用`git add -> git commit -> git push`命令添加至远程仓库。

## 总结

>
使用jekyll搭建github博客已经全部完成，经过本人改造后的主题存放在[github中](https://github.com/leesf/leesf.github.io)，有需要的读者可以直接使用，同时也非常感谢该主题的制作者。

> **有了一副好皮囊，是时候注入灵魂了。**

