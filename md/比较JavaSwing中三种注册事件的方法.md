Swing 是目前Java中不可缺少的窗口工具组，是建立图形化用户界面（GUI）程序的强大工具。Java
Swing组件自动产生各种事件来响应用户行为。Java将事件封装成事件类，并且为每个事件类定义了一个事件监听器。一个组件注册事件监听器方法，表明该组件要响应指定事件。也就是说我们可以通过注册监听器，监听事件源产生的事件，从而在事件处理程序中处理我们所需要处理的用户行为。

Java Swing中处理各组件事件的一般步骤是：

1． 新建一个组件。

2． 将该组件添加到相应的面板。

3． 注册监听器以监听事件源产生的事件

4． 定义处理事件的方法。

注册事件我们一般采用两种方式：一是：利用一个监听器以及多个if语句来决定是哪个组件产生的事件；二是使用多个内部类来响应不同组件产生的各种事件，它又分两种方式，一种是采用匿名内部类，一种是采用一般内部类。

下面我们采用以上三种方式来注册事件。来说明以上三种方式是如何实现事件的处理方法。

一、采用一个监听器多个if语句来实现

在这种方式下：我们要继承ActionListener接口，并且要实现actionPerformed方法。通过getActionCommand()方法来获取事件的事件源。

    
    
     1 public class Test_01 extends JFrame implements ActionListener {
     2 
     3     Test_01() {
     4         JPanel panel = new JPanel();
     5         JButton button1 = new JButton("按钮一");
     6         JButton button2 = new JButton("按钮二");
     7 
     8         panel.add(button1);
     9         panel.add(button2);
    10         this.getContentPane().add(panel);
    11         this.setVisible(true);
    12         
    13         button1.addActionListener(this);
    14         button2.addActionListener(this);
    15 
    16     }
    17 
    18     public void actionPerformed(ActionEvent e) {
    19         String source = e.getActionCommand();
    20         if (source.equals("按钮一")) {
    21             System.out.println("你按了按钮一");
    22         }
    23         if (source.equals("按钮二")) {
    24             System.out.println("你按了按钮二");
    25         }
    26     }
    27 
    28     public static void main(String args[]) {
    29         new Test_01();
    30 
    31     }
    32 }

利用一个监听器来处理事件的缺点是:其实当处理的事件比较少的时候，这种方式还是一种比较好的方式，它简单。当程序比较复杂时，需要一大串的if语句来实现。程序的代码比较难阅读和维护。

一、利用匿名内部类来是实现

使用匿名内部类来实现可以解决使用if来获取事件源带来的麻烦。但是使用匿名内部类同样存在着一些问题。由于它是和事件组一起的。根据事件组在代码中的位置不同，类的定义以及处理事件，同样不便于阅读。如果事件处理程序比较复杂，内部类中的代码就会变的很长。

    
    
     1 public class Test_02 extends JFrame{
     2     
     3     Test_02(){
     4         JPanel panel = new JPanel();
     5         JButton button1 = new JButton("按钮一");
     6         JButton button2 = new JButton("按钮二");
     7 
     8         panel.add(button1);
     9         panel.add(button2);
    10         this.getContentPane().add(panel);
    11         this.setVisible(true);
    12         
    13         button1.addActionListener(
    14                 new ActionListener(){
    15                     public void actionPerformed(ActionEvent e) {
    16                         System.out.println("你按了按钮一");
    17                     }
    18                 });
    19         button2.addActionListener(
    20                 new ActionListener(){
    21                     public void actionPerformed(ActionEvent e) {
    22                         System.out.println("你按了按钮二");
    23                     }
    24                 });
    25     }
    26     
    27     public static void main(String args[]){
    28         new Test_02();
    29     }
    30 }

三、利用一般内部类来实现

    
    
     1 public class Test_03 extends JFrame{
     2 
     3     Test_03(){
     4         JPanel panel = new JPanel();
     5         JButton button1 = new JButton("按钮一");
     6         JButton button2 = new JButton("按钮二");
     7 
     8         panel.add(button1);
     9         panel.add(button2);
    10         this.getContentPane().add(panel);
    11         this.setVisible(true);
    12         
    13         button1.addActionListener(new Button1ActionListener());
    14         button2.addActionListener(new Button2ActionListener());
    15         
    16     }
    17     
    18     private class Button1ActionListener implements ActionListener{
    19         public void actionPerformed(ActionEvent e) {
    20             System.out.println("你按了按钮一");    
    21         }    
    22     }
    23     
    24     private class Button2ActionListener implements ActionListener{
    25         public void actionPerformed(ActionEvent e) {
    26             System.out.println("你按了按钮二");    
    27         }    
    28     }
    29     
    30     public static void main(String[] args) {
    31         new Test_03();
    32     }
    33 
    34 }

利用一般内部类我们可以解决很多的问题，该方法避免了第二种方法中由于使用匿名内部类而导致的代码混乱。它把所有的事件处理方法都集中在一块，并且都具有有意义的名称，程序非常容易阅读与维护。单个的事件处理程序也可以被工具栏、菜单栏等重复使用。

基于上面的总结，我们一般采用第三种方法来注册事件

