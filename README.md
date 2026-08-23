# Finance Manager

Sistema web para controle de finanças pessoais, desenvolvido com Python e Flask, que permite registrar e organizar entradas e saídas financeiras, associar transações a categorias, criar novas categorias, excluir informações e visualizar um dashboard com o resumo financeiro, facilitando o acompanhamento das movimentações.

<p align="center">
  <img src="static/images/finance1.png" width="500px" alt="Print do projeto">
</p>

## Tecnologias

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)


## Como executar

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/financemanager.git
cd expense-control
```

### 2. Crie e ative o ambiente virtual

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados

Crie o banco MySQL utilizando o arquivo `schema.sql`:

```bash
mysql -u root -p < schema.sql
```

### 5. Configure as variáveis de ambiente

Copie `.env.example` para `.env` e configure as credenciais do seu banco MySQL.

### 6. Execute a aplicação

```bash
python app.py
```
