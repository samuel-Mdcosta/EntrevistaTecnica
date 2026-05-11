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

## Como iniciar

### Backend

1. Acesse a pasta do backend:

   ```bash
   cd parte2-bonus\backend
   ```

2. Instale as dependências:

   ```bash
   pip install fastapi uvicorn python-multipart networkx
   ```

3. Inicie o servidor:

   ```bash
   uvicorn mainP2:app --reload
   ```

   O backend ficará disponível em `http://localhost:8000`.

### Frontend

Abra o arquivo [parte2-bonus/frontend/index.html](frontend/index.html) diretamente no navegador, pois live server bloqueia a renderizacao por pagina

Entregue no Domingo, dia 10/05.

### Decisões de implementação

**Lazy Loading com IntersectionObserver:** as páginas só são renderizadas quando entram no viewport durante o scroll. O `IntersectionObserver` observa cada canvas placeholder e dispara a renderização individualmente, evitando processar todo o documento de uma vez.

**Placeholders dimensionados antecipadamente:** ao carregar o PDF, a primeira página é usada para calcular as dimensões padrão. Todos os canvas são criados com esse tamanho antes de qualquer renderização — por isso a barra de scroll já reflete o tamanho real do documento logo após o upload.

**Upload em chunks com walrus operator:** o backend lê o arquivo enviado em blocos de 1MB usando o operador walrus (`while chunk := await file.read(CHUNK_SIZE)`), evitando carregar o PDF inteiro na memória durante o salvamento.

**Range Requests (HTTP 206):** o frontend usa `rangeChunkSize` para que o PDF.js busque apenas os bytes necessários por página via `Range: bytes=X-Y`, e o backend responde com `206 Partial Content` lendo apenas o trecho solicitado via `seek` + `read`.

**Redirecionamento automático pós-upload:** após o upload bem-sucedido, o viewer é inicializado automaticamente sem necessidade de ação adicional do usuário.

### Pipeline completo

**POST /upload**

1. Frontend envia o arquivo via `FormData`
2. Backend valida `content_type == application/pdf`
3. Arquivo salvo em disco em chunks de 1MB
4. Retorna `{ url: "http://localhost:8000/pdf/{filename}" }`
5. Frontend chama `renderizarPDF(url)`

**GET /pdf/{filename}**

1. PDF.js solicita trechos do arquivo via `Range: bytes=X-Y`
2. Backend faz `seek(start)` + `read(chunk_length)` — sem carregar o arquivo inteiro na memória
3. Responde com `206 Partial Content` e `Content-Range: bytes X-Y/total`
4. `loadingTask.promise` resolve com o objeto `pdf` (metadados e estrutura do documento)
5. Placeholders criados para todas as páginas com dimensões corretas
6. Ao rolar, cada canvas que entra no viewport dispara `pdf.getPage(n)` → nova range request → renderização → canvas desobservado
