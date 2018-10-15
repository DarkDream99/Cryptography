$(document).ready(function () {
    $("#swap_key").click(function () {
        let server_url = $("#server_url").val();
        $.get("set_server_url/", {server_url: server_url}, function () { }, "text");

        // let pub_client_key = $("#client_key").val();
        let pub_key;

        $.get("public_keys/", {}, function (json_data) {
            pub_key = JSON.parse(json_data);

            $.ajax({
                type: "GET",
                url: server_url + "swap_keys",
                data: {pub_key: json_data},
                contentType: "application/json; charset=utf-8",
                dataType: "jsonp",
                success: function(json_data_swap) {
                    let server_pub_key = JSON.parse(json_data_swap);

                     $.get("server_key/", {e: server_pub_key.e, n: server_pub_key.n}, function (json_data_skey) {
                        $("#server_key").text(json_data_skey);
                     });
                }
            });
        }, "text");
    });
});