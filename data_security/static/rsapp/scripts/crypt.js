$(document).ready(function () {
    $("#crypt").click(function () {
        let text = $("#input_text").val();
        $.get("rsa/crypt_text/", {message: text}, function(json_data) {
            let data = JSON.parse(json_data);
            let crypted = data[0]
            $("#result_bytes").text(crypted);
        }, "text");
    });
});
