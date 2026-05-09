var inpuArquivo = document.getElementById("arquivo");

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
        const blob = new Blob([file], { type: 'application/pdf' });
        const creatObjUrl = URL.createObjectURL(blob);
        window.open(creatObjUrl, "_blank");
        console.log("sucesso", data);
    }).catch(error => {
        alert("Erro ao atualizar o arquivo.");
        inpuArquivo.value = '';
        console.error("Erro:", error);
    });
}