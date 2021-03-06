# -*- coding: utf-8 -*-
__author__ = 'Mc.Lee'
import sys, os

path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, path)


import socket
import selectors
import configparser,pickle



class Ftp_Client(object):
    '''
    selector版FTP客户端
    '''
    def __init__(self):
        #创建客户端socket
        self.Client = socket.socket()
        #获取配置文件
        self.Get_Conf()
        #创建连接
        self.Conn()
        #进入命令循环
        self.Command()


    def Conn(self):
        self.Client.connect((self.IP,self.Port))



    def Command(self):
        '''
        按命令执行
        :return:
        '''
        while True:
            cmd = input('请输入命令：').strip()
            cmd_list = cmd.split()
            #print('list:',len(cmd_list))
            if len(cmd_list) == 3:
                if cmd_list[0] == 'put':
                    self.UpLoad(cmd_list)

                elif cmd_list[0] == 'get':
                    self.DownLoad(cmd_list)

                else:
                    print('\033[1;31;1m命令错误！\033[0m')
                    self.Show_Help()
                    continue
            else:
                print('\033[1;31;1m命令错误！\033[0m')
                self.Show_Help()
                continue



            #self.Client.send(cmd.encode())

    def UpLoad(self,cmd_list):
        data = {
            'act':'upload',
            'localfile':cmd_list[1],
            'cloudfile':cmd_list[2]
        }
        self.Client.send(pickle.dumps(data))
        #接收确认信息
        chk = self.Client.recv(1024)#up:1
        if chk.decode() == 'ready':
            print('服务端已准备好，开始发送文件...')
            self.Send_File_Size(data)
        else:
            print('数据传输错误，程序中止')
            exit()


    def Send_File_Size(self,dict):
        '''
        发送文件大小
        :param dict: 命令字典
        :return:
        '''
        data = {'size':0}
        file_path = dict['localfile']
        if os.path.isfile(file_path):
            data['size'] = os.path.getsize(file_path)
            print('获取大小：',data['size'])
            f = open(file_path,'rb')
            self.Client.send(pickle.dumps(data))  # up：2
            self.Send_File_Data(f)#发送文件数据
        else:
            print('文件不存在，无法上传！')
            self.Client.send(pickle.dumps(data)) #up：2

    def Send_File_Data(self,file_obj):
        '''
        发送文件数据
        :param file_obj: 文件句柄
        :return:
        '''
        #接收确认信息
        chk = self.Client.recv(1024)
        if chk.decode() == 'ok':
            print('发送数据')
            for line in file_obj:
                self.Client.send(line)
            file_obj.close()
            print('文件传输完毕！')
            #给服务端发送一个完成信号
            self.Client.send(b'upload completed')
        else:
            print('数据传输错误，程序中止')
            exit()


    def DownLoad(self,cmd_list):
        data = {
            'act': 'download',
            'localfile': cmd_list[2],
            'cloudfile': cmd_list[1]
        }
        self.Client.send(pickle.dumps(data))
        #接收确认信息
        chk = self.Client.recv(1024)#down:1
        if chk.decode() == 'ready':
            self.Client.send(b'ok')#发送一个消息以激活服务端监听回调 down:2
            self.Get_File_Size(data)
        else:
            print('数据传输错误，程序中止')
            exit()

    def Get_File_Size(self,dict):
        '''
        接收服务端文件大小
        :param dict: 命令字典
        :return:
        '''
        filesize = pickle.loads(self.Client.recv(1024))
        if filesize['size'] == 0:
            print('云端文件不存在！')
        else:
            new_filename = self.ReNmae(dict['cloudfile'])
            f = open(new_filename,'wb')
            dict['newfile'] = new_filename
            self.Save_File_Data(f,filesize['size'],dict)


    def Save_File_Data(self,file_obj,file_size,dict):
        '''
        接收服务端发送的文件数据
        :param file_obj: 文件句柄
        :param file_size: 要接收的文件大小
        :param dict: 文件信息字典
        :return:
        '''
        recved_size = 0
        self.Client.send(b'ok')#发送激活信号 down:3
        while file_size - recved_size >0:
            if file_size - recved_size <1024:
                size = file_size - recved_size
            else:
                size = 1024
            file_data = self.Client.recv(1024)
            recved_size += len(file_data)
            file_obj.write(file_data)
        else:
            print('download completed')
            file_obj.close()
            self.ReNmae(dict['newfile'],dict['localfile'])





    def Show_Help(self):
        '''
        打印帮助信息
        :return:
        '''
        print('帮助'.center(50,'-'))
        print('上传文件：put [本地文件名] [云端文件名]')
        print('下载文件：get [云端文件名] [本地文件名]')




    def Get_Conf(self):
        '''
        获取配置信息
        :return:
        '''
        conf = configparser.ConfigParser()
        conf.read('conf.ini')
        self.IP = conf['CLIENT']['ip']
        self.Port = int(conf['CLIENT']['port'])


    def ReNmae(self,filename,type='tmp'):
        '''
        重命名文件
        :param filename:要重命名的文件
        :param type: tmp参数时，在文件最后扩展名加上.tmp;normal参数时，将tmp后缀去掉；其他参数时，type接收一个文件名，重命名为此文件名
        :return:新的文件名
        '''
        file_exp = filename.split('.')
        if type == 'tmp':
            file_exp.append('tmp')
            new_filename = '.'.join(file_exp)
        elif type == 'normal':
            file_exp.pop()
            new_filename = '.'.join(file_exp)
        else:
            #print('重命名参数错误！')
            os.rename(filename,type)
            new_filename = type

        return new_filename




client = Ftp_Client()