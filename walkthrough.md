# Walkthrough - Sincronização de Repositório

Neste guia, detalhamos o processo realizado para sincronizar o ambiente local com o repositório remoto.

## Visão Geral
O objetivo foi baixar todo o código-fonte do projeto "Gerador de XML - Prefeitura de Caieiras" para o diretório local.

## Passo a Passo

### 1. Verificação Inicial
- Verificamos se o Git estava disponível no sistema (`git version`).
- Confirmamos que o diretório estava inicialmente vazio.

### 2. Preparação do Diretório
- Como o diretório continha arquivos de documentação criados no início (`implementation_plan.md` e `task.md`), optamos por inicializar o repositório manualmente em vez de um clone simples.

### 3. Sincronização
- Comandos executados:
  ```powershell
  git init
  git remote add origin https://github.com/jacksonsantosjr/gerador-de-XML-Prefeitura-Caieiras
  git fetch origin
  git pull origin main
  ```

### 4. Resultado
- O repositório foi baixado com sucesso.
- O branch local está sincronizado com `origin/main`.
- As estruturas `backend` e `frontend` estão prontas no diretório.

## Próximos Passos
- Explorar a estrutura do projeto.
- Instalar dependências se necessário (verificar README.md).
