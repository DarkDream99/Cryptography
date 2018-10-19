$(document).ready(function () {
    $("#decrypt").click(function () {
        let user_name = $("#user_name").val();
        let crypt_bytes = $("#bits").val().split(',');

        for (let i = 0; i < crypt_bytes.length; ++i) {
            crypt_bytes[i] = parseInt(crypt_bytes[i])
        }

        $.get(
            "rsa/decrypt_bits/",
            {
                user_name: user_name,
                crypt_bytes: JSON.stringify(crypt_bytes)
            },
            function(json_data) {
                let data = JSON.parse(json_data);
                let decrypt = data;
                $("#decrypt_text").text(decrypt);
            },
            "text"
        );
    });
});