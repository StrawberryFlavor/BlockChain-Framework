# -*- coding: utf-8 -*-
import struct
import binascii
import hashlib

'''
读取文件并转为十六进制字符串
参数:
    path: 文件绝对路径; string类型

返回值:    
    十六进制字符串
'''


def FileToHex(path):
    with open(path, "rb") as f:
        value = f.read()

    return binascii.b2a_hex(value).decode('utf-8')


'''
Byte 类型转为十六进制字符串
参数:
    bytes_value: Byte字节串; byte类型

返回值:    
    十六进制字符串
'''


def ByteToHex(bytes_value):
    return binascii.b2a_hex(bytes_value).decode('utf-8')


'''
将输入字符串按两字节倒序, 例如输入'abcd', 输出'cdab' 
参数:
    value: 输入字符串; string类型

返回值:    
    倒序之后的字符串
'''


def ReverseString(value):
    new_value = ""
    if len(new_value) % 2 == 1:
        raise RuntimeError('IllegalArgumentException')
    for i in range(int(len(value) / 2)):
        new_value += value[len(value) - (i + 1) * 2:len(value) - i * 2]

    return new_value


'''
将输入十六进制字符串转为 bytearray
参数:
    hexStr: 输入字符串; string类型

返回值:    
    转换之后的 bytearray
'''


def HexToByte(hexStr):
    if hexStr == None or len(hexStr) == 0:
        return bytearray(0)
    if len(hexStr) % 2 == 1:
        raise RuntimeError('IllegalArgumentException')
    result = bytearray(int(len(hexStr) / 2))
    for i in range(len(result)):
        result[i] = int(hexStr[i * 2: i * 2 + 2], 16)
    return result
