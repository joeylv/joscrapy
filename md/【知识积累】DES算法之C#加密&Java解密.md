一、前言

在项目需要添加安全模块，客户端调用服务端发布的service必须要经过验证，加密算法采用DES，客户端采用C#进行加密，服务端使用Java进行解密。废话不多说，直接上代码。

二、客户端

客户端采用C#进行开发，C#进行DES加密解密代码清单如下：

![]()![]()

    
    
    using System;
    using System.Collections.Generic;
    using System.Linq;
    using System.Text;
    using System.Security.Cryptography;
    using System.IO;
    
    namespace DESHelper
    {
        public class DESHelper
        {
            private static string m_encryptkey = "ENCRYPTT";
            private static string m_str = "IAMACOEDR";
    
            public static string DESEncrypt()
            {
                string str = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + m_str;
                DESCryptoServiceProvider des = new DESCryptoServiceProvider();
                byte[] inputByteArray = Encoding.GetEncoding("UTF-8").GetBytes(str);
                //建立加密对象的密钥和偏移量    
                //原文使用ASCIIEncoding.ASCII方法的GetBytes方法    
                //使得输入密码必须输入英文文本    
                des.Key = ASCIIEncoding.ASCII.GetBytes(m_encryptkey);
                des.IV = ASCIIEncoding.ASCII.GetBytes(m_encryptkey);
                MemoryStream ms = new MemoryStream();
                CryptoStream cs = new CryptoStream(ms, des.CreateEncryptor(), CryptoStreamMode.Write);
    
                cs.Write(inputByteArray, 0, inputByteArray.Length);
                cs.FlushFinalBlock();
                StringBuilder ret = new StringBuilder();
                foreach (byte b in ms.ToArray())
                {
                    ret.AppendFormat("{0:X2}", b);
                }
                ret.ToString();
                return ret.ToString();
            }
    
            public static string DESDecrypt(string pToDecrypt, string sKey)
            {
                DESCryptoServiceProvider des = new DESCryptoServiceProvider();
                byte[] inputByteArray = new byte[pToDecrypt.Length / 2];
                for (int x = 0; x < pToDecrypt.Length / 2; x++)
                {
                    int i = (Convert.ToInt32(pToDecrypt.Substring(x * 2, 2), 16));
                    inputByteArray[x] = (byte)i;
                }
                des.Key = ASCIIEncoding.ASCII.GetBytes(sKey);
                des.IV = ASCIIEncoding.ASCII.GetBytes(sKey);
                MemoryStream ms = new MemoryStream();
                CryptoStream cs = new CryptoStream(ms, des.CreateDecryptor(), CryptoStreamMode.Write);
                cs.Write(inputByteArray, 0, inputByteArray.Length);
                cs.FlushFinalBlock();
                StringBuilder ret = new StringBuilder();
                return System.Text.Encoding.Default.GetString(ms.ToArray());
            }
    
            static void Main(string[] args)
            {
                string str = DESEncrypt();
                Console.WriteLine(str);
                Console.WriteLine(DESDecrypt(str, m_encryptkey));
            }
        }
    }

View Code

运行结果：

34DB26C86E933FB8F9C294A563BEF742D85451292A3C40C6FC8DF5A99C56EDCC  
2016-03-10 12:43:05IAMACOEDR

三、服务器

服务器采用Java进行开发，Java进行DES加密解密代码清单如下：

![]()![]()

    
    
    import javax.crypto.SecretKey;   
    import javax.crypto.SecretKeyFactory;   
    import javax.crypto.spec.DESKeySpec;   
    import javax.crypto.spec.IvParameterSpec;  
    import java.security.Key;
    import java.security.spec.AlgorithmParameterSpec;
    import javax.crypto.Cipher;
    
    public class Des {       
        //解密数据   
        public static String decrypt(String message,String key) throws Exception {                
            byte[] bytesrc =convertHexString(message);      
            Cipher cipher = Cipher.getInstance("DES/CBC/PKCS5Padding");       
            DESKeySpec desKeySpec = new DESKeySpec(key.getBytes("UTF-8"));      
            SecretKeyFactory keyFactory = SecretKeyFactory.getInstance("DES");      
            SecretKey secretKey = keyFactory.generateSecret(desKeySpec);      
            IvParameterSpec iv = new IvParameterSpec(key.getBytes("UTF-8"));                      
            cipher.init(Cipher.DECRYPT_MODE, secretKey, iv);                       
            byte[] retByte = cipher.doFinal(bytesrc);   
            
            return new String(retByte);    
        }  
        
        // 加密数据
        public static byte[] encrypt(String message, String key)   
                throws Exception {   
            Cipher cipher = Cipher.getInstance("DES/CBC/PKCS5Padding");   
            DESKeySpec desKeySpec = new DESKeySpec(key.getBytes("UTF-8"));      
            SecretKeyFactory keyFactory = SecretKeyFactory.getInstance("DES");   
            SecretKey secretKey = keyFactory.generateSecret(desKeySpec);   
            IvParameterSpec iv = new IvParameterSpec(key.getBytes("UTF-8"));   
            cipher.init(Cipher.ENCRYPT_MODE, secretKey, iv);   
       
            return cipher.doFinal(message.getBytes("UTF-8"));   
        }   
            
        public static byte[] convertHexString(String ss) {    
            byte digest[] = new byte[ss.length() / 2];    
            for(int i = 0; i < digest.length; i++) {    
                String byteString = ss.substring(2 * i, 2 * i + 2);    
                int byteValue = Integer.parseInt(byteString, 16);    
                digest[i] = (byte)byteValue;    
            }    
       
            return digest;    
        }  
    
        public static String toHexString(byte b[]) {   
            StringBuffer hexString = new StringBuffer();   
            for (int i = 0; i < b.length; i++) {   
                String plainText = Integer.toHexString(0xff & b[i]);   
                if (plainText.length() < 2)   
                    plainText = "0" + plainText;   
                hexString.append(plainText);   
            }   
                
            return hexString.toString();   
        }       
          
        public static void main(String[] args) throws Exception {   
            String key = "ENCRYPTT";   
            String value = "IAMACODER";   
            String formatString = java.net.URLEncoder.encode(value, "utf-8");             
            System.out.println("加密数据:"+ formatString);   
            String encryptedString = toHexString(encrypt(formatString, key));                    
            System.out.println("加密后的数据为:" + encryptedString);   
            String decryptedString = java.net.URLDecoder.decode(decrypt(encryptedString, key), "utf-8") ;   
            System.out.println("解密后的数据:" + decryptedString);     
        }    
    }

View Code

运行结果：

加密数据:IAMACODER  
加密后的数据为:a8a3f8641ec18ddeff808105c493510e  
解密后的数据:IAMACODER

四、测试C#加密&Java解密

将C#端加密的字符串传入Java端(替换decrypt中的encryptedString即可)直接进行解密，可以得到如下结果：

加密数据:IAMACODER  
加密后的数据为:a8a3f8641ec18ddeff808105c493510e  
解密后的数据:2016-03-10 12:43:05IAMACOEDR

五、总结

这是一个小的功能模块，有此需求的园友可以直接拿去使用，谢谢各位园友观看~

