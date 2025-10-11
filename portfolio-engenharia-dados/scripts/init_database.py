import asyncpg
import os
import asyncio
import json
from datetime import datetime, timedelta

async def create_regulatory_data_warehouse():
    """Criar Data Warehouse para Relatórios Regulamentares"""
    database_url = os.getenv("DATABASE_URL")
    conn = await asyncpg.connect(database_url)
    
    # ========== DIMENSÕES ==========
    
    # Dimensão Clientes
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS dim_clientes (
            cliente_id SERIAL PRIMARY KEY,
            nome VARCHAR(200) NOT NULL,
            tipo_cliente VARCHAR(50),
            segmento VARCHAR(100),
            regiao VARCHAR(50),
            data_cadastro DATE,
            status VARCHAR(20)
        )
    ''')
    
    # Dimensão Produtos
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS dim_produtos (
            produto_id SERIAL PRIMARY KEY,
            nome_produto VARCHAR(200) NOT NULL,
            categoria VARCHAR(100),
            subcategoria VARCHAR(100),
            preco_base DECIMAL(10,2),
            data_inclusao DATE
        )
    ''')
    
    # Dimensão Tempo
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS dim_tempo (
            data_id SERIAL PRIMARY KEY,
            data_completa DATE,
            ano INTEGER,
            semestre INTEGER,
            trimestre INTEGER,
            mes INTEGER,
            dia INTEGER,
            dia_semana INTEGER,
            feriado BOOLEAN
        )
    ''')
    
    # ========== FATOS ==========
    
    # Fato Vendas
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS fato_vendas (
            venda_id SERIAL PRIMARY KEY,
            cliente_id INTEGER REFERENCES dim_clientes(cliente_id),
            produto_id INTEGER REFERENCES dim_produtos(produto_id),
            data_id INTEGER REFERENCES dim_tempo(data_id),
            quantidade INTEGER,
            valor_total DECIMAL(10,2),
            regiao VARCHAR(50),
            canal_venda VARCHAR(50),
            status_venda VARCHAR(20)
        )
    ''')
    
    # ========== TABELAS OPERACIONAIS ==========
    
    # Requisitos de Negócio
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS requisitos_negocio (
            id SERIAL PRIMARY KEY,
            unidade_negocio VARCHAR(100),
            descricao TEXT,
            prioridade VARCHAR(20),
            contato VARCHAR(100),
            status VARCHAR(20),
            data_solicitacao TIMESTAMP DEFAULT NOW()
        )
    ''')
    
    # Solicitações de Suporte
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS solicitacoes_suporte (
            id SERIAL PRIMARY KEY,
            titulo VARCHAR(200),
            descricao TEXT,
            urgencia VARCHAR(20),
            solicitante VARCHAR(100),
            status VARCHAR(20),
            data_abertura TIMESTAMP DEFAULT NOW(),
            data_resolucao TIMESTAMP
        )
    ''')
    
    # Pipelines ETL
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS pipelines_etl (
            id SERIAL PRIMARY KEY,
            nome_pipeline VARCHAR(100),
            status VARCHAR(50),
            registros_processados INTEGER,
            ultima_execucao TIMESTAMP DEFAULT NOW(),
            detalhes_execucao TEXT
        )
    ''')
    
    # Fontes de Dados
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS fontes_dados (
            id SERIAL PRIMARY KEY,
            nome_fonte VARCHAR(100),
            tipo_fonte VARCHAR(50),
            conexao_ativa BOOLEAN,
            ultima_atualizacao TIMESTAMP
        )
    ''')
    
    # Relatórios Regulatórios
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS relatorios_regulatorios (
            id SERIAL PRIMARY KEY,
            tipo_relatorio VARCHAR(100),
            periodo VARCHAR(50),
            status VARCHAR(50),
            data_geracao TIMESTAMP DEFAULT NOW(),
            arquivo_gerado VARCHAR(200)
        )
    ''')
    
    # Tabela simplificada para demonstração
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id SERIAL PRIMARY KEY,
            produto VARCHAR(100),
            quantidade INTEGER,
            valor_total DECIMAL(10,2),
            data_venda DATE,
            regiao VARCHAR(50),
            cliente VARCHAR(100)
        )
    ''')
    
    # ========== INSERIR DADOS DE EXEMPLO ==========
    
    # Clientes
    await conn.execute('''
        INSERT INTO dim_clientes (nome, tipo_cliente, segmento, regiao, data_cadastro, status)
        VALUES 
        ('Empresa A Ltda', 'Corporativo', 'Tecnologia', 'Sul', '2023-01-15', 'Ativo'),
        ('Comércio B ME', 'Pequena Empresa', 'Varejo', 'Norte', '2023-02-20', 'Ativo'),
        ('Serviços C SA', 'Corporativo', 'Consultoria', 'Sudeste', '2023-03-10', 'Inativo'),
        ('Indústria D EPP', 'Média Empresa', 'Manufatura', 'Nordeste', '2023-04-05', 'Ativo')
        ON CONFLICT DO NOTHING
    ''')
    
    # Produtos
    await conn.execute('''
        INSERT INTO dim_produtos (nome_produto, categoria, subcategoria, preco_base, data_inclusao)
        VALUES 
        ('Software Gestão', 'Software', 'ERP', 1500.00, '2023-01-01'),
        ('Consultoria TI', 'Serviços', 'Consultoria', 5000.00, '2023-01-01'),
        ('Suporte Premium', 'Serviços', 'Suporte', 800.00, '2023-01-01'),
        ('Treinamento', 'Serviços', 'Educação', 1200.00, '2023-01-01')
        ON CONFLICT DO NOTHING
    ''')
    
    # Inserir vendas de exemplo
    for i in range(50):
        await conn.execute('''
            INSERT INTO vendas (produto, quantidade, valor_total, data_venda, regiao, cliente)
            VALUES ($1, $2, $3, $4, $5, $6)
        ''', 
        f'Produto {i % 4 + 1}', 
        (i % 10) + 1,
        ((i % 10) + 1) * 100.0,
        datetime.now() - timedelta(days=i % 30),
        ['Norte', 'Nordeste', 'Sudeste', 'Sul', 'Centro-Oeste'][i % 5],
        f'Cliente {i % 4 + 1}'
        )
    
    # Inserir dados de exemplo nas outras tabelas
    await conn.execute('''
        INSERT INTO requisitos_negocio (unidade_negocio, descricao, prioridade, contato, status)
        VALUES 
        ('Vendas', 'Relatório de performance mensal por região', 'Alta', 'joao.silva@empresa.com', 'Em Desenvolvimento'),
        ('Marketing', 'Dashboard de campanhas e conversões', 'Média', 'maria.santos@empresa.com', 'Pendente'),
        ('Financeiro', 'Relatório de compliance regulamentar trimestral', 'Alta', 'carlos.oliveira@empresa.com', 'Concluído')
        ON CONFLICT DO NOTHING
    ''')
    
    await conn.execute('''
        INSERT INTO pipelines_etl (nome_pipeline, status, registros_processados)
        VALUES 
        ('Pipeline Vendas', 'Ativo', 1500),
        ('Pipeline Clientes', 'Ativo', 500),
        ('Pipeline Produtos', 'Em Manutenção', 200)
        ON CONFLICT DO NOTHING
    ''')
    
    print("✅ Data Warehouse criado com sucesso!")
    await conn.close()

if __name__ == "__main__":
    asyncio.run(create_regulatory_data_warehouse())
