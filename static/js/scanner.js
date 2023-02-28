// Custom Scanner API for the Html5Qrcode library

// create scanner instance
let html5QrCode;

// functionality
function initScanner(id) {
    html5QrCode = new Html5Qrcode(id);
}

function startScanning(width, height, callback) {
    const config = { fps: 10, qrbox: { width: width, height: height } };
    html5QrCode.start({ facingMode: "environment" }, config, callback)
    .catch(error => {
        alert("No camera was found!");
    });
}
function stopScanning() {
    html5QrCode.stop().then(ignore => {
        // stopped scanning, idle
    }).catch(err => {
        alert("error: camera can`t stop!");
    });
}