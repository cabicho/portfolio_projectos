import os
import shutil

def build_assets():
    """Copia assets para o diretório correto no build do Render"""
    if not os.path.exists('assets'):
        os.makedirs('assets')
    
    if os.path.exists('assets/styles.css'):
        print("✅ Assets CSS encontrados")
    else:
        with open('assets/styles.css', 'w') as f:
            f.write("/* CSS do Dashboard Rossmann */\n")
        print("📁 CSS básico criado")
    
    print("✅ Build de assets concluído")

if __name__ == '__main__':
    build_assets()
