from website import create_app
try:
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip_addre = s.getsockname()[0]
    s.close()
except Exception as e:
    ip_addre = "192.168.31.155"
    print("Hello 2: " + e)
app = create_app()

if __name__ == '__main__':
    # app.run(host= "127.0.1.1", port='5000', debug=True)
    app.run(host= str(ip_addre), port='5000', debug=True)
