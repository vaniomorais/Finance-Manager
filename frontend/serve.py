#!/usr/bin/env python3
"""Servidor HTTP simples para servir os arquivos do frontend."""

import http.server
import socketserver
import os

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Adicionar headers de CORS para permitir requisições ao backend
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

# Mudar para o diretório do frontend
os.chdir(os.path.dirname(os.path.abspath(__file__)))

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print(f"🚀 Servidor Frontend rodando em http://127.0.0.1:{PORT}")
    print("Pressione CTRL+C para parar")
    httpd.serve_forever()
