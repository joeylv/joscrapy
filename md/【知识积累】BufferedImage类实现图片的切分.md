一、引言

如何实现图片分割？若有园友用到这个模块，使用Java的BufferedImage类来实现，图片切分也可以作为一个小工具积累起来，以备不时之需。

二、代码清单

![]()![]()

    
    
    package com.leesf.util;
    
    import java.awt.image.BufferedImage;
    import java.io.File;
    import java.io.IOException;
    import java.util.ArrayList;
    
    import javax.imageio.ImageIO;
    
    public class ImageUtil {
        // 切图
        public static ArrayList<BufferedImage> cutImage(String fileUrl, int rows,
                int cols, int nums) {
            ArrayList<BufferedImage> list = new ArrayList<BufferedImage>();
            try {
                BufferedImage img = ImageIO.read(new File(fileUrl));
                int lw = img.getWidth() / cols;
                int lh = img.getHeight() / rows;
                for (int i = 0; i < nums; i++) {
                    BufferedImage buffImg = img.getSubimage(i % cols * lw, i / cols
                            * lh, lw, lh);
                    list.add(buffImg);
                }
                return list;
            } catch (IOException e) {
                e.printStackTrace();
            }
            return list;
        }
    
        public static void main(String[] args) throws IOException {
            ArrayList<BufferedImage> biLists = ImageUtil.cutImage("img/image2.jpg",
                    2, 2, 4);
            String fileNameString = "E:";
            int number = 0;
            String format = "jpg";
            for (BufferedImage bi : biLists) {
                File file1 = new File(fileNameString + File.separator + number
                        + "." + format);
                ImageIO.write(bi, format, file1);
                number++;
            }
        }
    }

View Code

说明：可以切分任何图片，具体的参数园友可以自行配置~之后就可以在配置的目录下看到切分结果了。

三、总结

要将平时遇到的一些小工具积累起来，以备不时之需。谢谢各位园友的观看~

