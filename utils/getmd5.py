# -*- coding: utf-8 -*- 
import hashlib
import os


class GetMd5(object):
    '''
    计算文件的md5
    参数:
        _file: 文件绝对路径; string类型
    返回值:
        文件md5值
    '''

    def calc_md5_for_file(self, file):
        md5 = hashlib.md5()
        with open(file, "rb") as f:
            md5.update(f.read())
        return md5.hexdigest()

    '''
    分别计算文件夹中文件的md5
    参数:
        _folder: 文件夹绝对路径; string类型
    返回值:    
        各文件md5值的列表
    '''

    def calc_md5_for_files(self, folder):
        md5 = []
        files = os.listdir(folder)
        files.sort()
        for _file in files:
            md5.append(str(self.calc_md5_for_file(os.path.join(folder, _file))))
        return md5

    '''
    计算文件夹的md5
    参数:
        _file: 文件夹绝对路径; string类型

    返回值:    
        文件夹md5值
    '''

    def calc_md5_for_folder(self, folder):
        md5 = hashlib.md5()
        files = os.listdir(folder)
        files.sort()
        for _file in files:
            md5.update(str(self.calc_md5_for_file(os.path.join(folder, _file))).encode())
        return md5.hexdigest()


if __name__ == "__main__":
    md5 = GetMd5()
    print(md5.calc_md5_for_file("D:/Temp/hashgard"))
