// $(document).ready(function(){
//    $("#des_action").click(function() {
//        $("label").hide();
//        // alert("DES action!");
//    }) ;
//
//    $("button").dblclick(function() {
//        $(this).hide();
//    });
// });

$(document).ready(function () {
   $("#des_action").on({
       click: function() {
           $("label").hide(1000);
           $("#res_text").text("Hello");
       },
       dblclick: function() {
           $(this).hide();
       }
   });
});