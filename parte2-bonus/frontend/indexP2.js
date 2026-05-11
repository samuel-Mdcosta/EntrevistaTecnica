var inpuArquivo = document.getElementById("arquivo");
var divStatus = document.getElementById("status");
var divViewer = document.getElementById("viewer");

function validarUpdate(){
    var file = inpuArquivo.files[0];
    var formData = new FormData();
    formData.append("file", file);

    fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData
    }).then(response => {
        if(!response.ok){
            throw new Error("Arquivo não suportado");
        }
        return response.json();
    }).then(data => {
        alert("Arquivo atualizado com sucesso!");
        console.log("sucesso", data);
        renderizarPDF(data.url);
    }).catch(error => {
        alert("Erro ao atualizar o arquivo.");
        inpuArquivo.value = '';
        console.error("Erro:", error);
    });
}


async function renderizarPDF(pdfUrl) {
    divViewer.innerHTML = '';
    divStatus.innerText = 'Carregando PDF...';

    //inicia o carregamento do pdf utilizando o PDF.js
    try {
        // worker configurado globalmente no HTML via workerSrc (CDN)
        // disableAutoFetch impede o prefetch do PDF inteiro em background
        const loadingTask = pdfjsLib.getDocument({
            url: pdfUrl,
            rangeChunkSize: 65536,
            disableAutoFetch: true,
        });

        const pdf = await loadingTask.promise;

        // usa a primeira pagina para dimensionar os placeholders
        const primeiraPage = await pdf.getPage(1);
        const defaultViewport = primeiraPage.getViewport({ scale: 1.5 });

        divStatus.innerText = `${pdf.numPages} páginas — role para renderizar`;

        // renderiza a pagina quando o canvas entra no viewport
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (!entry.isIntersecting) return;

                const canvas = entry.target;
                if (canvas.dataset.rendered) return;
                canvas.dataset.rendered = 'true';
                observer.unobserve(canvas);

                const pageNum = parseInt(canvas.dataset.page);
                pdf.getPage(pageNum).then((page) => {
                    const vp = page.getViewport({ scale: 1.5 });
                    canvas.height = vp.height;
                    canvas.width = vp.width;
                    page.render({ canvasContext: canvas.getContext('2d'), viewport: vp });
                });
            });
        // 200px de margem: comeca a renderizar antes de chegar na pagina
        }, { rootMargin: '200px 0px' });

        // cria placeholders para todas as paginas de uma vez
        for (let n = 1; n <= pdf.numPages; n++) {
            const canvas = document.createElement('canvas');
            canvas.dataset.page = n;
            canvas.height = defaultViewport.height;
            canvas.width = defaultViewport.width;
            canvas.style.cssText = 'display:block; background:#e8e8e8; margin-bottom:8px';
            divViewer.appendChild(canvas);
            observer.observe(canvas);
        }

    } catch (error) {
        console.error('Erro:', error);
        divViewer.innerHTML = '';
        inpuArquivo.value = '';
        divStatus.innerText = 'Erro: ' + error.message;
    }
}
