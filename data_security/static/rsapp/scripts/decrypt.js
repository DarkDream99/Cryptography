$(document).ready(function () {
    $("#decrypt").click(function () {
        $.get("rsa/decrypt_bits/", {}, function(json_data) {
            let data = JSON.parse(json_data);
            let decrypt = data[0];
            $("#decrypt_text").text(decrypt);
        }, "text");
    });
});