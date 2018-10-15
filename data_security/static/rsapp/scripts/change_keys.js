$(document).ready(function () {
    $("#change").click(function () {
        $.get("change_keys/", {}, function(json_data) {
            let data = JSON.parse(json_data);
            let pub_key = data[0];
            let priv_key = data[1];
            $("#public_key").text(pub_key);
            $("#private_key").text(priv_key);
        }, "text");
    });
});