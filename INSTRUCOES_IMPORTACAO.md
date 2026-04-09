# 📋 Instruções para Carga de Dados (Amanhã na Empresa)

Este guia explica como sincronizar os **526 tomadores** com o Supabase oficial e como eliminar de vez a dependência de planilhas.

## 🛡️ Segurança Total (Não quebra o deploy!)
Fique tranquilo: o arquivo `.gitignore` do projeto já está configurado para **bloquear** planilhas (`*.xlsm`, `*.xlsx`). 
*   Isso significa que, mesmo que você coloque a planilha na pasta do projeto, ela **NUNCA** será enviada para o GitHub ou Hugging Face.
*   O deploy continuará funcionando perfeitamente e o Space ficará "limpinho".

## 🚀 Passo a Passo para Independência Total

### 1. Sincronize o código
Ao chegar na máquina da empresa, rode no terminal:
```bash
git pull origin main
```

### 2. Carga Única no Banco
Coloque a planilha na raiz do projeto e rode:
```bash
python backend/scripts/importar_tomadores.py
```
Esse comando vai ler a planilha e "empurrar" todos os 526 tomadores para dentro do Supabase na nuvem.

### 3. Fim da Dependência
Assim que o script terminar:
1.  **Delete a planilha** da pasta do projeto.
2.  Pronto! Agora o Supabase é o dono de tudo. O site em casa, no celular ou no Hugging Face mostrará os 526 registros sem precisar da planilha nunca mais.

---
**Boa noite e bom descanso!**
