// $(document).ready(function () {
//     $("#send").click(function () {
//         let input_bytes = $("#input_bits").val();
//         let server_url_text = $("#server_url").val();
//
//         $.ajax({
//             type: "POST",
//             url: server_url_text + "send_text",
//             data: JSON.stringify({message: input_bytes}),
//             contentType: "application/json; charset=utf-8",
//             dataType: "json",
//             success: function (json_bytes) {
//                 let res_bytes = JSON.parse(json_bytes);
//                 $("result_bits").text(res_bytes);
//             }
//         });
//     });
// });