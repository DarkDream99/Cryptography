$(document).ready(function() {
    $("#encrypt").click(function() {
        let text = $("#source").val();
        let key = $("#key").val();
        $.get("http://127.0.0.1:8000/des/encrypt/", {text: text, key: key}, function(json_data) {
            let data = JSON.parse(json_data)
            let encrypt_text = data[0];
            let encrypt_text_in_bits = data[1];
            // alert(data[0]);
            // alert(data[1]);

            $("#res_text").text(encrypt_text);
            $("#res_in_bits").text(encrypt_text_in_bits);
        }, "text");
    });
});