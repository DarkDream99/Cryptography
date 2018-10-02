$(document).ready(function() {
    $("#encrypt").click(function() {
        let text = $("#source").val();
        let key = $("#key").val();
        $.get(HOST + "/des/encrypt/", {text: text, key: key}, function(json_data) {
            let data = JSON.parse(json_data);
            let encrypt_text = data[0];
            let encrypt_text_in_bits = data[1];

            $("#res_text").text(encrypt_text);
            $("#res_in_bits").text(encrypt_text_in_bits);
        }, "text");
    });

    $("#source").change(function() {
        let text = $(this).val();
        $.get("bits/", {text: text}, function(data) {
           let bits =  data;
           $("#source_in_bits").text(bits);
        }, "text");
    });

    $("#key").change(function() {
        let text = $(this).val();
        $.get("bits/", {text: text}, function(data) {
           let bits = data;
           $("#key_in_bits").text(bits);
        }, "text");
    });
});