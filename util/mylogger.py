#encoding=utf-8
import logging
import os

# Define a Handler and set a format which output to file

def log_file(log_path,log_name):  
    """
    这个方法只会输出到文件 不会显示在控制台
    """
    file_log=logging.FileHandler(log_path,"w")
    file_log.setLevel(logging.DEBUG)
    file_logger=logging.getLogger(log_name)
    file_logger.addHandler(file_log)
    file_logger.setLevel(logging.DEBUG)
    return file_logger

def log_console(): 
    """
    这个方法在使用的时候会返回一个logger实例
    """
    #console和logger的级别都应该设置 the setLevel of console and logger all should be reset
    console = logging.StreamHandler()                  # 定义console handler
    console.setLevel(logging.DEBUG)                     # 定义该handler级别
    formatter = logging.Formatter('%(asctime)s  %(filename)s : %(levelname)s  %(message)s')  #定义该handler格式
    console.setFormatter(formatter)
    
    logger = logging.getLogger("mylogger")
    logger.setLevel(logging.WARNING)
    logger.addHandler(console)
    return logger

def log_console_and_file(log_path,log_name):
    ''' Output log to file and console '''
    # Define a Handler and set a format which output to file
    # 创建一个logger  
    #不同的log_name可以创建不同的log,如果只改变log_path，只会把同一个log_name 写到多个路径下
    logger = logging.getLogger(log_name)  
    logger.setLevel(logging.DEBUG)  
      
    # 创建一个handler，用于写入日志文件  
    fh = logging.FileHandler(log_path)  
    fh.setLevel(logging.INFO)  
      
    # 再创建一个handler，用于输出到控制台  
    ch = logging.StreamHandler()  
    ch.setLevel(logging.WARNING)  
      
    # 定义handler的输出格式  
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
#     fh.setFormatter(formatter)  
#     ch.setFormatter(formatter)  
      
    # 给logger添加handler  
    logger.addHandler(fh)  
    logger.addHandler(ch) 
    return logger

def main():
    path_project = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir))
    log_path ='log.log'
    log_path1 ='log1.log'
    log_path2 ='log2.log'
    logger=log_console_and_file(log_path,'log')
#     logger.debug('logger debug message')     
    logger.info('logger info message')
#     logger.warning('logger warning message')
#     logger.error('logger error message')
#     logger.critical('logger critical message')
    logger1=log_console_and_file(log_path1,'log1')
    logger1.info('logger info message1')
    
    logger2=log_console_and_file(log_path2,'log2')
    logger2.info('logger info message2')
    
if __name__=="__main__":
    main()

    

