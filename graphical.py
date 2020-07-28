#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Graphical
    ~~~~~~~~~~~~
    快速的创建和使用图形公式

这是一个可以自由创建公式的模块
支持以下功能：
1、支持公式参数
2、支持扩展
3、内置图形公式
4、内置中文、分数、文章扩展
5、支持自定义图形

以下是核心部分的声明：

def compute(equation: str, **kwargs) -> int or float: ...

class Graphical_metaclass(type):
    def __new__(cls, name: str, bases: tuple, classdict: dict) -> object: ...

class Graphical(object, metaclass=Graphical_metaclass):
    def __init__(self, **kwargs) -> None: ...

    def __call__(self) -> str: ...

    @classmethod
    def buildtoJSON(cls) -> str: ...
    
    def __repr__(self) -> str: ...
    
    def __str__(self) -> str: ...

class Extension(object):

    def __init__(self, name: str, function: object) -> None: ...

    def get_name(self) -> str: ...

    def get_function(self) -> object: ...

def parameter(*args, **kwargs) -> list: ...

class Integrated_Graphical(object):

    def __init__(self, **kwargs) -> None: ...
    
    def getresult(self, name: str) -> int or float: ...
    
    def __getattr__(self, variable: str) -> int or float: ...
    
    def __call__(self, variable: str) -> int or float: ...

def loadfromJSON(json: str) -> type: ...

"""

formula = None
args = None
extension = None

#导入需要的模块
import argparse  # 用于解析参数
import ast  # 用于解析抽象语法树
import fractions  # 用于分数支持
import re  # 正则表达式
import sys  # 系统调用
from decimal import Decimal  # 精确的浮点数
from enum import Enum, unique  # 枚举
from json import dumps, loads  # json支持

if sys.platform == 'win32':    #判断是否是Windows系统
    from ctypes import WinDLL  # 用于加载dll

__all__ = [    #模块接口列表
    'compute',
    'Graphical',
    'Extension',
    'parameter',
    'Integrated_Graphical',
    'loadfromJSON',
    '正方形',
    'square',
    '正方形面积',
    'square_area',
    '正方形周长',
    'square_perimeter',
    '长方形',
    'rectangle',
    '长方形面积',
    'rectangle_area',
    '长方形周长',
    'rectangle_perimeter',
    '三角形',
    'triangle',
    '三角形面积',
    'triangle_area',
    '梯形',
    'trapezoid',
    '梯形面积',
    'trapezoid_area',
    '平行四边形',
    'parallelogram',
    '平行四边形面积',
    'parallelogram_area',
    '平行四边形周长',
    'parallelogram_perimeter',
    '正方体',
    'cube',
    '正方体表面积',
    'cube_surface_area',
    '正方体体积',
    'cube_volume',
    '正方体棱长总和',
    'sum_of_cube_edges',
    '长方体',
    'cuboid',
    '长方体表面积',
    'cuboid_surface_area',
    '长方体体积',
    'cuboid_volume',
    '长方体棱长总和',
    'sum_of_cuboid_edges',
    '圆形',
    'circle',
    '圆形周长',
    'circle_perimeter',
    '圆形面积',
    'circle_area',
    'Marketing'
]

def compute(equation,c_extend=True,**kwargs):
    """计算字符串表达式

    参数:
    equation (str) --> 表达式本身
    c_extend=True (bool) --> 是否启用c扩展
    **kwargs (dict) --> 全局作用域
    
    返回:
    一个整数或浮点数"""

    #其实这个c扩展的计算bug（不，是特性！）有很多，
    #比如说不支持浮点数、除法计算有误差、不支持扩展等等
    #但是还是很有用的。
    #虽然一般来说这个用处不大，
    #但是如果对于CPU密集计算（疯狂计算）的时候，
    #其实是能提高一点速度（我做过测试）

    def py_compute(equation,**kwargs):
        #返回标准python的eval计算
        #主要是c的缺陷
        return eval(equation,kwargs,{})
    
    if sys.platform != 'win32':
        c_extend = False

    if c_extend:
        class eval_visit(ast.NodeVisitor):
            """遍历源码树"""
            def __init__(self):
                """初始化"""
                self.truediv = False
                self.hasfloat = False
            
            def visit_BinOp(self,node):
                """表达式调用"""
                if isinstance(node.op,ast.Div):    #判断是不是除法
                    self.truediv = True
                self.generic_visit(node)    #处理后续工作
                return node
            
            def visit_Constant(self,node):
                """遇到数字"""
                if isinstance(node.s,float):    #如果是浮点数
                    self.hasfloat = True
                self.generic_visit(node)    #处理后续工作
                return node

                 
        source = ast.parse(equation)    #解析代码，生成抽象语法树
        code = eval_visit()    #初始化遍历对象
        code.visit(source)    #遍历
        if code.truediv:    #如果有除法运算
            #返回eval运算，因为不精确……
            return py_compute(equation,**kwargs)
        
        if code.hasfloat:    #判断是不是浮点数
            #返回eval运算，因为不支持……
            return py_compute(equation,**kwargs)

        if len(kwargs) != 0:    #判断有没有扩展
            #因为，我不知道怎么在C语言里使用python函数
            return py_compute(equation,**kwargs)

        #判断系统位数，在64位的python调用32位的dll会报错
        bit = re.findall(r".*\[.*(\d\d) bit.*\].*",sys.version)[0]
        dll_bit_list = {
            '32':'win32',
            '64':'amd64'
        }
        dll_name = 'graphical-{bit}.dll'.format(bit=dll_bit_list[bit])
        try:
            #导入dll
            dll = WinDLL('.\\' + dll_name)
        except FileNotFoundError:    #找不到会报错，捕获错误
            #就返回普通的计算
            import warnings   #给你个警告
            warnings.warn(
                '找不到DLL: {}'.format(dll_name),
                RuntimeWarning, -1
            )
            return py_compute(equation,**kwargs)
        
        try:    #执行
            return dll.compute(bytes(equation,"utf-8"))
        except OSError:
            return py_compute(equation,**kwargs)

    #都不行调用eval
    return eval(equation,kwargs,{})

class Graphical_metaclass(type):
    """这个是Graphical类的元类，不应该被修改"""
    def __new__(cls,name,bases,classdict:dict):
        if name == "Graphical":    #判断是否是Graphical本身，如果是，直接返回
            return type.__new__(cls,name,bases,classdict)
        
        if callable(classdict.get('plugin')):    
            #判断是否是扩展，
            #实现了plugin接口的直接返回
            return type.__new__(cls,name,bases,classdict)
        
        formula = classdict.get("formula")    #获取必要参数formula和args
        _args = classdict.get("args")

        if "extension" in classdict:    #获取可选扩展参数
            _extension = classdict.get("extension")    #如果有，获取并将has_extension为True
            has_extension = True
        else:
            has_extension = False    #没有，设置has_extension为False
        
        if isinstance(_args,dict):    #这么做是为了兼容json
            key_value = _args    #如果args已经是字典就不用转化了
        else:
            key_value = {}
            for key,value in _args:    #将参数转成字典
                key_value[key] = value

        classdict["formula"] = formula    #将必要参数formula和args写入类字典
        classdict["_args"] = key_value


        #如果有扩展参数这一步将会执行
        

        if has_extension:    #处理扩展参数
            #导入迭代器的基类对象做判断
            if hasattr(_extension, '__iter__'):    #判断是否是一个可迭代对象
                #如果是，迭代出扩展对象
                temp = {}
                for extend in _extension:
                    if not isinstance(extend,Extension):    #判断是否是扩展对象，不是则报错
                        raise TypeError("\'%s\' not a extension object"%extend)

                    temp[extend.get_name()] = extend.get_function()    #解析，加入进字典
                
                _extension = temp
            else:    #不是，直接判断
                if not isinstance(_extension,Extension):    #同上
                    raise TypeError("\'%s\' not a extension object"%extend)

                _extension = {_extension.get_name():_extension.get_function()}    #加入字典
            
            classdict["extension"] = _extension    #将可选参数extension加入类字典

        #没有跳到这里

        return type.__new__(cls,name,bases,classdict)    #返回处理好后的对象


class Graphical(object,metaclass=Graphical_metaclass):
    #继承于object,Graphical_metaclass构建
    """
    创建一个公式

    参数:
        **kwargs (dict) 公式的参数

    方法:
        buildtoJSON 构建成json字符串，持久化
    
    示例:

    class test(Graphical):
        formula = "a*b"
        args = parameter(a="a",b="b")
    a = test(a=2,b=3)  # 6
    """
    def __init__(self, **kwargs):
        self.kwargs = kwargs    #保存公式参数
        
        trans = {}    #初始化映射表
        for key, value in self._args.items():    #迭代参数列表
            if key not in kwargs.keys():    #检查是否传入参数，
                #如果必要的参数没有传入
                raise KeyError(key + " is not given")    #引发错误并详细说明
            trans[value] = str(kwargs[key])    #添加到映射表
        
        table = str.maketrans(trans)    #构建字符映射表
        self._formula = self.formula.translate(table)    #替换

        #计算结果
        if hasattr(self,"extension"):    #如果有扩展属性，说明有扩展模块
            self._value = compute(self._formula,**self.extension)    #使用带扩展的计算
            return
        self._value = compute(self._formula, 
                                c_extend=False
                            )    #没有则使用普通的计算

    def __call__(self):
        """计算结果"""
        return self._value


    @classmethod    #这是一个类静态方法
    def buildtoJSON(cls):
        """构建参数字典"""
        if hasattr(cls, "extension"):    #如果有扩展引发警告
            raise Warning("扩展将会失效")    #因为我不知道如何存储扩展   
        dictionary = {    #构建保存字典
            'name':cls.__name__,
            'formula':cls.formula,
            'args':dict(cls._args.items())
        }
        return dumps(dictionary)    #解析返回json
    
    #用多种方法都可以获取
    def __repr__(self):
        return str(self.__call__())
    
    def __str__(self):
        return str(self.__call__())


class Extension(object):
    """
    扩展类

    参数:
        name (str) 方法名称
        function (function) 方法
    
    方法:
        get_name 获取方法名称
        get_function 获取方法本身
    """
    def __init__(self,name,function):
        self.name = name     #保存名称和函数
        self.function = function

    def get_name(self):
        return self.name    #返回方法名称

    def get_function(self):
        return self.function    #返回方法自身

def parameter(*args,**kwargs):
    """
    将参数转为公式参数格式

    参数:
        *args (list) 位置参数
        **kwargs (dict) 关键字参数

    返回:
        一个可供公式参数读取的格式列表
    
    示例:
    parameter(a="a") --> [("a","a")]
    parameter(a="b") --> [("a","b")]
    parameter("a") --> [("a","a")]
    """
    #使用这个方法是为了方便
    #因为使用 [("传入的参数名","在公式中的参数名"),...] 不是很方便

    argslist = []    #创建临时列表

    #遍历 位置实参 和 位置实参 的值
    #转换并添加进列表
    for variable in args:    #位置形参
        argslist.append((variable,variable))
    
    for key,value in kwargs.items():    #关键字参数
        argslist.append((key,value))
    
    return argslist    #返回临时列表

class Integrated_Graphical(object):
    """
    一个包含一些公式的集合

    参数:
        **kwargs (dict) 图形的参数
    
    用法:
        使用Python的注解添加映射
        注解的格式是:
            class test:
                key1 : value1
                key2 : value2

    示例:

    class test(Integrated_Graphical):
        d : circle_area
    a = test(r=1)
    a.d

    提示: 注解的用法是标记类型，但Python不会去检查它"""
    def __init__(self,**kwargs):
        """初始化图形"""
        self.kwargs = kwargs    #保存参数
        self.model = {}    #初始化映射表
        if getattr(self, '__annotations__', None) is None:    #判断是否有注解
            self.__annotations__ = {}    #如果没有设定为空值，免得报错
        for name, func in self.__annotations__.items():    #遍历注解字典
            #判断是否是公式对象
            assert issubclass(func, Graphical) ,\
                '\'%s\' 不是公式对象 (他是 \'%s\')'%(name,func)    #不是报错
            self.model[name] = func    #将键和值放入映射表

    def getresult(self,name):
        """这里是为了兼容之前的代码而设置的"""
        #附带参数name为参数名称
        #通过这里可以更灵活的计算
        #由于这里被更好用的注解代替
        #所以这里被用来报错
        raise AttributeError('\'%s\' object has no attribute \'%s\'' % (self.__class__.__name__, name))
    
    def __getattr__(self, name):
        """可以用xxx.x的方式获取结果"""
        if name in self.model:    #判断目标是否在映射表里
            func = self.model[name]    #如果在，取出来
            return func(**self.kwargs)    #计算返回
        function = getattr(self,'getresult', None)    #获取报错方法
        return function(name)    #返回，如果重写了这个就不会直接报错
    
    def __call__(self,variable):
        """也可以用xxx("x")的方式获取结果"""
        if variable in self.model:    #判断函数是否在映射表里
            func = self.model[variable]    #如果在，获取键值
            return func(**self.kwargs)    #返回计算结果
        return self.getresult(variable)    #返回报错函数
    
    def __getitem__(self, key):
        """还可以通过xxx['x']的方法获取结果"""
        if self.model.get(key, None) is None:    #判断函数是否在映射表里
            #如果不在
            return self.getresult()    #返回报错函数
        else:    #如果在
            obj = self.model.get(key)    #获取键值
            return obj(**self.kwargs)._value    #返回计算结果


def loadfromJSON(json):
    """
    加载json公式

    参数:
        json (str) JSON字符串
    
    返回:
        一个公式类对象
    """
    dictionary = loads(json)    #解析json
    name = dictionary['name']
    bases = (Graphical,)
    classdict = {
        "formula":dictionary['formula'],
        "args":dictionary['args']
    }
    kind = Graphical_metaclass(name, bases, classdict)    #构建类
    return kind    #返回类

#以下是一些图形简单公式

#正方形
class square_area(Graphical):
    """正方形面积 
    公式:a*a"""
    formula = "a*a"
    args = parameter("a")

class square_perimeter(Graphical):
    """正方形周长
    公式:a*4"""
    formula = "a*4"
    args = parameter("a")

class square(Integrated_Graphical):
    """正方形类
    参数:
    a --> 边长
    含有:面积 周长"""
    def getresult(self,name):
        if (name == "area" or name == "面积"):
            return square_area(**self.kwargs)
        elif (name == "perimeter" or name == "周长"):
            return square_perimeter(**self.kwargs)
        else:
            raise AttributeError("'square' object has no attribute '%s'"%name)

#长方形
class rectangle_area(Graphical):
    """长方形面积 
    公式:a*b"""
    formula = "a*b"
    args = parameter("a","b")

class rectangle_perimeter(Graphical):
    """长方形周长
    公式:(a+b)*2"""
    formula = "(a+b)*2"
    args = parameter("a","b")

class rectangle(Integrated_Graphical):
    """长方形类
    参数:
    a --> 长
    b --> 宽
    含有:面积 周长"""
    def getresult(self,name):
        if (name == "area" or name == "面积"):
            return rectangle_area(**self.kwargs)
        elif (name == "perimeter" or name == "周长"):
            return rectangle_perimeter(**self.kwargs)
        else:
            raise AttributeError("'rectangle' object has no attribute '%s'"%name)

#三角形

#要问为什么三角形只有面积，因为我在百度上搜的只有面积，有谁可以告诉我一下
class triangle_area(Graphical):
    """三角形面积 
    公式:a*h/2"""
    formula = "a*h/2"
    args = parameter("a","h")

class triangle(Integrated_Graphical):
    """三角形类
    参数:
    a --> 底
    h --> 高
    含有:面积"""
    def getresult(self,name):
        if (name == "area" or name == "面积"):
            return triangle_area(**self.kwargs)
        else:
            raise AttributeError("'triangle' object has no attribute '%s'"%name)

#梯形

class trapezoid_area(Graphical):
    """梯形面积 
    公式:(a+b)*h/2"""
    formula = "(a+b)*h/2"
    args = parameter("a","b","h")

class trapezoid(Integrated_Graphical):
    """梯形类
    参数:
    a --> 上底
    b --> 下底
    h --> 高
    含有:面积"""
    def getresult(self,name):
        if (name == "area" or name == "面积"):
            return trapezoid_area(**self.kwargs)
        else:
            raise AttributeError("'trapezoid' object has no attribute '%s'"%name)

#平行四边形
class parallelogram_area(Graphical):
    """平行四边形面积 
    公式:a*h"""
    formula = "a*h"
    args = parameter("a","h")

class parallelogram_perimeter(Graphical):
    """平行四边形周长
    公式:(a+h)*2"""
    formula = "(a+h)*2"
    args = parameter("a","h")

class parallelogram(Integrated_Graphical):
    """平行四边形类
    参数:
    a --> 长
    h --> 高
    含有:面积 周长"""
    def getresult(self,name):
        if (name == "area" or name == "面积"):
            return parallelogram_area(**self.kwargs)
        elif (name == "perimeter" or name == "周长"):
            return parallelogram_perimeter(**self.kwargs)
        else:
            raise AttributeError("'parallelogram' object has no attribute '%s'"%name)

#长方体

class cuboid_volume(Graphical):
    """长方体体积 
    公式:a*b*h"""
    formula = "a*b*h"
    args = parameter(a="a",b="b",h="h")

class cuboid_surface_area(Graphical):
    """长方体表面积 
    公式:(a*b+a*h+b*h)*2"""
    formula = "(a*b+a*h+b*h)*2"
    args = parameter(a="a",b="b",h="h")

class sum_of_cuboid_edges(Graphical):
    """长方体棱长总和 
    公式:(a+b+h)*4"""
    formula = "(a+b+h)*4"
    args = parameter(a="a",b="b",h="h")

class cuboid(Integrated_Graphical):
    """长方体类
    参数:
    a --> 长
    b --> 宽
    h --> 高
    含有:表面积 体积 棱长总和"""
    def getresult(self,name):
        if (name == "volume" or name == "体积"):
            return cuboid_volume(**self.kwargs)
        elif (name == "surface_area" or name == "表面积"):
            return cuboid_surface_area(**self.kwargs)
        elif (name == "total_length" or name == "棱长总和"):
            return sum_of_cuboid_edges(**self.kwargs)
        else:
            raise AttributeError("'cuboid' object has no attribute '%s'"%name)

#正方体

class cube_surface_area(Graphical):
    """正方体表面积 
    公式:a*a*6"""
    formula = "a*a*6"
    args = parameter(a="a")

class cube_volume(Graphical):
    """正方体体积 
    公式:a*a*a"""
    formula = "a*a*a"
    args = parameter(a="a")

class sum_of_cube_edges(Graphical):
    """正方体棱长总和 
    公式:a*12"""
    formula = "a*12"
    args = parameter(a="a")

class cube(Integrated_Graphical):
    """正方体类 
    参数:
    a --> 棱长
    含有:表面积 体积 棱长总和"""
    def getresult(self,name):
        if (name == "volume" or name == "体积"):
            return cube_volume(**self.kwargs)
        elif (name == "surface_area" or name == "表面积"):
            return cube_surface_area(**self.kwargs)
        elif (name == "total_length" or name == "棱长总和"):
            return sum_of_cube_edges(**self.kwargs)
        else:
            raise AttributeError("'cube' object has no attribute '%s'"%name)

#圆形
#由于Python浮点数运算不精确，所以使用Decimal
pai = Decimal("3.14")    #圆周率，一般只要精确到小数点后两位就好了

#惰性求值是专门为圆形设计的
class _lazy_property(object):
    """惰性求值 描述符"""
    def __init__(self,fget):
        self.fun = fget    #初始化
    
    def __get__(self, instance, owner):
        if instance is None:    #如果是类调用
            return self    #返回本身
        value = self.fun(instance)    #计算结果
        setattr(instance,self.fun.__name__, value)    #存放结果
        return value    #返回结果

#这个是最难的
class circle_perimeter(Graphical):
    """圆形周长 
    公式:pi*r*2"""
    formula = "pi*r*2"
    args = parameter("r")
    extension = Extension("pi",pai)

class circle_area(Graphical):
    """圆形面积
    公式:pi*(r*r)"""
    formula = "pi*(r**2)"
    args = parameter("r")
    extension = Extension("pi",pai)

class circle(Integrated_Graphical):
    """圆形类 
    参数:
    r --> 半径
    含有:周长 面积
    常量:
    pi --> 3.14..."""
    @_lazy_property
    def perimeter(self):
        #周长
        return circle_perimeter(**self.kwargs)
    
    @_lazy_property
    def area(self):
        #面积
        return circle_area(**self.kwargs)
    
    def getresult(self,name):
        if (name == "perimeter" or name == "周长"):
            return self.perimeter
        elif (name == "area" or name =="面积"):
            return self.area
        else:
            raise AttributeError("'circle' object has no attribute '%s'"%name)


# 已弃用
# def _namespaces__call__(cls):    #需要一个命名空间类型，就自己写了一个数据类型
#     raise TypeError("'%s' object is not callable"%cls.__qualname__)
# Namespaces = type("_Namespaces_metaclass",(type,),{"__call__":_namespaces__call__})("Namespaces",(object,),{"__qualname__":"Namespaces","__module__":"__main__"})

#一些翻译，方便英文不是很好的同学~

#正方形相关
正方形 = square
正方形面积 = square_area
正方形周长 = square_perimeter

#长方形相关
长方形 = rectangle
长方形面积 = rectangle_area
长方形周长 = rectangle_perimeter

#三角形相关
三角形 = triangle
三角形面积 = triangle_area

#梯形相关
梯形 = trapezoid
梯形面积 = trapezoid_area

#平行四边形
平行四边形 = parallelogram
平行四边形面积 = parallelogram_area
平行四边形周长 = parallelogram_perimeter

#正方体相关
正方体 = cube
正方体表面积 = cube_surface_area
正方体体积 = cube_volume
正方体棱长总和 = sum_of_cube_edges

#长方体相关
长方体 = cuboid
长方体表面积 = cuboid_surface_area
长方体体积 = cuboid_volume
长方体棱长总和 = sum_of_cuboid_edges

#圆形相关
圆形 = circle
圆形周长 = circle_perimeter
圆形面积 = circle_area

_built_cn_en_table = {    #中英对照表
    "square_area":'正方形面积',
    "square_perimeter":'正方形周长',
    "rectangle_area":'长方形面积',
    "rectangle_perimeter":'长方形周长',
    "triangle_area":'三角形面积',
    "trapezoid_area":'梯形面积',
    "parallelogram_area":'平行四边形面积',
    "parallelogram_perimeter":'平行四边形周长',
    "cube_surface_area":'正方体表面积',
    "cube_volume":'正方体体积',
    "sum_of_cube_edges":'正方体棱长总和',
    "cuboid_surface_area":'长方体表面积',
    "cuboid_volume":'长方体体积',
    "sum_of_cuboid_edges":'长方体棱长总和',
    "circle_perimeter":'圆形周长',
    "circle_area":'圆形面积',
    "Marketing":'营销号生成器'
}

中英对照表 = _built_cn_en_table


#一般的一键生成句子
class Graphical_str_compose(Graphical):
    """不会计算，直接返回字符串，适合于生成器"""
    def plugin(self):
        pass

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.replace()
    
    def replace(self):
        self._formula = self.formula
        try:
            for key,value in self._args.items():    #迭代参数字典，将参数替换到公式里
                self._formula = self._formula.replace(str(value),str(self.kwargs[key]))
        except KeyError:    #如果引发KeyError,说明必要的参数没有传入
            raise KeyError(key + " is not given")    #引发错误并详细说明
        #这里再次引发错误是因为原本的错误说明不详细
    
    @_lazy_property   #惰性求值
    def str_formula(self):
        return self._formula

    def __call__(self):
        """直接返回"""
        return self.str_formula

#在此我想说一句，分数扩展真惨啊~~~


class _Plugin(Enum):    #扩展开关
    #已成为标准选项，故已弃用
    # chinese = True    #中文翻译变量名开关，默认为True，中文好的同学可以改成False
    # str_compose = True    #文章扩展

    fraction = False    #分数扩展
    

if _Plugin:    
    if _Plugin.fraction.value:
        """支持分数的扩展"""
        #已知问题：
        #参数可能会替换原公式的分数表达式

        #教程
        #分数表达式: <frac 分子 分母>

        class _Fraction(object):
            """内部函数"""
            def __init__(self,word):
                self.word = word    #保存参数
                self.frac = re.findall(r"<frac \d+ \d+>",self.word)    #解析分数表达式
                value = re.compile("<frac (\d+) (\d+)>")
                for key in self.frac:    #替换分数表达式
                    v = value.findall(key)[0]
                    self.word = self.word.replace(key,"Fraction(%s,%s)"%(v[0],v[1]))
            
            def __str__(self):
                return self.word    #返回表达式
            
            def __call__(self):
                #计算
                return eval(self.word,{"Fraction":fractions.Fraction},{})
        
        class Graphical_fraction(Graphical):
            """分数扩展主扩展"""
            def plugin(self):
                pass

            def __check(self):
                #检查并替换
                Graphical.__check(self)    #调用原函数
            
            def __call__(self):
                """计算"""
                self.frac = _Fraction(self.formula)    #替换分数表达式
                if hasattr(self,"extension"):    #有扩展
                    self.extension["Fraction"] = fractions.Fraction
                    return compute(self.frac.__str__(),**self.extension)
                #无扩展
                return compute(self.frac.__str__(),Fraction=fractions.Fraction)

# 这里使用的自己的单元测试框架
# 有人可能会问为什么不用那些成熟的单元测试框架呢
# 比如 unittest, nose2, ddt, pytest
# 这里我自己做的是因为我觉得自己的话输出可控一些
# 也没有那么多依赖项

class TestCaseMetaclass(type):
    '''单元测试元类'''
    def __new__(cls, name, bases, classdict):
        if name == 'TestCase':    #如果是TestCase本身
            return type.__new__(cls, name, bases, classdict)    #直接返回
        _tests_list = []    #初始化测试列表
        for attr_name, attr in classdict.items():    #遍历类字典
            if attr_name.startswith('_') or attr_name.endswith('_'):    #如果是以下划线开头或结尾的
                continue    #跳过
            elif attr_name.startswith('test_') and callable(attr):    #如果是以 test_ 开头且可调用的
                _tests_list.append(attr)    #加入测试函数列表
        classdict['_tests_list'] = _tests_list    #保存测试函数列表
        return type.__new__(cls, name, bases, classdict)    #构建类对象，返回


class TestCase(metaclass=TestCaseMetaclass):
    '''单元测试框架
    这是一个精简的单元测试的模块
    使用上和 unittest 模块差不多
    但比 unittest 简单了不少
    支持断言、错误分析
    '''
    def __init__(self, stream=sys.stdout):
        '''初始化测试框架

        参数:
            stream    (object) 指定输出的那个类文件对象，需要有 write 方法
        '''
        self.stream = stream    #保存文件流对象

        #初始化添加次数
        self.oks = 0    #通过次数
        self.failures = 0    #断言失败次数
        self.errors = 0    #报错次数

    def _printf(self, *values, sep=' ', end='\n'):
        '''打印文本到文件对象中， 默认和print没有全部
        内部方法
        '''
        print(*values, sep=sep, end=end, file=self.stream)    #对号入座
    
    def assertEqual(self, test_values, real_values):
        '''断言方法
        
        参数:
            test_values  (Any) 测试中的结果
            real_values  (Any) 正确的结果
        
        返回:
            如果一致，返回 True
            否则引发 AssertionError (断言错误) 然后会被捕获
        
        注意:
            虽然将两个参数顺序颠倒不会报错，但强烈不建议这么做，
            因为会产生语义上的错误
        '''
        if test_values == real_values:
            return True
        else:
            raise AssertionError('{} != {}'.format(test_values, real_values))
    
    def assertTrue(self, test_values):
        '''判断是否为 True
        
        参数:
            test_values    (bool) 布尔值
        
        这个方法内部使用了 assertEqual
        '''
        return self.assertEqual(test_values, True)
    
    def assertFalse(self, test_values):
        '''判断是否为 False
        
        参数:
            test_values    (bool) 布尔值
        
        这个方法内部使用了 assertEqual
        '''
        return self.assertEqual(test_values, False)
    
    class assertError:
        '''判断是否会引发某个错误
        
        参数:
            error_type    (Exception) 会引发的错误类型

        例子:
            with self.assertError(KeyError):
                dict()['apple']
        
        返回:
            如果成功抛出错误，返回 None
            否则引发 AssertionError 然后被捕获
        '''
        
        def __init__(self, error_type):
            '''初始化
            '''
            self.error_type = error_type    #保存错误类型

        def __enter__(self):
            '''进入 with 语句
            '''
            return TestCase()    #返回 TestCase 实例
        
        def __exit__(self, type, value, traceback):
            '''退出 with 语句'''
            if type is self.error_type:    #判断异常类型是否一致
                return True    #是返回 True, 
                # 表示是这个异常已经成功处理了, 
                # Python 解释器不会将这个错误打印出来
            else:    #类型不对或为 None (没有异常)
                raise AssertionError('{} != {}'.format(type, self.error_type))    #引发 AssertionError 断言异常
    
    def __run__(self):
        '''运行测试'''
        for test_function in self._tests_list:    #遍历从元类那里得来的函数列表
            self._func_name = test_function.__name__    #将 _func_name 设为调用函数的名称
            with self:    #进入上下文管理器
                test_function(self)    #执行函数
    
    def __enter__(self):
        '''进入 with 语句
        '''
        #打印位置信息
        self._printf(self._func_name,     #函数名称
            ' (from ',
            self.__class__.__module__ , '.', self.__class__.__name__,    #模块名字
            ') ...',
            sep='', end=''    #打印的参数
        )
        #打印出来就像这样 test_value (from __main__.Test) ...
        return self
    
    def __exit__(self, type, value, traceback):
        '''退出 with 语句'''
        if type is None:    #如果没有异常
            self._printf('ok')    #通过
            self.oks += 1    #将通过计数增加一
            return False    #返回
        elif type is AssertionError:    #如果断言失败
            self._printf('failures')    #断言失败
            self._printf('Traceback (most recent call last):')    #打印回溯信息
            self._printf('    Test "%s" in "%s"'%(self._func_name, self.__class__.__name__))    #大概位置
            self._printf('        ...')    #具体的代码段省略，因为判断位置太复杂了
            self._printf('AssertionError:', value)    #错误类型
            self._printf()    #空行
            self.failures += 1    #将断言失败次数增加一
            return True    #已处理这个错误
        else:    #如果错误
            self._printf('error')    #错误
            self._printf('Traceback (most recent call last):')    #打印回溯信息
            self._printf('    Test "%s" in "%s"'%(self._func_name, self.__class__.__name__))    #大概位置
            self._printf('        ...')    #同上
            self._printf(type.__name__, ': ', value, sep='')    #打印错误类型
            self._printf()    #空行
            self.errors += 1    #将报错计数增加一
            return True    #同上
        
    def __str__(self):
        '''打印时输出的内容'''
        string = '<{name} object ok=\'{ok}\' failure=\'{failure}\' error=\'{error}\'>'    #模板字符串
        return string.format(name=self.__class__.__name__, ok=self.oks, failure=self.failures, error=self.errors)    #填充信息，返回
    
    __repr__ = __str__    #用 >>> 输出也和打印时输出的一样

def run_tests(*iterables, file=None):
    '''批量运行测试
    
    参数:
        *iterables  (list[Testcase]) 一个包含参数对象的列表
        file  (object) 输出对象，要有 write 方法
    
    返回:
        一个三元组, 为 (通过次数, 断言失败次数, 报错次数)'''
    if file is None:    #判断输出对象是否有指定
        file = sys.stdout    #没有就指定为标准输出
    #初始化状态次数
    ok = 0    #通过次数
    failure = 0    #断言失败次数
    error = 0    #报错次数
    for iterable in iterables:    #遍历测试列表
        #判断是否是测试用例
        assert issubclass(iterable, TestCase), \
            '\'%s\' is not a test case.'%iterable.__name__    #不是报错
        test = iterable(stream=file)    #初始化测试对象
        test.__run__()    #运行测试

        #统计状态次数
        ok += test.oks
        failure += test.failures
        error += test.errors
    
    file.write('-' * 40)    #分割线
    file.write('\nFinish %s Test.\n'%len(iterables))    #结束语
    file.write('Result(ok={ok}, failure={failure}, error={error})\n'.format(ok=ok, failure=failure, error=error))    #状态信息
    return ok, failure, error    #返回

def _test(old_test=False):
    """测试"""            

    class Square_AreaTest(TestCase):    #正方形面积类测试
        def test_output(self):    #测试输出
            test1 = square_area(a=2)
            self.assertEqual(test1._value, 4)    #测试用例1  
            test2 = square_area(a=3)
            self.assertEqual(test2._value, 9)    #测试用例2  
            test3 = square_area(a=4)
            self.assertEqual(test3._value, 16)    #测试用例3  


    class Square_PerimeterTest(TestCase):    #正方形周长类测试
        def test_output(self):    #测试输出
            test1 = square_perimeter(a=2)
            self.assertEqual(test1._value, 8)    #测试用例1
            test2 = square_perimeter(a=3)
            self.assertEqual(test2._value, 12)    #测试用例2
            test3 = square_perimeter(a=4)
            self.assertEqual(test3._value, 16)    #测试用例3


    class Rectangle_AreaTest(TestCase):    #长方形面积类测试
        def test_output(self):    #测试输出
            test1 = rectangle_area(a=2, b=3)
            self.assertEqual(test1._value, 6)    #测试用例1
            test2 = rectangle_area(a=3, b=5)
            self.assertEqual(test2._value, 15)    #测试用例2
            test3 = rectangle_area(a=7, b=8)
            self.assertEqual(test3._value, 56)    #测试用例3


    class Rectangle_PerimeterTest(TestCase):    #长方形周长类测试
        def test_output(self):    #测试输出
            test1 = rectangle_perimeter(a=2, b=3)
            self.assertEqual(test1._value, 10)    #测试用例1
            test2 = rectangle_perimeter(a=2, b=5)
            self.assertEqual(test2._value, 14)    #测试用例2
            test3 = rectangle_perimeter(a=5, b=10)
            self.assertEqual(test3._value, 30)    #测试用例3


    class Triangle_AreaTest(TestCase):    #三角形面积类测试
        def test_output(self):    #测试输出
            test1 = triangle_area(a=2, h=3)
            self.assertEqual(test1._value, 3.0)    #测试用例1
            test2 = triangle_area(a=3, h=4)
            self.assertEqual(test2._value, 6.0)    #测试用例2
            test3 = triangle_area(a=5, h=10)
            self.assertEqual(test3._value, 25.0)    #测试用例3


    class Trapezoid_AreaTest(TestCase):    #梯形面积类测试
        def test_output(self):    #测试输出
            test1 = trapezoid_area(a=2, b=3 ,h=4)
            self.assertEqual(test1._value, 10.0)    #测试用例1
            test2 = trapezoid_area(a=1, b=1, h=1)
            self.assertEqual(test2._value, 1.0)    #测试用例2
            test3 = trapezoid_area(a=10, b=20, h=30)
            self.assertEqual(test3._value, 450.0)    #测试用例3


    class Parallelogram_AreaTest(TestCase):    #平行四边形面积类测试
        def test_output(self):    #测试输出
            test1 = parallelogram_area(a=2, h=3)
            self.assertEqual(test1._value, 6)    #测试用例1
            test2 = parallelogram_area(a=3, h=4)
            self.assertEqual(test2._value, 12)    #测试用例2
            test3 = parallelogram_area(a=4, h=5)
            self.assertEqual(test3._value, 20)    #测试用例3


    class Parallelogram_PerimeterTest(TestCase):    #平行四边形周长类测试
        def test_output(self):    #测试输出
            test1 = parallelogram_perimeter(a=1, h=2)
            self.assertEqual(test1._value, 6)    #测试用例1
            test2 = parallelogram_perimeter(a=2, h=3)
            self.assertEqual(test2._value, 10)    #测试用例2
            test3 = parallelogram_perimeter(a=3, h=4)
            self.assertEqual(test3._value, 14)    #测试用例3


    class Cube_Surface_AreaTest(TestCase):    #正方体表面积类测试
        def test_output(self):    #测试输出
            test1 = cube_surface_area(a=6)
            self.assertEqual(test1._value, 216)    #测试用例1
            test2 = cube_surface_area(a=4)
            self.assertEqual(test2._value, 96)    #测试用例2
            test3 = cube_surface_area(a=2)
            self.assertEqual(test3._value, 24)    #测试用例3


    class Cube_VolumeTest(TestCase):    #正方体体积类测试
        def test_output(self):    #测试输出
            test1 = cube_volume(a=6)
            self.assertEqual(test1._value, 216)    #测试用例1
            test2 = cube_volume(a=4)
            self.assertEqual(test2._value, 64)    #测试用例2
            test3 = cube_volume(a=2)
            self.assertEqual(test3._value, 8)    #测试用例3


    class Sum_Of_Cube_EdgesTest(TestCase):    #正方体棱长总和类测试
        def test_output(self):    #测试输出
            test1 = sum_of_cube_edges(a=6)
            self.assertEqual(test1._value, 72)    #测试用例1
            test2 = sum_of_cube_edges(a=4)
            self.assertEqual(test2._value, 48)    #测试用例2
            test3 = sum_of_cube_edges(a=2)
            self.assertEqual(test3._value, 24)    #测试用例3


    class Cuboid_Surface_AreaTest(TestCase):    #长方体表面积类测试
        def test_output(self):    #测试输出
            test1 = cuboid_surface_area(a=2, b=3, h=4)
            self.assertEqual(test1._value, 52)    #测试用例1
            test2 = cuboid_surface_area(a=3, b=4, h=5)
            self.assertEqual(test2._value, 94)    #测试用例2
            test3 = cuboid_surface_area(a=10, b=20, h=30)
            self.assertEqual(test3._value, 2200)    #测试用例3


    class Cuboid_VolumeTest(TestCase):    #长方体体积类测试
        def test_output(self):    #测试输出
            test1 = cuboid_volume(a=1, b=2, h=3)
            self.assertEqual(test1._value, 6)    #测试用例1
            test2 = cuboid_volume(a=2, b=3, h=4)
            self.assertEqual(test2._value, 24)    #测试用例2
            test3 = cuboid_volume(a=10, b=20, h=30)
            self.assertEqual(test3._value, 6000)    #测试用例3


    class Sum_Of_Cuboid_EdgesTest(TestCase):    #长方体棱长总和类测试
        def test_output(self):    #测试输出
            test1 = sum_of_cuboid_edges(a=2, b=3, h=4)
            self.assertEqual(test1._value, 36)    #测试用例1
            test2 = sum_of_cuboid_edges(a=3, b=4, h=5)
            self.assertEqual(test2._value, 48)    #测试用例2
            test3 = sum_of_cuboid_edges(a=10, b=20, h=30)
            self.assertEqual(test3._value, 240)    #测试用例3


    class Circle_PerimeterTest(TestCase):    #圆形周长类测试
        def test_output(self):    #测试输出
            de_decimal = lambda decimal_object: float(str(decimal_object))
            test1 = circle_perimeter(r=1)
            self.assertEqual(de_decimal(test1._value), 6.28)    #测试用例1
            test2 = circle_perimeter(r=2)
            self.assertEqual(de_decimal(test2._value), 12.56)    #测试用例2
            test3 = circle_perimeter(r=3)
            self.assertEqual(de_decimal(test3._value), 18.84)    #测试用例3


    class Circle_AreaTest(TestCase):    #圆形面积类测试
        def test_output(self):    #测试输出
            de_decimal = lambda decimal_object: float(str(decimal_object))
            test1 = circle_area(r=1)
            self.assertEqual(de_decimal(test1._value), 3.14)    #测试用例1
            test2 = circle_area(r=2)
            self.assertEqual(de_decimal(test2._value), 12.56)    #测试用例2
            test3 = circle_area(r=3)
            self.assertEqual(de_decimal(test3._value), 28.26)    #测试用例3


    class MarketingTest(TestCase):    #营销号生成器类测试
        def test_output(self):    #测试输出
            result = '{k}{i}是怎么回事呢？{k}相信大家都很熟悉了，但是{k}{i}是怎么回事呢？下面就让小编大家一起带大家了解一下吧。{k}{i}，其实就是{a}。大家可能会惊讶{k}怎么会{i}呢？但事实就是这样，小编也感到非常惊讶。这就是关于{k}{i}的事情了，大家有什么想法呢，欢迎在评论区告诉小编一起讨论哦！'
            test1 = Marketing(keyword="我",incident="睡觉",another="我困啦")
            self.assertEqual(test1(), result.format(k="我",i="睡觉",a="我困啦"))    #测试用例1
            test2 = Marketing(keyword="你",incident="玩水",another="你无聊")
            self.assertEqual(test2(), result.format(k="你",i="玩水",a="你无聊"))    #测试用例2
            test3 = Marketing(keyword="他",incident="皮",another="他无聊")
            self.assertEqual(test3(), result.format(k="他",i="皮",a="他无聊"))    #测试用例3

    tests_list = [    #单元测试列表
        Square_AreaTest,
        Square_PerimeterTest,
        Rectangle_AreaTest,
        Rectangle_PerimeterTest,
        Triangle_AreaTest,
        Trapezoid_AreaTest,
        Parallelogram_AreaTest,
        Parallelogram_PerimeterTest,
        Cube_Surface_AreaTest,
        Cube_VolumeTest,
        Sum_Of_Cube_EdgesTest,
        Cuboid_Surface_AreaTest,
        Cuboid_VolumeTest,
        Sum_Of_Cuboid_EdgesTest,
        Circle_PerimeterTest,
        Circle_AreaTest,
        MarketingTest
    ]
    
    if old_test:    #旧的测试
        print("---测试---")
        a = square(a=1)
        print(a.周长)
        b = rectangle(a=4,b=6)
        print(b.area)
        print(rectangle(a=2,b=3).面积)
        t = cuboid_volume(a=1,b=2.5,h=5.5)
        print(t)
        d = cuboid_surface_area(a=1,b=2.5,h=5.5)
        print(d)
        f = sum_of_cuboid_edges(a=1,b=2,h=3)
        print(f)
        for i,j in parameter(a=1.1):
            print(i,j)
        class b(Graphical):
            formula = "cos(sin(a))"
            args = parameter("a")
            extension = [
                Extension("sin",__import__("math").sin),
                Extension("cos",__import__("math").cos)
            ]
        print(b(a=1))
        #print(b.buildtoJSON())
        class a(Integrated_Graphical):
            def getresult(self,name):
                if name == "d":
                    return cube_volume(**self.kwargs)
        e = a(a=2)
        print(e.d)
        print(e("d"))
        test = cuboid(h=1,a=2,b=1).表面积
        print(test)
        test1 = cube(a=7).体积
        print(test1)
        print(compute("sin(1)",sin=__import__("math").sin))
        print(triangle(a=5,h=3).面积)
        #help(长方形)
        print(正方形面积(a=2))
        print(正方体(a=5).表面积)
        print(circle_perimeter(r=5))
        print(circle_area(r=5))
        print(cube_volume(a=2))
        print(trapezoid(a=2,b=3,h=4).area)
        print(parallelogram(a=2,h=3).perimeter)
        print(平行四边形(a=2,h=3).area)
        print(圆形(r=10).周长)
        print(圆形(r=16).面积)
        print(平行四边形(a=10,h=5).面积)
        class a(Graphical):
            def plugin(self):
                pass
            def c():
                return 1 + 1
        print(a.c())
        print(cuboid(a=5,b=4,h=4).表面积)
        print(cube_volume.buildtoJSON())
        a = loadfromJSON('{"name": "a","formula": "1+a+2","args": {"a": "a"}}')
        print(a(a=3))
        print(Marketing(keyword="李琰",incident="睡觉",another="它困啦"))
    else:
        run_tests(*tests_list)

#sys.exit(_test())

#段子
class Marketing(Graphical_str_compose):
    """营销号生成器
    keyword --> 主体
    incident --> 事件
    another --> 另一种说法"""
    formula = """
    ki是怎么回事呢？k相信大家都很熟悉了，但是
    ki是怎么回事呢？下面就让小编大家一起带大家了解一下吧。
    ki，其实就是a。大家可能会惊讶k怎么会i呢？
    但事实就是这样，小编也感到非常惊讶。
    这就是关于ki的事情了，大家有什么想法呢，欢迎在评论区告诉小编一起讨论哦！
    """.replace("\n","").replace(" ","")
    args = parameter(keyword="k",incident="i",another="a")


@unique
class formula_enum(Enum):
    #公式对应的类
    正方形面积 = square_area
    正方形周长 = square_perimeter
    长方形面积 = rectangle_area
    长方形周长 = rectangle_perimeter
    三角形面积 = triangle_area
    梯形面积 = trapezoid_area
    平行四边形面积 = parallelogram_area
    平行四边形周长 = parallelogram_perimeter
    正方体表面积 = cube_surface_area
    正方体体积 = cube_volume
    正方体棱长总和 = sum_of_cube_edges
    长方体表面积 = cuboid_surface_area
    长方体体积 = cuboid_volume
    长方体棱长总和 = sum_of_cuboid_edges
    圆形周长 = circle_perimeter
    圆形面积 = circle_area
    营销号生成器 = Marketing

formula_dict = {
    "正方形面积":square_area,
    "正方形周长":square_perimeter,
    "长方形面积":rectangle_area,
    "长方形周长":rectangle_perimeter,
    "三角形面积":triangle_area,
    "梯形面积":trapezoid_area,
    "平行四边形面积":parallelogram_area,
    "平行四边形周长":parallelogram_perimeter,
    "正方体表面积":cube_surface_area,
    "正方体体积":cube_volume,
    "正方体棱长总和":sum_of_cube_edges,
    "长方体表面积":cuboid_surface_area,
    "长方体体积":cuboid_volume,
    "长方体棱长总和":sum_of_cuboid_edges,
    "圆形周长":circle_perimeter,
    "圆形面积":circle_area,
    "营销号生成器":Marketing
}

formula_list = [    #函数列表
    square_area,
    square_perimeter,
    rectangle_area,
    rectangle_perimeter,
    triangle_area,
    trapezoid_area,
    parallelogram_area,
    parallelogram_perimeter,
    cube_surface_area,
    cube_volume,
    sum_of_cube_edges,
    cuboid_surface_area,
    cuboid_volume,
    sum_of_cuboid_edges,
    circle_perimeter,
    circle_area,
    Marketing
]

def _builtin_formula_to_json(indent=4):
    """
    将内置公式构建成JSON文件
    
    参数:
        indent (int)    格式化JSON的缩进
    返回:
        一个JSON字符串
    """
    builtin_dict = {}
    for graphical_formula in formula_list:
        if hasattr(graphical_formula,"extension"):
            continue
        json_data = graphical_formula.buildtoJSON()
        data = loads(json_data)
        builtin_dict[_built_cn_en_table[data['name']]] = data
    json = dumps(builtin_dict,ensure_ascii=False,indent=indent)
    return json


formula_name = [    #公式的名称
    "正方形面积",
    "正方形周长",
    "长方形面积",
    "长方形周长",
    "三角形面积",
    "梯形面积",
    "平行四边形面积",
    "平行四边形周长",
    "正方体表面积",
    "正方体体积",
    "正方体棱长总和",
    "长方体表面积",
    "长方体体积",
    "长方体棱长总和",
    "圆形周长",
    "圆形面积",
    "营销号生成器"
]

#这里是与用户交互的部分

#这是可复用部分
class printlist_metaclass(type):
    """这个是printlist类的元类"""
    def __new__(cls,name,bases,classdict):
        if name == "printlist":    #如果是printlist本身，直接返回
            return type.__new__(cls,name,bases,classdict)
        key_value = {}    #创建字典
        for key in classdict:    #遍历属性
            if key == "__module__":    #如果是内置属性，跳过
                continue
            elif key == "__qualname__":
                continue
            else:    #如果是其他类型
                if not isinstance(key,list):    #判断数据的类型
                    key_value[key] = classdict[key]    #解析参数
                else:
                    raise ValueError("值的类型必须是列表")    #引发错误
        classdict["key"] = key_value    #保存解析后的数据
        return type.__new__(cls,name,bases,classdict)    #构建类


class printlist(object,metaclass=printlist_metaclass):
    """用继承的方式创建列表
    使用这个类可以轻松打印出像pip list那样的列表
    如：
    Package    Version
    ---------- -------
    pip        20.1.1
    setuptools 46.4.0
    wheel      0.34.2
    """
    def __init__(self):
        """初始化打印列表"""
        self.title = []    #初始化
        self.args = []
        for key,value in self.key.items():    #解析标题和选项
            self.title.append(key)    #加入各自的列表
            self.args.append(value)
        self.item = list(self.packaging(*self.args))    #打包数据
    
    def packaging(self,*iterables):
        '''将两个或多个迭代器打包
        类似于 zip 函数
        '''
        iterables = [list(iterable) for iterable in iterables]    #将所有对象都转为列表
        long_list_length = 0    #初始化最大长度
        for iterable in iterables:    #迭代迭代器
            if len(iterable) >= long_list_length:    #如果长度大于最大长度
                long_list_length = len(iterable)    #将最大长度设为这个列表的长度
        result = []    #初始化返回结果
        for index in range(long_list_length):    #重复最大长度次
            pack = []    #每层的元素列表
            for iterable in iterables:    #迭代每个列表
                try:    #获取元素
                    #获取每个列表的对应的元素
                    value = iterable[index]
                except IndexError:    #如果报错
                    value = ''    #将内容设为空字符串
                finally:    #最后
                    pack.append(value)    #进入元素列表
            pack = tuple(pack)    #将列表转为元组
            result.append(pack)    #加入结果列表
        return result    #返回结果列表


    def get(self):
        result = []    #初始化结果列表
        #标题
        result.append("\t".join(self.title))
        #分割线
        division = []    #初始化
        for index in range(len(self.title)*2 - 1):
            try:
                division.append("--" * len(self.title[index]))
            except IndexError as identifier:
                division.append("-----")
        result.append("".join(division))
        #内容
        for line in self.item:
            body = []
            for char in line:
                body.append(str(char) + "\t")
            result.append("".join(body))
        return "\n".join(result)

    def __str__(self):
        return self.get()

def _print_id_key():
    """打印图形id列表"""
    class formula_object(printlist):
        圆形ID = list(range(1,18))
        对应的公式 = [
            "正方形面积",
            "正方形周长",
            "长方形面积",
            "长方形周长",
            "三角形面积",
            "梯形面积",
            "平行四边形面积",
            "平行四边形周长",
            "正方体表面积",
            "正方体体积",
            "正方体棱长总和",
            "长方体表面积",
            "长方体体积",
            "长方体棱长总和",
            "圆形周长",
            "圆形面积",
            "营销号生成器"
        ]
    print(formula_object().get())


#GUI界面

def _tkinter_main():
    """启动窗口"""
    class window(tkinter.Frame):
        """用户图形界面"""

        def __init__(self,master: tkinter.Tk=None):
            self.master = master    #初始化，保存参数
            self.master.title("图形")    #设置标题
            tkinter.Frame.__init__(self,self.master)    #调用原来的初始化函数
            #初始化变量
            self.match = tkinter.StringVar()
            self.match.set("")
            #调用方法
            self.title()
            self.label()
            #循环
            self.pack()
            self.master.mainloop()

        def title(self):
            """设置标题"""
            tkinter.Label(self,text="图形",font=("Arial",20)).pack()    #要大大大的标题

        def label(self):
            """摆放内容"""
            enter = tkinter.Frame(self)    #创建一个框架
            #说明文本
            ttk.Label(enter,text="图形:").grid(row=0,column=0)
            ttk.Label(enter,text="参数:").grid(row=1,column=0)
            #下拉框和参数输入框
            self.formula = ttk.Combobox(enter,value=formula_name,state="readonly")
            self.formula.current(0)
            self.formula.grid(row=0,column=1,columnspan=2)
            self.args = ttk.Entry(enter,show=None)
            self.args.grid(row=1,column=1,columnspan=2)
            enter.pack()

            def callback(self=self):
                """计算回调函数"""
                formula = formula_enum[self.formula.get()].value    #获取对应的函数
                compute_args = self.args.get().split(' ')
                if len(compute_args) % 2 != 0:    #如果参数的个数不是2的倍数
                    raise TypeError("参数错误")    #引发错误
                argv = {}    #参数字典
                iterable = 0    #循环变量
                for char in range(int(len(compute_args) / 2)):    #循环
                    argv[compute_args[iterable]] = compute_args[iterable + 1]    #解析参数并放到字典
                    iterable += 2    #自增
                result = formula(**argv)
                self.match.set(result)    #设置显示变量
            #计算按钮
            ttk.Button(self,text="计算",command=callback).pack()
            #显示结果
            group = ttk.LabelFrame(self,text="结果")
            ttk.Label(group,textvariable=self.match).pack()
            group.pack()

            tkinter.Label(self,text="参数格式:\n参数名称 参数值 参数名称 参数值\n例：a 3 b 4").pack()    #帮助

    root = tkinter.Tk()
    window(root)


#命令行交互界面

#这里使用了自己的命令行框架
#其实有一个标准库 cmd 就是一个命令行框架
#但是我想自己定义输出
#所以写了一个类似的框架

class Cmd(object):
    '''用于编写面向行的命令解释器的简单框架

    这是一个简单的命令行交互框架，
    用于编写一些声明式的程序
    '''

    #一些配置
    headers = ''    #头部信息
    prompt = '(Cmd) '    #提示符

    #代码部分
    def __init__(self, stdin=None, stdout=None, stderr=None):
        '''初始化框架
        
        参数:
            stdin  (like-file) 从某个文件获取输入
            stdout (like-file) 输出到某个文件
            stderr (like-file) 异常输出到文件中
        
        注意:
            如果你没有听说过 一切皆文件 的概念，请不要指定上面三个参数
        '''
        if stdin is None:    #判断 stdin 是否为空
            self.stdin = sys.stdin    #是，指定为标准输入
        else:    #否则，
            self.stdin = stdin    #保存参数
        
        if stdout is None:    #判断 stdout 是否为空
            self.stdout = sys.stdout    #是，指定为标准输出
        else:    #否则，
            self.stdout = stdout    #保存参数
        
        if stderr is None:    #判断 stderr 是否为空
            self.stderr = sys.stderr    #是，指定为标准异常输出
        else:    #否则，
            self.stderr = stderr    #保存参数
        
        self.history = []    #初始化历史命令列表
        
    def preloop(self):
        '''开始事件循环前的回调函数
        '''
        pass

    def stoploop(self):
        '''结束事件循环后的回调函数
        '''
        pass

    def precmd(self, line):
        '''开始解析命令前的回调函数
        '''
        return line    #一定要返回
    
    def postcmd(self):
        '''结束执行命令后的回调函数
        '''
        pass

    def emptyline(self):
        '''输入是空行的回调函数
        '''
        pass

    def _parse_cmd(self, line):
        '''解析命令行
        '''
        #分词
        line = line + ' '    #加一个空格
        result = []    #初始化结果
        chars = ''    #初始化临时字符串
        for char in line:    #遍历输入的每个字符
            if char == ' ' and chars == '':    #遇到空格和临时字符串是空
                continue    #跳过
            elif char == ' ' and chars != '':    #遇到空格和临时字符串有东西
                result.append(chars)    #将临时字符串加入结果
                chars = ''    #清空临时字符串
            else:    #否则
                #这会匹配普通字符
                chars = chars + char    #加到临时字符串
        if len(result) == 0:   #如果结果字符串是空列表
            return None    #返回 空(None)
        #否则
        return result    #返回结果
    
    def onecmd(self, arg):
        '''执行命令
        '''
        execute = arg[0]    #命令名称
        execute = 'do_' + execute    #加上 do_ 前缀就是方法名
        args = arg[slice(1, len(arg))]   #参数
        function = getattr(self, execute, self.unknown_command)    #获取函数方法
        #默认是 unknown_command 方法
        if function == self.unknown_command:    #如果是 unknown_command 方法
            return function(execute)    #传入名称
        else:    #是普通方法
            return function(*args)   #执行命令
    
    def unknown_command(self, execute):
        '''未知命令
        '''
        print('unknown command \'%s\''%execute[8:], file=self.stderr)    #打印一条信息

    
    def do_help(self, *args):
        '''显示帮助
        '''
        if not args:    #如果没有参数
            #就打印全部方法
            if self.__doc__ is not None:    #如果有类文档
                print(self.__doc__, file=self.stdout)    #打印类文档
            print(file=self.stdout)    #空行
            for k, v in self.__class__.__dict__.items():    #遍历方法字典
                if k.startswith('do_'):    #如果开头是 do_
                    #就是命令方法
                    print(k[8:], '\t', end='', file=self.stdout)    #打印名称 + 一个制表符
                    if v.__doc__ is not None:    #如果函数有文档
                        print(v.__doc__, end='', file=self.stdout)    #打印函数文档
                    print(file=self.stdout)    #空行
        else:    #有参数
            #打印指定的目录
            for arg in args:   #遍历参数
                if hasattr(self, 'do_' + arg):    #如果有这个方法
                    print(arg, end='\t', file=self.stdout)   #打印名称 + 一个制表符
                    doc = getattr(self, 'do_'+arg).__doc__    #获取文档
                    if doc:    #如果文档不是空
                        print(doc, file=self.stdout)    #打印文档
                else:    #否则
                    #输入的命令不存在
                    print('没有这个命令 \'%s\''%args, file=self.stdout)    #打印一条信息

    def mainloop(self):
        '''启动事件循环
        '''
        try:    #进入
            self.preloop()    #执行回调函数
            print(self.headers, file=self.stdout)
            while True:
                line = input(self.prompt)   #获取输入
                line = self.precmd(line)    #执行回调函数
                if not line:    #如果是空行
                    self.emptyline()    #执行回调函数
                    continue    #跳过
                else:    #否则
                    #去掉前面和后面的空格
                    line = line.strip(' ')    #清理
                arg = self._parse_cmd(line)    #预处理命令，分词
                if arg is None:    #如果分词后是空
                    continue    #跳过
                output = self.onecmd(arg)    #执行命令
                self.postcmd()    #执行回调函数
                if output is True:    #如果函数返回的是 True
                    break    #跳过
                self.stdout.write('\n')    #空行
                self.stdout.flush()    #刷新
                #下一轮循环
        except KeyboardInterrupt:    #如果遇到 KeyboardInterrupt
            #也就是按下 Ctrl+C
            pass   #退出
        finally:    #结束
            self.stoploop()    #执行回调函数

class shell(Cmd):
    '''命令行交互界面
    '''

    headers = 'Graphical Shell'
    prompt = "Graphical> "    #提示符

    def do_list(self, *arg):
        '''打印id
        '''
        _print_id_key()
    
    def do_compute(self, *arg):
        '''计算
        '''
        compute_id = int(arg[0])    #获取图形id
        compute_args = arg[1:]    #获取参数
        if len(compute_args) % 2 != 0:    #如果参数的个数不是2的倍数
            raise TypeError("参数错误")    #引发错误
        kwargs = {}    #参数字典
        iterable = 0    #循环变量
        for char in range(int(len(compute_args) / 2)):    #循环
            kwargs[compute_args[iterable]] = compute_args[iterable + 1]    #解析参数并放到字典
            iterable += 2    #自增
        try:
            print(formula_list[compute_id - 1](**kwargs))    #输出结果
        except IndexError:
            raise IndexError("不是有效的图形")    #如果超出索引，报错
        
    def do_exit(self, *arg):
        '''退出
        '''
        print('bye')   #打印一条信息
        return True    #按照和Cmd类的小约定，如果返回True就退出

    def emptyline(self):
        '''如果输入空行，调用这个
        '''
        print()    #打印一个空行

    def unknown_command(self,line):
        '''如果无此命令，调用这个
        '''
        print("'%s' 不是有效的命令"%line)

    def do_help(self, *arg):
        '''帮助
        '''
        print(
            """
命令:
    list
        打印所有可用的公式
    compute 
        计算公式
        参数:
            compute id key value [arg ...]
            """
        )

def _run_shell():
    """启动交互式shell"""
    try:
        a = shell()    #实例化
        a.mainloop()    #进入事件循环
    except KeyboardInterrupt:    #如果遇到 KeyboardInterrupt
        #也就是按下 Ctrl+C
        pass    #跳过

#命令行帮助
HELP = '''
选项: graphical [-h] [-t | -s | -g | -j | -ot] [-l] [id] [(key value) [(key value) ...]]

选项参数:
  -h, --help       显示帮助并退出
  -t, --test       开始测试
  -s, --shell      启动交互式Shell
  -g, --gui        打开图形界面
  -j, --json       将内置公式导出到JSON
  -ot, --old-test  开始旧的测试

  -l, --list       列出所有可用的图形公式
  id               图形ID
  arg              计算图形公式 格式：**参数
'''

def _command(arg):
    """命令行参数开关"""

    #这里使用 Python 标准库 argparse
    parse = argparse.ArgumentParser(description="图形", prog="graphical", add_help=False)    #生成ArgumentParser对象

    parse.add_argument('-h', '--help',action='store_true', help='显示帮助并退出')    #添加帮助

    option = parse.add_mutually_exclusive_group()
    option.add_argument("-t","--test",action="store_true",help="开始测试")
    option.add_argument("-s","--shell",action="store_true",help="启动交互式Shell")    #添加启动shell
    option.add_argument("-g","--gui",action="store_true",help="打开图形界面")
    option.add_argument("-j","--json",action="store_true",help="将内置公式导出到JSON")
    option.add_argument("-ot","--old-test",action="store_true",help="开始旧的测试")

    group = parse.add_argument_group()
    group.add_argument("-l","--list",help="列出所有可用的图形公式",action="store_true") #添加list参数
    group.add_argument("id",help="图形ID",type=int,nargs="?",default=1)    #添加图形参数
    group.add_argument("arg",help="计算图形公式 格式：**参数",nargs="*")    #添加图形公式的参数

    parse_args = parse.parse_args(arg)    #解析参数

    if parse_args.help:
        #打印帮助
        print(HELP)    #打印

    elif parse_args.shell:    
        #启动shell
        return main.shell()    #从入口点启动
    
    elif parse_args.test:
        #单元测试
        return main.test()    #从入口点启动
    
    elif parse_args.gui:
        #图形界面
        return main.gui()    #从入口点启动
    
    elif parse_args.json:
        json_str = _builtin_formula_to_json()    #获取JSON字符串
        with open("graphical.json",'w',encoding="utf-8") as json_file:    #打开文件
            json_file.write(json_str)    #写入文件
        return json_str    #结束
    
    elif parse_args.old_test:    
        #老的测试模块
        return _test(old_test=True)    #启动老的测试

    elif parse_args.list:    
        #图形ID列表
        _print_id_key()    #调用函数打印
    
    elif parse_args.arg:    #否则计算图形公式
        compute_id = parse_args.id    #获取图形id
        compute_args = vars(parse_args)['arg']    #获取参数
        if len(compute_args) % 2 != 0:    #如果参数的个数不是2的倍数
            raise TypeError("参数错误")    #引发错误
        kwargs = {}    #参数字典
        iterable = 0    #循环变量
        for char in range(int(len(compute_args) / 2)):    #循环
            kwargs[compute_args[iterable]] = compute_args[iterable + 1]    #解析参数并放到字典
            iterable += 2    #自增
        try:
            print(formula_list[compute_id - 1](**kwargs))    #输出结果
        except IndexError:
            raise IndexError("不是有效的图形")    #如果超出索引，报错

class main(object):
    '''程序入口点
    '''
    def __init__(self):
        self.args = sys.argv    #保存变量

    def _parse(self):
        '''解析参数列表
        '''
        first = True    #初始化
        parameter = []
        for char in self.args:    #循环
            if first:   #判断是否是第一个参数
                self.file_name = char
                first = False    #后面的都为参数
            else:
                parameter.append(char)
        return parameter    #返回参数
    
    @classmethod
    def command(cls):
        '''命令行参数解析
        '''
        return _command(cls()._parse())
    
    @staticmethod
    def gui():
        '''图形用户界面
        '''
        try:
            import tkinter    #Tk/Tcl接口
            from tkinter import ttk    #tkinter ttk扩展
        except ImportError:    #遇到导入错误

            #其实 tkinter 是 Python 的可选标准库
            #安装时可以取消安装
            #另外 Python 的 ZIP 发行版是没有 tkinter 的

            import warnings    #导入 warnings 模块
            warnings.warn("无法导入Tk/Tcl接口，请确保已正确安装tkinter",     #如果你没有安装 Tkinter
                RuntimeWarning)    #给你个警告
        else:    #如果一切正常
            globals()['tkinter'] = tkinter    #将tkinter保存到全局变量
            globals()['ttk'] = ttk    #将ttk保存到全局变量
            return _tkinter_main()    #运行入口函数
    
    @staticmethod
    def shell():
        '''命令行交互提示符'''
        return _run_shell()
    
    @staticmethod
    def test():
        '''测试'''
        return _test()

if __name__ == "__main__":
    main()
    main.command()

# os.system(sys.argv[0] + " 17 keyword 李琰 incident 睡觉 another 他困啦")
