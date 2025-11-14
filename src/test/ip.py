import socket

def get_ip_addr():
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception as e:
        ip = "127.0.0.1"
    finally:
        s.close()
    
    return ip


def is_port_available(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        
        except OSError:
            return False

def get_port_number():
    ip_addr = get_ip_addr()
    
    for port in range(1100 , 9999+1):
        if is_port_available(ip_addr , port):
            return [True , port]
    
    return [False]


# 0-9 & A-Z
chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def encode_ip_port(ip: str, port: int):
    """
        1. split the ip address using dot('.')
        2. convert the string into int using map()
    """
    parts = list(map(int, ip.split('.')))
    
    """
        port 0-15 bits 
        ip1 16-23 bits (8 bits)
        ip2 23-31 bits (8 bits)
        ip3 32-39 bits (8 bits)
        ip4 40-47 bits (8 bits)
        8 bit can store value from 0 to 255
        16 bit can store vale from 0 to 65535
    
        bitwise OR ('|') is used 
    
    """
    num = (parts[0] << 40) | (parts[1] << 32) | (parts[2] << 24) | (parts[3] << 16) | port    
    
    encoded = ""
    
    while num > 0:
        # 26(A-Z) + 10 = 36
        num, r = divmod(num, 36)
        encoded = chars[r] + encoded
    
    return encoded.rjust(9, '0')  # fix length


def decode_ip_port(code: str):
    num = 0
    for c in code:
        num = num * 36 + chars.index(c)

    """
        octal-format (0xFFFF) = 65535(decimal)
        bitwise AND ('&')  
    """    
    port = num & 0xFFFF
    #  removing bits that represent the port
    ip_num = num >> 16
    # 0xFF = 255
    ip = '.'.join(str((ip_num >> shift) & 0xFF) for shift in (24, 16, 8, 0))
    return ip, port , f'{ip}:{port}'


def buildup_url_from_ip_addr(ip_addr_port:str):
    url = "http://"+ip_addr_port
    return url
