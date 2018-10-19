$(document).ready(function () {
    $("#swap_key").click(function () {
        let server_url_text = $("#server_url").val();

        $.get("set_server_url/", {server_url: server_url_text}, function () {
            alert("URL was saved");
        });

        $.get("public_keys/", {}, function (json_data) {
            // pub_key = JSON.parse(json_data);

            $.ajax({
                type: "POST",
                url: server_url_text + "swap_keys",
                data: JSON.stringify(json_data),
                contentType: "application/json; charset=utf-8",
                dataType: "json",
                success: function(json_data_swap) {
                    alert(json_data_swap);
                    let server_pub_key = json_data_swap;

                     $.get("server_key/", {e: server_pub_key.e, n: server_pub_key.n}, function (json_data_skey) {
                        $("#server_key").text(json_data_skey);
                     });
                }
            });
        });
    });
});