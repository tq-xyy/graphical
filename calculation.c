#include <stdio.h>
#include <string.h>

#define maxn 100005

char s[maxn],infixList[maxn][10];
char suffix[maxn][10];
int p=0;
char tmp[maxn];
int p1=0;

//把字符串根据操作数、运算符、括号拆开，存储到infixList数组中
int _toInfixExpression(char *s) {
    int tot=0,n=strlen(s);
    for(int i=0;i<n;i++) {
        if(s[i]>='0'&&s[i]<='9') {
            int p=0;
            infixList[tot][p++]=s[i];
            while(i+1<n&&s[i+1]>='0'&&s[i+1]<='9') {
                infixList[tot][p++]=s[++i];
            }
            tot++;
        }else{
            infixList[tot++][0]=s[i];
        }
    }
    return tot;
}

//获得优先级
int _getPriority(char c) {
    if(c=='+'||c=='-') return 1;
    else if(c=='*'||c=='/') return 2;
    else return 0; //处理'('的情况
}

//转换成后缀表达式
void _parseSuffixExpression(char s[][10],int n) {

    for(int i=0;i<n;i++) {
        if(s[i][0]>='0'&&s[i][0]<='9') {
            strcpy(suffix[p++],s[i]);
        }else if(s[i][0]=='('){
            tmp[p1++]=s[i][0];
        }else if(s[i][0]==')') {
            while(tmp[p1-1]!='(') {
                suffix[p++][0]=tmp[--p1];
            }
            p1--;
        }else{
            while(p1!=0 && _getPriority(tmp[p1-1])>=_getPriority(s[i][0])){
                suffix[p++][0]=tmp[--p1];
            }
            tmp[p1++]=s[i][0];
        }
     }
     while(p1!=0) {
         suffix[p++][0]=tmp[--p1];
     }
}

//计算一个以字符串形式存储的数的值
int _parseInt(char *s) {
    int k=strlen(s);
    int ans=0;
    for(int i=0;i<k;i++) {
        ans=ans*10+(s[i]-'0');
    }
    return ans;
}

//将数k转化成字符串形式存储到指针s开始的地方
void _parseString(char *s,int k){
    char b[11];
    int point=0;
    do{
        b[point++]=(char)('0'+k%10);
        k/=10;
    }while(k!=0);
    for(int i=point-1,j=0;i>=0;i--,j++) {
        *(s+j)=b[i];
    }
    *(s+point)='\0';
}

//计算后缀表达式的值
int _calculate() {
    int point=0;
    char t[maxn][10];
    int m=1;
    for(int i=0;i<p;i++) {
        int k=strlen(suffix[i]);
        if(suffix[i][0]>='0'&&suffix[i][0]<='9') {
            strcpy(t[point++],suffix[i]);
            t[point-1][k]='\0';
        }else {
            int b=_parseInt(t[--point]);
            int a=_parseInt(t[--point]);
            int res=0;
            if(suffix[i][0]=='+') {
                res=a+b;
                //printf("(%d) %d + %d = %d\n",m++,a,b,res);
            }else if(suffix[i][0]=='-') {
                res=a-b;
                //printf("(%d) %d - %d = %d\n",m++,a,b,res);
            }else if(suffix[i][0]=='*') {
                res=a*b;
                //printf("(%d) %d * %d = %d\n",m++,a,b,res);
            }else if(suffix[i][0]=='/') {
                if(b==0) {
                    //printf("除数为零出错！！！\n");
                    return -1;
                }
                res=a/b;
                //printf("(%d) %d / %d = %d\n",m++,a,b,res);
            }
            _parseString(t[point],res);
            point++;
        }
    }
    return _parseInt(t[0]);
}

int compute(char *value) {
    p=p1=0;
    int infixNum=_toInfixExpression(value);
    _parseSuffixExpression(infixList,infixNum);
    int ans=_calculate();
    return ans;
}

/*
int main() {
    //输入字符串
    while(1) {
        int a;
        a = compute("1+1");
        printf("\n%d\n",a);
        p=p1=0;
        printf("------------------------------\n");
        printf("Please enter the expression to be calculated:");
        scanf("%s",s);
        int infixNum=_toInfixExpression(s);
        _parseSuffixExpression(infixList,infixNum);
        printf("The calculation process is as follows:\n");
        int ans=_calculate();
        printf("The operation result is: %d\n",ans);
        printf("------------------------------\n");
        printf("Please choose whether to continue (enter 0 to exit, otherwise continue):");
        int opt;
        scanf("%d",&opt);
        if(opt==0) break;
        printf("\n");

    }
}
*/
