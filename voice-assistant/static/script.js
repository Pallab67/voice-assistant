function startRecording() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = "en-US";

    recognition.start();
    document.getElementById("response").innerText = "Listening... 🎙️";

    recognition.onresult = function(event) {
        let speechText = event.results[0][0].transcript;
        document.getElementById("response").innerText = "You said: " + speechText;

        // Send speechText to Python backend
        $.ajax({
            type: "POST",
            url: "/process",
            contentType: "application/json",
            data: JSON.stringify({ text: speechText }),
            success: function(response) {
                document.getElementById("response").innerText = "AI: " + response;
            }
        });
    };
}
