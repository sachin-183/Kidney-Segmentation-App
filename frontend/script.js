async function uploadImage(){

    const fileInput = document.getElementById("imageInput");

    if(fileInput.files.length === 0){
        alert("Please select an image");
        return;
    }

    const file = fileInput.files[0];

    const formData = new FormData();
    formData.append("file", file);

    // show original image
    document.getElementById("originalImage").src =
        URL.createObjectURL(file);

    try{

        const response = await fetch("http://127.0.0.1:8000/predict",{
            method:"POST",
            body:formData
        });

        console.log(response);

        const data = await response.json();

        console.log(data);

        const byteArray = new Uint8Array(
            data.overlay.match(/.{1,2}/g).map(byte => parseInt(byte,16))
        );

        const blob = new Blob([byteArray], {type:"image/png"});
        const url = URL.createObjectURL(blob);

        document.getElementById("resultImage").src = url;

    }catch(error){
        console.error(error);
        alert("Prediction failed");
    }
}