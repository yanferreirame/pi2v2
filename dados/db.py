import sqlite3
import streamlit as st
import os
from datetime import datetime

DB_PATH = "pi2.db"

def get_db_connection():
    """Cria conexão com SQLite"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        create_tables(conn)
        return conn
    except Exception as e:
        st.error(f"Erro SQLite: {e}")
        return None

def create_tables(conn):
    """Cria as tabelas se não existirem"""
    try:
        cursor = conn.cursor()
        
        # Tabela de clientes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cidade TEXT,
                cep TEXT,
                endereco TEXT,
                telefone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de produtos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT NOT NULL,
                valor_unitario REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de fornecedores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fornecedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                razao_social TEXT NOT NULL,
                apelido TEXT,
                cnpj TEXT UNIQUE,
                endereco TEXT,
                cep TEXT,
                telefone TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de pedidos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER,
                produto_id INTEGER,
                quantidade INTEGER NOT NULL,
                metodo_pagamento TEXT,
                desconto REAL DEFAULT 0,
                valor_total REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES clientes (id),
                FOREIGN KEY (produto_id) REFERENCES produtos (id)
            )
        """)
        
        conn.commit()
        
    except Exception as e:
        st.error(f"Erro ao criar tabelas: {e}")

def execute_query(query, params=None):
    """Executa query de inserção/atualização"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Adaptar query para SQLite (usar ? em vez de %s)
        query = query.replace("%s", "?")
        query = query.replace("AUTO_INCREMENT", "AUTOINCREMENT")
        query = query.replace("NOW()", "datetime('now')")
        query = query.replace("CURRENT_TIMESTAMP", "datetime('now')")
        
        cursor.execute(query, params or ())
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"❌ Erro ao executar query: {e}")
        return False

def fetch_all(query, params=None):
    """Busca todos os registros"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Adaptar query para SQLite
        query = query.replace("NOW()", "datetime('now')")
        query = query.replace("CURRENT_TIMESTAMP", "datetime('now')")
        
        cursor.execute(query, params or ())
        results = cursor.fetchall()
        conn.close()
        return [dict(row) for row in results]
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")
        return []

def fetch_one(query, params=None):
    """Busca um único registro"""
    results = fetch_all(query, params)
    return results[0] if results else None

# Criar banco e tabelas ao importar
if not os.path.exists(DB_PATH):
    conn = get_db_connection()
    conn.close()
    st.success("✅ Banco SQLite criado com sucesso!")