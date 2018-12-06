##【死磕 Spring】----- IOC 之 注册 BeanDefinition

##
##原文出自：http://cmsblogs.com

##
##获取 Document 对象后，会根据该对象和 Resource 资源对象调用 registerBeanDefinitions() 方法，开始注册 BeanDefinitions 之旅。如下：    public int registerBeanDefinitions(Document doc, Resource resource) throws BeanDefinitionStoreException {        BeanDefinitionDocumentReader documentReader = createBeanDefinitionDocumentReader();        int countBefore = getRegistry().getBeanDefinitionCount();        documentReader.registerBeanDefinitions(doc, createReaderContext(resource));        return getRegistry().getBeanDefinitionCount() - countBefore;    	}

##
##首先调用 createBeanDefinitionDocumentReader() 方法实例化 BeanDefinitionDocumentReader 对象，然后获取统计前 BeanDefinition 的个数，最后调用 registerBeanDefinitions() 注册 BeanDefinition。

##
##实例化 BeanDefinitionDocumentReader 对象方法如下：    protected BeanDefinitionDocumentReader createBeanDefinitionDocumentReader() {        return BeanDefinitionDocumentReader.class.cast(BeanUtils.instantiateClass(this.documentReaderClass));    	}

##
##注册 BeanDefinition 的方法 registerBeanDefinitions() 是在接口 BeanDefinitionDocumentReader 中定义，如下：    void registerBeanDefinitions(Document doc, XmlReaderContext readerContext)            throws BeanDefinitionStoreException;

##
##从给定的 Document 对象中解析定义的 BeanDefinition 并将他们注册到注册表中。方法接收两个参数，待解析的 Document 对象，以及解析器的当前上下文，包括目标注册表和被解析的资源。其中 readerContext 是根据 Resource 来创建的，如下：    public XmlReaderContext createReaderContext(Resource resource) {        return new XmlReaderContext(resource, this.problemReporter, this.eventListener,                this.sourceExtractor, this, getNamespaceHandlerResolver());    	}

##
##DefaultBeanDefinitionDocumentReader 对该方法提供了实现：    public void registerBeanDefinitions(Document doc, XmlReaderContext readerContext) {        this.readerContext = readerContext;        logger.debug("Loading bean definitions");        Element root = doc.getDocumentElement();        doRegisterBeanDefinitions(root);    	}

##
##调用 doRegisterBeanDefinitions() 开启注册 BeanDefinition 之旅。    protected void doRegisterBeanDefinitions(Element root) {        BeanDefinitionParserDelegate parent = this.delegate;        this.delegate = createDelegate(getReaderContext(), root, parent);        if (this.delegate.isDefaultNamespace(root)) {              // 处理 profile            String profileSpec = root.getAttribute(PROFILE_ATTRIBUTE);            if (StringUtils.hasText(profileSpec)) {                String[] specifiedProfiles = StringUtils.tokenizeToStringArray(                        profileSpec, BeanDefinitionParserDelegate.MULTI_VALUE_ATTRIBUTE_DELIMITERS);                if (!getReaderContext().getEnvironment().acceptsProfiles(specifiedProfiles)) {                    if (logger.isInfoEnabled()) {                        logger.info("Skipped XML bean definition file due to specified profiles [" + profileSpec +                                "] not matching: " + getReaderContext().getResource());                    	}                    return;                	}            	}        	}      // 解析前处理        preProcessXml(root);        // 解析        parseBeanDefinitions(root, this.delegate);        // 解析后处理        postProcessXml(root);        this.delegate = parent;    	}

##
##程序首先处理 profile属性，profile主要用于我们切换环境，比如切换开发、测试、生产环境，非常方便。然后调用 parseBeanDefinitions() 进行解析动作，不过在该方法之前之后分别调用 preProcessXml() 和 postProcessXml() 方法来进行前、后处理，目前这两个方法都是空实现，交由子类来实现。    protected void preProcessXml(Element root) {    	}        protected void postProcessXml(Element root) {    	}

##
##parseBeanDefinitions() 定义如下：    protected void parseBeanDefinitions(Element root, BeanDefinitionParserDelegate delegate) {        if (delegate.isDefaultNamespace(root)) {            NodeList nl = root.getChildNodes();            for (int i = 0; i < nl.getLength(); i++) {                Node node = nl.item(i);                if (node instanceof Element) {                    Element ele = (Element) node;                    if (delegate.isDefaultNamespace(ele)) {                        parseDefaultElement(ele, delegate);                    	}                    else {                        delegate.parseCustomElement(ele);                    	}                	}            	}        	}        else {            delegate.parseCustomElement(root);        	}    	}

##
##最终解析动作落地在两个方法处：parseDefaultElement(ele, delegate) 和 delegate.parseCustomElement(root)。我们知道在 Spring 有两种 Bean 声明方式：配置文件式声明：<bean id="studentService" class="org.springframework.core.StudentService"/>自定义注解方式：<tx:annotation-driven>

##
##两种方式的读取和解析都存在较大的差异，所以采用不同的解析方法，如果根节点或者子节点采用默认命名空间的话，则调用 parseDefaultElement() 进行解析，否则调用 delegate.parseCustomElement() 方法进行自定义解析。

##
##至此，doLoadBeanDefinitions() 中做的三件事情已经全部分析完毕，下面将对 Bean 的解析过程做详细分析说明。