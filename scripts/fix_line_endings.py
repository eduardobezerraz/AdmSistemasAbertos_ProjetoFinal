#!/usr/bin/env python3
import os

# Extensões de arquivos que podem precisar de correção
TEXT_EXTENSIONS = {".py", ".yml", ".yaml", ".conf", ".crt", ".csr", ".key", ".html", ".htm", ".php", ".cf", ".txt", ".md", ".sh", ".ini"}

# Diretórios a ignorar (para não perder tempo em arquivos que não importam)
IGNORE_DIRS = {".git", "__pycache__", "node_modules"}

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def is_text_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    return ext in TEXT_EXTENSIONS

def fix_line_endings(file_path):
    try:
        with open(file_path, "rb") as f:
            content = f.read()

        # pula arquivos binários
        if b"\x00" in content:
            return False, "Binário detectado"

        new_content = content.replace(b"\r\n", b"\n")
        if new_content != content:
            with open(file_path, "wb") as f:
                f.write(new_content)
            return True, "Corrigido"
        else:
            return False, "Já está em LF"

    except Exception as e:
        return False, f"Erro: {e}"

def main():
    print(f"Verificando quebra de linha dos arquivos em: {ROOT_DIR}")
    for root, dirs, files in os.walk(ROOT_DIR):
        # pula pastas ignoradas
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for file in files:
            file_path = os.path.join(root, file)
            if is_text_file(file_path):
                changed, status = fix_line_endings(file_path)
                #print(f"[{status}] {os.path.basename(file_path)}")

if __name__ == "__main__":
    main()
