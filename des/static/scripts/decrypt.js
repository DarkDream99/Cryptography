$(document).ready(function() {
    $("#decrypt").click(function() {
        let code_bits = $("#encrypt_bits").val();
        let key = $("#key").val();
        $.get("http://192.168.0.103:8000/des/decrypt/", {code: code_bits, key: key}, function(json_data) {
            let data = JSON.parse(json_data);
            let decrypt_text = data[0];
            let decrypt_text_in_bits = data[1];

            $("#res_text").text(decrypt_text);
            $("#res_in_bits").text(decrypt_text_in_bits);
        }, "text");
    });

    $("#encrypt_bits").change(function() {
        let bits = $(this).val();
        $.get("text/", {bits: bits}, function(data) {
           let text =  data;
           $("#encrypt_text").text(text);
        }, "text");
    });

    $("#key").change(function() {
        let text = $(this).val();
        $.get("http://192.168.0.103:8000/des/encrypt/bits/", {text: text}, function(data) {
           let bits = data;
           $("#key_in_bits").text(bits);
        }, "text");
    });
});