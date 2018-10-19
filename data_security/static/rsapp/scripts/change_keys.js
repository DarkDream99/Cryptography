$(document).ready(function () {
    $("#reload").click(function () {
        let user_name = $("#user_name").val();

        $.get("", {user_name: user_name}, function(json_data) {
            let data = JSON.parse(json_data);
            let pub_key = data["public"];
            let priv_key = data["private"];
            $("#public_key").text(pub_key);
            $("#private_key").text(priv_key);
        }, "text");
    });
});