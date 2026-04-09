# 📋 Instruções para Carga de Dados (Amanhã na Empresa)

Este guia explica como sincronizar os **526 tomadores** com o Supabase oficial.

## 🚀 Passo a Passo

### 1. Sincronize o código
Ao chegar na máquina da empresa, abra o terminal na pasta do projeto e rode:
```bash
git pull origin main
```
Isso trará as correções de conexão e o script atualizado que acabamos de fazer.

### 2. Prepare a Planilha
Coloque o arquivo `TEMPLATE MODELO ENVIO DE RPS EM LOTE - PREF. CAIEIRAS.xlsm` **dentro da pasta raiz do projeto** (onde fica o arquivo `.gitignore`).

### 3. Execute a Importação
Ainda no terminal, rode o comando:
```bash
python backend/scripts/importar_tomadores.py
```

### 4. Verifique o Resultado
*   O terminal deve exibir: `Importacao finalizada com sucesso! - Novos clientes: 441` (aproximadamente).
*   Abra o site no Hugging Face: os 526 registros aparecerão lá instantaneamente.

---

## 🔒 Segurança de Banco (Lembrete)
O site agora usa a `DATABASE_URL` secreta que configuramos. Se por algum motivo o banco da empresa ainda estiver apontando para um arquivo local (`.db`), o script que você rodará acima vai garantir que tudo seja enviado para o **PostgreSQL (Supabase)** correto.

**Boa noite e bom descanso! Até amanhã.**
