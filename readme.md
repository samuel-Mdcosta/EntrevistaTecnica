# Entrevista

Projeto com backend em FastAPI e frontend em HTML/JS para upload de PDFs.

## Como iniciar

### Backend

1. Acesse a pasta do backend:

   ```bash
   cd backend
   ```

2. Instale as dependências:

   ```bash
   pip install fastapi uvicorn python-multipart networkx
   ```

3. Inicie o servidor:

   ```bash
   uvicorn main:app --reload
   ```

   O backend ficará disponível em `http://localhost:8000`.

### Frontend

Abra o arquivo [frontend/index.html](frontend/index.html) diretamente no navegador, ou utilize uma extensão como **Live Server** no VS Code.

# Parte 2 (Bônus)

Não cheguei a implementar a parte 2, pois não consegui desenvolver a ideia e não tenho o conhecimento prático necessário para trabalhar com o `Range`.

Porém, a ideia que tive foi fazer um processamento em lote do documento enviado, junto com *lazy loading*. Tentei implementar um *generator* com `yield` para renderizar novos *chunks* apenas quando o usuário disparasse o evento de scroll.

Dessa forma, o processamento dos documentos seria muito mais rápido e o documento não precisaria ser carregado inteiro na memória, evitando o risco de estourar o uso.
