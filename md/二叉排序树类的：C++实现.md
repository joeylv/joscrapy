
    #include<iostream>
    using namespace std;
    
    template<class T>
    struct TreeNode
    {
        T element;
        TreeNode<T>*parent, *lnode, *rnode;
        TreeNode(){ parent = lnode = rnode = NULL; }
        TreeNode(const T& key)
        {
            element = key;
            parent = lnode = rnode = NULL;
        }
    };
    
    template<class T>
    class BStree
    {
    public:
        BStree() :root(NULL){}
        //获取根结点
        TreeNode<T>* Getroot(){ return root; }
        //中序遍历
        void Inorder(TreeNode<T>*node);                 
        //递归查找
        TreeNode<T>* TreeSearch(TreeNode<T>*node, T key);    
        //迭代查找
        TreeNode<T>* IterativeTreeSearch(TreeNode<T>*node, T key);       
        //插入元素
        void TreeInsert(T key);    
        //最大值
        TreeNode<T>*TreeMax(TreeNode<T>*node);   
        //最小值
        TreeNode<T>*TreeMin(TreeNode<T>*node);   
        //查找前驱结点
        TreeNode<T>*TreePredecessor(T key);    
        //查找后继结点
        TreeNode<T>*TreeSuccessor(T key);            
        //用结点 nodeM 替换结点 nodeN,删除操作的辅助函数
        void TransPlant(TreeNode<T>*nodeM, TreeNode<T>*nodeN);    
        //删除结点是key的元素
        void Delete(T key);                 
    
    private:
        TreeNode<T>* root;
    };
    
    //中序遍历
    template<class T>
    void BStree<T>::Inorder(TreeNode<T>*node)
    {
        if (node == NULL)
            return;
        else
        {
            Inorder(node->lnode);
            cout << node->element << " ";
            Inorder(node->rnode);
        }
    }
    
    //递归查找,调用时，node的初始值是root
    template<class T>
    TreeNode<T>* BStree<T>::TreeSearch(TreeNode<T>*node, T key)
    {
        if ((node == NULL) || (key == node->element))
        {
            if (node == NULL)
                cout << "不存在该元素" << endl;
            else
                cout << "存在该元素" << endl;
            return node;
        }
            
        if (key > node->element)
             return TreeSearch(node->rnode,key);
        else
            return TreeSearch(node->lnode,key);
    }
    
    //迭代查找，node参数为root(根结点）
    template<class T>
    TreeNode<T>* BStree<T>::IterativeTreeSearch(TreeNode<T>*node, T key)
    {
        while (node != NULL&&key != node->element)
        {
            if (key < node->element)
                node = node->lnode;
            else
                node = node->rnode;
        }
        if (node == NULL)
            cout << "不存在该元素" << endl;
        else
            cout << "存在该元素" << endl;
        return node;
    }
    
    //插入元素
    template<class T>
    void BStree<T>::TreeInsert(T key)
    {
        TreeNode<T>* y = NULL;
        TreeNode<T>* x = root;
        TreeNode<T>* z = new TreeNode<T>(key);  //将需要插入的元素放入新建立的结点中
        while (x != NULL)  //找到要插入位置的双亲结点
        {
            y = x;
            if (z->element < x->element)
                x = x->lnode;
            else
                x = x->rnode;
        }
        z->parent = y;   
        if (y == NULL)    // 判断要插入的是：左 或 右结点
            root = z;
        else if (z->element>y->element)
            y->rnode = z;
        else
            y->lnode = z;
    }
    
    //最大值，一直遍历所给结点的右子树
    template<class T>
    TreeNode<T>*BStree<T>::TreeMax(TreeNode<T>*node)             
    {
        while (node->rnode != NULL)
            node = node->rnode;
        cout << "最大值是：" << node->element << endl;
        return node;
    }
    
    // 最小值，一直遍历所给结点的左子树
    template<class T>
    TreeNode<T>*BStree<T>::TreeMin(TreeNode<T>*node)            
    {
        while (node->lnode != NULL)
            node = node->lnode;
        cout << "最小值是：" << node->element << endl;
        return node;
    }
    
    //查找后继结点
    template<class T>    
    TreeNode<T>*BStree<T>::TreeSuccessor(T key)
    {
        TreeNode<T>* x = TreeSearch(root, key);    //查找关键字key所对应的结点
        if (x->rnode != NULL)                   //如果结点x存在右结点，则直接查找右结点为跟的最小值
            return TreeMin(x->rnode);
        /*若，不存在右结点
        1、if(x==x->parent->lnode), 则 x 的后继元素即是 x 的双亲结点
        2、if(x==x->parent->rnode)，则 x 的双亲 y 及 y->lnode均小于x,
        直到 x 的某一祖先 Yn 为左节点时，Yn 的双亲即是 x 的后继元素
        */
        TreeNode<T>*y = x->parent;
        while (y != NULL&&x == y->rnode)  
        {
            x = y;
            y = y->parent;
        }
        return y;
    }
    
    //查找前驱结点
    template<class T>   
    TreeNode<T>*BStree<T>::TreePredecessor(T key)
    {
        TreeNode<T>* x = TreeSearch(root, key);    //查找关键字key所对应的结点
        if (x->lnode != NULL)
            return TreeMax(x->lnode);    //若x的左子树不为空，查找左子树的最大值
        TreeNode<T>*y = x->parent;
        while (y != NULL&&x == y->lnode)
        {
            x = y;
            y = y->lnode;
        }
        return y;
    }
    
    //用结点 m 替换结点 n，不包括v的左右子树的更新
    template<class T>     
    void BStree<T>::TransPlant(TreeNode<T>*nodeM, TreeNode<T>*nodeN)   
    {
        if (nodeN->parent == NULL)
            root = nodeM;
        else if (nodeN == nodeN->parent->lnode)   // nodeN 是左结点，更新nodeN->parent 的左结点
            nodeN->parent->lnode = nodeM;
        else
            nodeN->parent->rnode = nodeM;
        if (nodeM != NULL)
            nodeM->parent = nodeN->parent;
    }
    
    //删除结点关节字是key的元素
    template<class T>     
    void BStree<T>::Delete(T key)
    {
        TreeNode<T>*z = IterativeTreeSearch(root,key);    //z 是要删除的结点
        if (z->lnode == NULL)
            TransPlant(z->rnode,z);
        else if (z->rnode == NULL)
            TransPlant(z->lnode,z);
        else
        {
            //找要删除结点的后继元素,
            TreeNode<T>*y = TreeMin(z->rnode);   //类的成员函数在调用成员函数（模板）时，直接写函数名，不需要<T>
            if (y->parent != z)
            {
                TransPlant(y->rnode, y);         //用 y 的右结点替代 y
                y->rnode = z->rnode;             //y的右结点 = z的右结点
                y->rnode->parent = y;
            }
            TransPlant(y,z);              //用 y替代z
            y->lnode = z->lnode;
            y->lnode->parent = y;
        }
    }
    
    
    #include<iostream>
    #include"stdlib.h"
    #include<time.h>
    #include"BSTreecpp.cpp"
    using namespace std;
    
    int main()
    {
        //生成要插入的数据
        int max = 500;
        int min = 0;
        srand((unsigned)time(NULL));
        int a[20] = {};
        int x = 0;
        for (int i = 0; i < 20; i++)
        {
            a[i] = rand() % (max - min) + min;
            cout << a[i] << " ";
        }
        cout << "输入数据：" << endl;
        BStree<int>myTree;
        for (int i = 0; i < 20; i++)
            myTree.TreeInsert(a[i]);
        myTree.Inorder(myTree.Getroot());
        cout << "二叉搜索树中序遍历：" << endl;
        //验证递归查找
        int b = 0;
        TreeNode<int>* A = myTree.TreeSearch(myTree.Getroot(), b);
        //验证迭代查找
        TreeNode<int>* B = myTree.IterativeTreeSearch(myTree.Getroot(), a[2]);
        //验证求取最大值
        TreeNode<int>* C = myTree.TreeMax(myTree.Getroot());
        //验证求取最小值
        TreeNode<int>* D = myTree.TreeMin(myTree.Getroot());
        //求取后继结点
        TreeNode<int>*E = myTree.TreeSuccessor(a[1]);
        cout << a[1] << " 的后继元素是：" << E->element << endl;
        //求取前驱结点
        TreeNode<int>*F = myTree.TreePredecessor(a[3]);
        cout << a[3] << " 的前驱元素是：" << F->element << endl;
        //验证删除结点
        myTree.Delete(a[0]);
        myTree.Inorder(myTree.Getroot());
        cout << "二叉搜索树删除元素后：" << endl;
        system("pause");
        return 0;
    }

