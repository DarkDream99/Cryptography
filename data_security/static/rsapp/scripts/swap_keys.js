$(document).ready(function () {
    $("#swap_key").click(function () {
        let server_url = $("#server_url").val();
        $.get("set_server_url/", {server_url: server_url}, function () { }, "text");

        let pub_client_key = $("#client_key").val();
        $.get(server_url + "swap_keys/", {public_key: pub_client_key}, function (json_data) {
            let data = JSON.parse(json_data);
            $("#server_key").text(data[0]);
        }, "text");
    });
});