  * 1 使用方式
  * 2 github地址
  * 3 原理解密
  * 4 总结

> 原文出处：<https://mp.weixin.qq.com/s/gDhsaKg2jXf_mUOW6ixTLg>

你的配置文件是不是还在使用下面这种落后的配置暴露一些密码：

    
    
    jdbc.url=jdbc:mysql://127.0.0.1:3305/afei
    jdbc.username=afei
    jdbc.password=123456
    

如果是，那么继续往下看。笔者今天介绍史上最优雅加密接入方式： **jasypt** 。

## 使用方式

**用法一**

先看用法有多简单，以 springboot 为例：

  1. Application.java 上增加注解 @EnableEncryptableProperties；
  2. 增加配置文件 jasypt.encryptor.password = Afei@2018 ，这是加密的秘钥；
  3. 所有明文密码替换为 ENC (加密字符串)，例如ENC(XW2daxuaTftQ+F2iYPQu0g==) ；
  4. 引入一个MAVEN依赖；

maven坐标如下：

    
    
    <dependency>
        <groupId>com.github.ulisesbocchio</groupId>
        <artifactId>jasypt-spring-boot</artifactId>
        <version>2.0.0</version>
    </dependency>
    

简答的 4 步就搞定啦，是不是超简单？完全不需要修改任何业务代码。其中第三步的加密字符串的生成方式为：

    
    
    java -cp jasypt-1.9.2.jar org.jasypt.intf.cli.JasyptPBEStringEncryptionCLI input="123456" password=Afei@2018 algorithm=PBEWithMD5AndDES
    

其中：

  * input的值就是原密码。
  * password的值就是参数jasypt.encryptor.password指定的值，即秘钥。

* * *

**用法二**

其实还有另一种更简单的姿势：

  1. 增加配置文件 jasypt.encryptor.password = Afei@2018，这是加密的秘钥；
  2. 所有明文密码替换为 ENC (加密字符串)，例如 ENC(XW2daxuaTftQ+F2iYPQu0g==)；
  3. 引入一个MAVEN依赖；

maven 坐标如下：

    
    
    <dependency>
        <groupId>com.github.ulisesbocchio</groupId>
        <artifactId>jasypt-spring-boot-starter</artifactId>
        <version>2.0.0</version>
    </dependency>
    

相比第一种用法，maven 坐标有所变化。但是不需要显示增加注解 @EnableEncryptableProperties；

## github地址

github：https://github.com/ulisesbocchio/jasypt-spring-boot  
它 github 首页有详细的用法说明，以及一些自定义特性，例如使用自定义的前缀和后缀取代 ENC()：

    
    
    jasypt.encryptor.property.prefix=ENC@[
    jasypt.encryptor.property.suffix=]
    

## 原理解密

既然是 springboot 方式集成，那么首先看 jasypt-spring-boot 的 spring.factories 的申明：

    
    
    org.springframework.context.ApplicationListener=\
    com.ulisesbocchio.jasyptspringboot.configuration.EnableEncryptablePropertiesBeanFactoryPostProcessor
    

这个类的部分核心源码如下：

    
    
    public class EnableEncryptablePropertiesBeanFactoryPostProcessor implements BeanFactoryPostProcessor, ApplicationListener<ApplicationEvent>, Ordered {
        @Override
        public void postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory) throws BeansException {
            // 得到加密字符串的处理类（已经加密的密码通过它来解密）
            EncryptablePropertyResolver propertyResolver = beanFactory.getBean(RESOLVER_BEAN_NAME, EncryptablePropertyResolver.class);
            // springboot下的Environment里包含了所有我们定义的属性, 也就包含了application.properties中所有的属性
            MutablePropertySources propSources = environment.getPropertySources();
            // 核心，PropertySource的getProperty(String)方法委托给EncryptablePropertySourceWrapper
            convertPropertySources(interceptionMode, propertyResolver, propSources);
        }
    
        @Override
        public int getOrder() {
            // 让这个jasypt定义的BeanFactoryPostProcessor的初始化顺序最低，即最后初始化
            return Ordered.LOWEST_PRECEDENCE;
        }
    }
    

PropertySource 的 `getProperty(String)`
方法委托给EncryptablePropertySourceWrapper，那么当获取属性时，实际上就是调用
EncryptablePropertySourceWrapper 的 `getProperty()` 方法，在这个方法里我们就能对 value 进行解密了。

EncryptablePropertySourceWrapper 实现了接口EncryptablePropertyResolver，该定义如下：

    
    
    // An interface to resolve property values that may be encrypted.
    public interface EncryptablePropertyResolver {
    
        String resolvePropertyValue(String value);
    }
    

接口描述：  
Returns the unencrypted version of the value provided free on any
prefixes/suffixes or any other metadata surrounding the encrypted value. Or
the actual same String if no encryption was detected.

  * 如果通过 prefixes/suffixes 包裹的属性，那么返回解密后的值；
  * 如果没有被包裹，那么返回原生的值；

实现类的实现如下：

    
    
    @Override
    public String resolvePropertyValue(String value) {
        String actualValue = value;
        // 如果value是加密的value，则进行解密。
        if (detector.isEncrypted(value)) {
            try {
                // 解密算法核心实现
                actualValue = encryptor.decrypt(detector.unwrapEncryptedValue(value.trim()));
            } catch (EncryptionOperationNotPossibleException e) {
                // 如果解密失败，那么抛出异常。
                throw new DecryptionException("Decryption of Properties failed,  make sure encryption/decryption passwords match", e);
            }
        }
        // 没有加密的value，返回原生value即可
        return actualValue;
    }
    

判断是否是加密的逻辑很简单：`(trimmedValue.startsWith(prefix) &amp;&amp;
trimmedValue.endsWith(suffix))`，即只要 value 是以 prefixe/suffixe 包括，就认为是加密的 value。

## 总结

通过对源码的分析可知 jasypt 的原理很简单，就是讲原本 spring 中PropertySource 的 getProperty(String)
方法委托给我们自定义的实现。然后再自定义实现中，判断 value 是否是已经加密的 value ，如果是，则进行解密。如果不是，则返回原 value。

