$(document).ready(function () {
    $("#crypt").click(function () {
        let user_name = $("#user_name").val();
        let text = $("#input_text").val();
        $.get("rsa/crypt_text/", {message: text, user_name: user_name}, function(json_data) {
            let data = JSON.parse(json_data);
            let crypted = data;
            $("#result_bytes").text(crypted);
        }, "text");
    });
});
