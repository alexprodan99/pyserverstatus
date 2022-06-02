import argparse
import socket
import ssl

def is_running(server_address, port):
    try:
        socket_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if port == 443:
            socket_conn = ssl.wrap_socket(socket_conn)
        
        socket_conn.connect((server_address, port))
        return True
    except:
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("server_address", help="[required] server address for status checking", type=str)
    parser.add_argument("--port", help="[optional] port number for server. [default] one is 80", default=80)
    args = parser.parse_args()
    
    if is_running(args.server_address, args.port):
        print(f"{args.server_address} is running")
    else:
        print(f"{args.server_address} is not running")

