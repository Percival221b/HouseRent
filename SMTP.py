from socket import *
import ssl
import base64

# QQ邮箱SMTP服务器
mailServer = "smtp.qq.com"
mailPort = 465

# 发件人邮箱
fromAddress = "3693352353@qq.com"

# 收件人邮箱
toAddress = "percival.221b@gmail.com"

# QQ邮箱授权码（不是QQ密码）
password = "xeqgaammvddycjec"

# 创建TCP socket
clientSocket = socket(AF_INET, SOCK_STREAM)

# SSL加密
context = ssl.create_default_context()

clientSocket = context.wrap_socket(
    clientSocket,
    server_hostname=mailServer
)

# 连接邮件服务器
clientSocket.connect((mailServer, mailPort))

# 接收服务器欢迎信息
recv = clientSocket.recv(1024).decode()
print(recv)

if recv[:3] != '220':
    print("220 reply not received from server.")

# 发送HELO命令
heloCommand = 'HELO Alice\r\n'
clientSocket.send(heloCommand.encode())

recv1 = clientSocket.recv(1024).decode()
print(recv1)

if recv1[:3] != '250':
    print('250 reply not received from server.')

# 登录认证 AUTH LOGIN
authCommand = 'AUTH LOGIN\r\n'
clientSocket.send(authCommand.encode())

recv2 = clientSocket.recv(1024).decode()
print(recv2)

# 发送用户名（Base64编码）
username = base64.b64encode(fromAddress.encode()).decode() + '\r\n'
clientSocket.send(username.encode())

recv3 = clientSocket.recv(1024).decode()
print(recv3)

# 发送授权码（Base64编码）
password64 = base64.b64encode(password.encode()).decode() + '\r\n'
clientSocket.send(password64.encode())

recv4 = clientSocket.recv(1024).decode()
print(recv4)

# MAIL FROM
mailFromCommand = f'MAIL FROM:<{fromAddress}>\r\n'
clientSocket.send(mailFromCommand.encode())

recv5 = clientSocket.recv(1024).decode()
print(recv5)

# RCPT TO
rcptToCommand = f'RCPT TO:<{toAddress}>\r\n'
clientSocket.send(rcptToCommand.encode())

recv6 = clientSocket.recv(1024).decode()
print(recv6)

# DATA
dataCommand = 'DATA\r\n'
clientSocket.send(dataCommand.encode())

recv7 = clientSocket.recv(1024).decode()
print(recv7)

# 邮件内容
msg = f"""From: <{fromAddress}>
To: <{toAddress}>
Subject: SMTP Test

I Love Computer Networks!
"""

# 发送邮件正文
clientSocket.send(msg.encode())

# VERY IMPORTANT:
# SMTP结束符
clientSocket.send("\r\n.\r\n".encode())

# 接收服务器响应
recv8 = clientSocket.recv(1024).decode()
print(recv8)

# QUIT
quitCommand = 'QUIT\r\n'
clientSocket.send(quitCommand.encode())

recv9 = clientSocket.recv(1024).decode()
print(recv9)

# 关闭连接
clientSocket.close()

print("邮件发送成功！")