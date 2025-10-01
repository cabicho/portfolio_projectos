import time
import os

def main():
    print("🚀 Worker Rossmann iniciado")
    while True:
        print("🤖 Worker rodando...", time.ctime())
        time.sleep(60)

if __name__ == '__main__':
    main()
