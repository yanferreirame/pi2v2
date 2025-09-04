import sqlite3
import random
from datetime import datetime, timedelta

# Conectar ao banco de dados
conn = sqlite3.connect('pi2.db')
cursor = conn.cursor()

# Dados dos clientes
clientes = [
    ('Construtora Alpha Ltda', 'São Paulo', '01234-567', 'Av. Paulista, 1000', '(11) 9999-8888'),
    ('Engenharia Beta S.A.', 'Rio de Janeiro', '22000-000', 'Rua do Ouvidor, 50', '(21) 8888-7777'),
    ('José da Silva Construtora', 'Belo Horizonte', '30123-456', 'Av. Afonso Pena, 2000', '(31) 7777-6666'),
    ('Maria Oliveira Reformas', 'Salvador', '40000-000', 'Rua Chile, 30', '(71) 6666-5555'),
    ('Pedro Santos Materiais', 'Brasília', '70000-000', 'SQS 105 Bloco C', '(61) 5555-4444'),
    ('Construdo Soluções', 'Curitiba', '80000-000', 'Rua XV de Novembro, 500', '(41) 4444-3333'),
    ('Mega Construções', 'Porto Alegre', '90000-000', 'Av. Borges de Medeiros, 300', '(51) 3333-2222'),
    ('Casa Forte Construção', 'Fortaleza', '60000-000', 'Av. Beira Mar, 800', '(85) 2222-1111'),
    ('Luiz Mendes & Filhos', 'Recife', '50000-000', 'Rua do Bom Jesus, 40', '(81) 1111-0000'),
    ('Andrade Incorporações', 'Manaus', '69000-000', 'Av. Eduardo Ribeiro, 600', '(92) 9999-8888'),
    ('Lar Doce Lar Construtora', 'Goiânia', '74000-000', 'Av. Goiás, 1000', '(62) 8888-7777'),
    ('Viveiro Materiais', 'Florianópolis', '88000-000', 'Rua Felipe Schmidt, 200', '(48) 7777-6666'),
    ('Tijolo Baiano Ltda', 'Vitória', '29000-000', 'Av. Vitória, 700', '(27) 6666-5555'),
    ('Cimento Nacional', 'Campinas', '13000-000', 'Av. John Boyd Dunlop, 500', '(19) 5555-4444'),
    ('Ferro & Aço Construção', 'São Luís', '65000-000', 'Av. Daniel de La Touche, 100', '(98) 4444-3333'),
    ('Telhas Nordeste', 'Maceió', '57000-000', 'Av. Durval de Góes Monteiro, 300', '(82) 3333-2222'),
    ('Vidraçaria Central', 'Natal', '59000-000', 'Av. Hermes da Fonseca, 400', '(84) 2222-1111'),
    ('Hidráulica Fácil', 'João Pessoa', '58000-000', 'Av. Epitácio Pessoa, 200', '(83) 1111-0000'),
    ('Elétrica Moderna', 'Teresina', '64000-000', 'Av. Frei Serafim, 800', '(86) 9999-8888'),
    ('Decorações em Obra', 'Cuiabá', '78000-000', 'Av. Isaac Póvoas, 600', '(65) 8888-7777')
]

# Dados dos fornecedores
fornecedores = [
    ('Cimento Nacional Indústria', 'Cimento Nacional', '12.345.678/0001-01', 'Rod. BR-101, km 100', '12345-678', '(11) 3333-4444'),
    ('Tigre S.A. Materiais', 'Tigre', '23.456.789/0001-02', 'Av. Industrial, 500', '23456-789', '(47) 3333-5555'),
    ('Votorantim Cimentos', 'Votorantim', '34.567.890/0001-03', 'Rua das Flores, 300', '34567-890', '(11) 3333-6666'),
    ('Cerâmica Portobello', 'Portobello', '45.678.901/0001-04', 'Estrada da Cerâmica, 1000', '45678-901', '(47) 3333-7777'),
    ('Deca S.A. Sanitários', 'Deca', '56.789.012/0001-05', 'Av. dos Sanitários, 200', '56789-012', '(11) 3333-8888'),
    ('Lorenzetti Eletricidade', 'Lorenzetti', '67.890.123/0001-06', 'Rua da Eletricidade, 150', '67890-123', '(11) 3333-9999'),
    ('Tramontina Ferramentas', 'Tramontina', '78.901.234/0001-07', 'Av. das Ferramentas, 700', '78901-234', '(54) 3333-0000'),
    ('Makita do Brasil', 'Makita', '89.012.345/0001-08', 'Rod. dos Equipamentos, 250', '89012-345', '(11) 4444-1111'),
    ('3M do Brasil', '3M', '90.123.456/0001-09', 'Av. da Inovação, 350', '90123-456', '(11) 4444-2222'),
    ('Saint-Gobain Brasil', 'Saint-Gobain', '01.234.567/0001-10', 'Rua dos Vidros, 450', '01234-567', '(11) 4444-3333'),
    ('Knauf do Brasil', 'Knauf', '12.345.679/0001-11', 'Estrada do Gesso, 550', '12345-679', '(11) 4444-4444'),
    ('Suvinil Tintas', 'Suvinil', '23.456.780/0001-12', 'Av. das Cores, 650', '23456-780', '(11) 4444-5555'),
    ('Coral Tintas', 'Coral', '34.567.891/0001-13', 'Rua dos Pigmentos, 750', '34567-891', '(11) 4444-6666'),
    ('Amanco Wavin', 'Amanco', '45.678.902/0001-14', 'Av. dos Tubos, 850', '45678-902', '(11) 4444-7777'),
    ('Lena Lighting', 'Lena', '56.789.013/0001-15', 'Rua da Iluminação, 950', '56789-013', '(11) 4444-8888'),
    ('Docol Metais', 'Docol', '67.890.124/0001-16', 'Av. dos Metais, 1050', '67890-124', '(11) 4444-9999'),
    ('Eucatex Painéis', 'Eucatex', '78.901.235/0001-17', 'Estrada dos Painéis, 1150', '78901-235', '(11) 5555-1111'),
    ('Duratex Madeiras', 'Duratex', '89.012.346/0001-18', 'Av. das Madeiras, 1250', '89012-346', '(11) 5555-2222'),
    ('Vedacit Impermeabilizantes', 'Vedacit', '90.123.457/0001-19', 'Rua da Impermeabilização, 1350', '90123-457', '(11) 5555-3333'),
    ('Lepri Materiais Elétricos', 'Lepri', '01.234.568/0001-20', 'Av. da Energia, 1450', '01234-568', '(11) 5555-4444')
]

# Dados dos produtos (nome e preço)
produtos = [
    ('Cimento CP II 50kg', 28.90),
    ('Cimento CP III 50kg', 32.50),
    ('Saco de Areia Média 20kg', 5.90),
    ('Saco de Brita 1 20kg', 6.80),
    ('Tijolo Baiano 1000un', 450.00),
    ('Tijolo Cerâmico 8 furos', 0.85),
    ('Tijolo Cerâmico 6 furos', 0.95),
    ('Bloco de Concreto 14x19x39cm', 2.20),
    ('Bloco de Concreto 9x19x39cm', 1.80),
    ('Telha Cerâmica 44x24cm', 1.50),
    ('Telha Cerâmica 40x22cm', 1.30),
    ('Telha de Fibrocimento 2,44x1,10m', 48.00),
    ('Telha Galvanizada 2,44x1,10m', 52.00),
    ('Viga de Madeira 6x12cmx3m', 35.00),
    ('Viga de Madeira 8x16cmx3m', 65.00),
    ('Caibro de Madeira 5x5cmx3m', 12.00),
    ('Ripas de Madeira 2,5x5cmx3m', 5.50),
    ('Tábua de Pinus 30x2,5cmx3m', 28.00),
    ('Porta de Madeira Maciça 0,80x2,10m', 320.00),
    ('Janela de Alumínio 1,00x1,20m', 180.00),
    ('Janela de PVC 1,00x1,20m', 220.00),
    ('Tubo PVC 100mm 3m', 42.00),
    ('Tubo PVC 75mm 3m', 28.00),
    ('Tubo PVC 50mm 3m', 15.00),
    ('Luvas PVC 100mm', 8.50),
    ('Luvas PVC 75mm', 5.80),
    ('Joelhos PVC 90° 100mm', 10.50),
    ('Joelhos PVC 90° 75mm', 7.20),
    ('Registro de Pressão 1/2"', 18.90),
    ('Registro de Pressão 3/4"', 22.50),
    ('Registro de Pressão 1"', 28.00),
    ('Torneira para Pia 1/2"', 45.00),
    ('Torneira para Tanque 1/2"', 55.00),
    ('Chuveiro Elétrico 220V', 85.00),
    ('Chuveiro Elétrico 110V', 80.00),
    ('Caixa d\'Água 500L', 280.00),
    ('Caixa d\'Água 1000L', 450.00),
    ('Fio Elétrico 2,5mm 100m', 125.00),
    ('Fio Elétrico 1,5mm 100m', 85.00),
    ('Fio Elétrico 4,0mm 100m', 180.00),
    ('Disjuntor Bipolar 25A', 35.00),
    ('Disjuntor Bipolar 40A', 45.00),
    ('Interruptor Simples', 8.50),
    ('Tomada 2P+T 10A', 9.90),
    ('Tomada 2P+T 20A', 12.50),
    ('Tinta Acrílica Branca 18L', 145.00),
    ('Tinta Acrílica Branca 3,6L', 38.00),
    ('Tinta Esmalte Sintético 3,6L', 65.00),
    ('Massa Corrida 20kg', 85.00),
    ('Massa Acrílica 20kg', 78.00),
    ('Argamassa AC-III 20kg', 15.90),
    ('Rejunte Cerâmico 1kg', 8.50),
    ('Impermeabilizante 18L', 120.00),
    ('Verniz Marítimo 3,6L', 75.00),
    ('Pincel 4"', 12.00),
    ('Rolo de Lã 25cm', 18.50),
    ('Lixa para Madeira Nº 80', 1.20),
    ('Lixa para Parede Nº 120', 0.90),
    ('Parafuso Madeira 3,5x60mm 100un', 25.00),
    ('Parafuso Drywall 3,5x25mm 100un', 18.00),
    ('Bucha Nylon 8mm 100un', 15.00),
    ('Prego 18x28 1kg', 12.50)
]

# Inserir clientes
cursor.executemany('''
INSERT INTO clientes (nome, cidade, cep, endereco, telefone)
VALUES (?, ?, ?, ?, ?)
''', clientes)

# Inserir fornecedores
cursor.executemany('''
INSERT INTO fornecedores (razao_social, apelido, cnpj, endereco, cep, telefone)
VALUES (?, ?, ?, ?, ?, ?)
''', fornecedores)

# Inserir produtos
cursor.executemany('''
INSERT INTO produtos (item, valor_unitario)
VALUES (?, ?)
''', produtos)

# Gerar alguns pedidos de exemplo
for i in range(30):
    cliente_id = random.randint(1, 20)
    produto_id = random.randint(1, 50)
    quantidade = random.randint(1, 20)
    metodo_pagamento = random.choice(['Dinheiro', 'PIX', 'Cartão de Crédito', 'Cartão de Débito', 'Transferência'])
    desconto = random.choice([0, 5, 10, 15]) if metodo_pagamento in ['Dinheiro', 'PIX'] else 0
    
    # Buscar preço do produto
    cursor.execute('SELECT valor_unitario FROM produtos WHERE id = ?', (produto_id,))
    resultado = cursor.fetchone()
    if resultado:
        valor_unitario = resultado[0]
        valor_total = valor_unitario * quantidade * (1 - desconto/100)
        
        # Data aleatória nos últimos 60 dias
        data_pedido = datetime.now() - timedelta(days=random.randint(1, 60))
        
        cursor.execute('''
        INSERT INTO pedidos (cliente_id, produto_id, quantidade, metodo_pagamento, desconto, valor_total, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (cliente_id, produto_id, quantidade, metodo_pagamento, desconto, valor_total, data_pedido))

# Commit e fechar conexão
conn.commit()
conn.close()

print("Dados inseridos com sucesso!")