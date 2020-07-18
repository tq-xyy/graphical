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
import unittest  # 单元参数
from cmd import Cmd  # 交互式命令行框架
from collections.abc import Iterable  # 导入迭代器基类
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
            if isinstance(_extension,Iterable):    #判断是否是一个可迭代对象
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
            


def _test(old_test=False):
    """测试"""
    class Square_AreaTest(unittest.TestCase):    #正方形面积类测试
        def test_value(self):    #测试输出
            test1 = square_area(a=2)
            self.assertEqual(test1._value, 4)    #测试用例1  
            test2 = square_area(a=3)
            self.assertEqual(test2._value, 9)    #测试用例2  
            test3 = square_area(a=4)
            self.assertEqual(test3._value, 16)    #测试用例3  


    class Square_PerimeterTest(unittest.TestCase):    #正方形周长类测试
        def test_value(self):    #测试输出
            test1 = square_perimeter(a=2)
            self.assertEqual(test1._value, 8)    #测试用例1
            test2 = square_perimeter(a=3)
            self.assertEqual(test2._value, 12)    #测试用例2
            test3 = square_perimeter(a=4)
            self.assertEqual(test3._value, 16)    #测试用例3


    class Rectangle_AreaTest(unittest.TestCase):    #长方形面积类测试
        def test_value(self):    #测试输出
            test1 = rectangle_area(a=2, b=3)
            self.assertEqual(test1._value, 6)    #测试用例1
            test2 = rectangle_area(a=3, b=5)
            self.assertEqual(test2._value, 15)    #测试用例2
            test3 = rectangle_area(a=7, b=8)
            self.assertEqual(test3._value, 56)    #测试用例3


    class Rectangle_PerimeterTest(unittest.TestCase):    #长方形周长类测试
        def test_value(self):    #测试输出
            test1 = rectangle_perimeter(a=2, b=3)
            self.assertEqual(test1._value, 10)    #测试用例1
            test2 = rectangle_perimeter(a=2, b=5)
            self.assertEqual(test2._value, 14)    #测试用例2
            test3 = rectangle_perimeter(a=5, b=10)
            self.assertEqual(test3._value, 30)    #测试用例3


    class Triangle_AreaTest(unittest.TestCase):    #三角形面积类测试
        def test_value(self):    #测试输出
            test1 = triangle_area(a=2, h=3)
            self.assertEqual(test1._value, 3.0)    #测试用例1
            test2 = triangle_area(a=3, h=4)
            self.assertEqual(test2._value, 6.0)    #测试用例2
            test3 = triangle_area(a=5, h=10)
            self.assertEqual(test3._value, 25.0)    #测试用例3


    class Trapezoid_AreaTest(unittest.TestCase):    #梯形面积类测试
        def test_value(self):    #测试输出
            test1 = trapezoid_area(a=2, b=3 ,h=4)
            self.assertEqual(test1._value, 10.0)    #测试用例1
            test2 = trapezoid_area(a=1, b=1, h=1)
            self.assertEqual(test2._value, 1.0)    #测试用例2
            test3 = trapezoid_area(a=10, b=20, h=30)
            self.assertEqual(test3._value, 450.0)    #测试用例3


    class Parallelogram_AreaTest(unittest.TestCase):    #平行四边形面积类测试
        def test_value(self):    #测试输出
            test1 = parallelogram_area(a=2, h=3)
            self.assertEqual(test1._value, 6)    #测试用例1
            test2 = parallelogram_area(a=3, h=4)
            self.assertEqual(test2._value, 12)    #测试用例2
            test3 = parallelogram_area(a=4, h=5)
            self.assertEqual(test3._value, 20)    #测试用例3


    class Parallelogram_PerimeterTest(unittest.TestCase):    #平行四边形周长类测试
        def test_value(self):    #测试输出
            test1 = parallelogram_perimeter(a=1, h=2)
            self.assertEqual(test1._value, 6)    #测试用例1
            test2 = parallelogram_perimeter(a=2, h=3)
            self.assertEqual(test2._value, 10)    #测试用例2
            test3 = parallelogram_perimeter(a=3, h=4)
            self.assertEqual(test3._value, 14)    #测试用例3


    class Cube_Surface_AreaTest(unittest.TestCase):    #正方体表面积类测试
        def test_value(self):    #测试输出
            test1 = cube_surface_area(a=6)
            self.assertEqual(test1._value, 216)    #测试用例1
            test2 = cube_surface_area(a=4)
            self.assertEqual(test2._value, 96)    #测试用例2
            test3 = cube_surface_area(a=2)
            self.assertEqual(test3._value, 24)    #测试用例3


    class Cube_VolumeTest(unittest.TestCase):    #正方体体积类测试
        def test_value(self):    #测试输出
            test1 = cube_volume(a=6)
            self.assertEqual(test1._value, 216)    #测试用例1
            test2 = cube_volume(a=4)
            self.assertEqual(test2._value, 64)    #测试用例2
            test3 = cube_volume(a=2)
            self.assertEqual(test3._value, 8)    #测试用例3


    class Sum_Of_Cube_EdgesTest(unittest.TestCase):    #正方体棱长总和类测试
        def test_value(self):    #测试输出
            test1 = sum_of_cube_edges(a=6)
            self.assertEqual(test1._value, 72)    #测试用例1
            test2 = sum_of_cube_edges(a=4)
            self.assertEqual(test2._value, 48)    #测试用例2
            test3 = sum_of_cube_edges(a=2)
            self.assertEqual(test3._value, 24)    #测试用例3


    class Cuboid_Surface_AreaTest(unittest.TestCase):    #长方体表面积类测试
        def test_value(self):    #测试输出
            test1 = cuboid_surface_area(a=2, b=3, h=4)
            self.assertEqual(test1._value, 52)    #测试用例1
            test2 = cuboid_surface_area(a=3, b=4, h=5)
            self.assertEqual(test2._value, 94)    #测试用例2
            test3 = cuboid_surface_area(a=10, b=20, h=30)
            self.assertEqual(test3._value, 2200)    #测试用例3


    class Cuboid_VolumeTest(unittest.TestCase):    #长方体体积类测试
        def test_value(self):    #测试输出
            test1 = cuboid_volume(a=1, b=2, h=3)
            self.assertEqual(test1._value, 6)    #测试用例1
            test2 = cuboid_volume(a=2, b=3, h=4)
            self.assertEqual(test2._value, 24)    #测试用例2
            test3 = cuboid_volume(a=10, b=20, h=30)
            self.assertEqual(test3._value, 6000)    #测试用例3


    class Sum_Of_Cuboid_EdgesTest(unittest.TestCase):    #长方体棱长总和类测试
        def test_value(self):    #测试输出
            test1 = sum_of_cuboid_edges(a=2, b=3, h=4)
            self.assertEqual(test1._value, 36)    #测试用例1
            test2 = sum_of_cuboid_edges(a=3, b=4, h=5)
            self.assertEqual(test2._value, 48)    #测试用例2
            test3 = sum_of_cuboid_edges(a=10, b=20, h=30)
            self.assertEqual(test3._value, 240)    #测试用例3


    class Circle_PerimeterTest(unittest.TestCase):    #圆形周长类测试
        def test_value(self):    #测试输出
            de_decimal = lambda decimal_object: float(str(decimal_object))
            test1 = circle_perimeter(r=1)
            self.assertEqual(de_decimal(test1._value), 6.28)    #测试用例1
            test2 = circle_perimeter(r=2)
            self.assertEqual(de_decimal(test2._value), 12.56)    #测试用例2
            test3 = circle_perimeter(r=3)
            self.assertEqual(de_decimal(test3._value), 18.84)    #测试用例3


    class Circle_AreaTest(unittest.TestCase):    #圆形面积类测试
        def test_value(self):    #测试输出
            de_decimal = lambda decimal_object: float(str(decimal_object))
            test1 = circle_area(r=1)
            self.assertEqual(de_decimal(test1._value), 3.14)    #测试用例1
            test2 = circle_area(r=2)
            self.assertEqual(de_decimal(test2._value), 12.56)    #测试用例2
            test3 = circle_area(r=3)
            self.assertEqual(de_decimal(test3._value), 28.26)    #测试用例3


    class MarketingTest(unittest.TestCase):    #营销号生成器类测试
        def test_value(self):    #测试输出
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
        runner = unittest.TextTestRunner(stream=sys.stdout)    #配置启动器
        for test in tests_list:
            itersuite = unittest.TestLoader().loadTestsFromTestCase(test)    #加载测试
            runner.run(itersuite)    #运行测试

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
        iterables = [list(iterable) for iterable in iterables]
        long_list_length = 0
        for iterable in iterables:
            if len(iterable) >= long_list_length:
                long_list_length = len(iterable)
        result = []
        for index in range(long_list_length):
            pack = []
            for iterable in iterables:
                try:
                    value = iterable[index]
                except IndexError:
                    value = ''
                finally:
                    pack.append(value)
            pack = tuple(pack)
            result.append(pack)
        return result


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
#导入cmd模块的Cmd类

class shell(Cmd):
    """命令行交互界面"""
    prompt = "Graphical> "    #提示符

    def do_list(self,arg):
        """打印id"""
        _print_id_key()
    
    def do_compute(self,arg):
        """计算"""
        arg = self.parse(arg)
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
        
    def do_exit(self,arg):
        """退出"""
        return True    #按照和cmd模块的小约定，如果返回True就退出

    def emptyline(self):
        """如果输入空行，调用这个"""
        sys.stdout.write("\n")    #打印一个空行

    def default(self,line):
        """如果无此命令，调用这个"""
        print("'%s' 不是有效的命令"%line)

    def do_help(self,arg):
        """帮助"""
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
    def parse(self,args):
        """解析参数"""
        return args.split(" ")

def _run_shell():
    """启动交互式shell"""
    try:
        a = shell()
        a.cmdloop()
    except KeyboardInterrupt:
        pass

def _command(arg):
    """命令行参数开关"""
    #这里使用python标准库argparse
    parse = argparse.ArgumentParser(description="图形",prog="graphical")    #生成ArgumentParser对象

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
    if parse_args.shell:    #启动shell
        return main.shell()
    elif parse_args.test:
        return main.test()
    elif parse_args.gui:
        return main.gui()
    elif parse_args.json:
        json_str = _builtin_formula_to_json()
        with open("graphical.json",'w',encoding="utf-8") as json_file:
            json_file.write(json_str)
        return json_str
    elif parse_args.old_test:
        return _test(old_test=True)

    if parse_args.list:    #开关list
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
    def __init__(self):
        self.args = sys.argv    #保存变量

    def _parse(self):
        """解析参数列表"""
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
        """命令行参数解析"""
        return _command(cls()._parse())
    
    @staticmethod
    def gui():
        """图形用户界面"""
        try:
            import tkinter    #Tk/Tcl接口
            from tkinter import ttk    #tkinter ttk扩展
        except ImportError:
            import warnings
            warnings.warn("无法导入Tk/Tcl接口，请确保已正确安装tkinter")
        else:    #如果一切正常
            globals()['tkinter'] = tkinter
            globals()['ttk'] = ttk
            return _tkinter_main()
    
    @staticmethod
    def shell():
        """命令行交互提示符"""
        return _run_shell()
    
    @staticmethod
    def test():
        """测试"""
        return _test()

if __name__ == "__main__":

    main()
    main.command()
#os.system(sys.argv[0] + " 17 keyword 李琰 incident 睡觉 another 他困啦")
