window.setInterval(function() {
	$.ajax({
        type: "POST",  
	 	url: "../user/game.do?TO=getGameInfoAjax",  
	 	data: "game_type=1&search_string=1",  
	 	dataType: "json",
	 	error: function(xhr, textStatus){
	 	   	},
	 	success: function(data) {
	 			var $container = $("#container");
	 					$.each(data, function(idx, value){
	 	 					var $li = $container.find("li.menu[data-id='"+value.gid+"']");
	 	 					if (!$li || $li.length == 0) {
	 	 						return true;
	 	 					}
	 	 					var $mval = $li.find(".master_val");
	 	 					if ($mval.text() != value.mval) {
	 	 						if (!$	li.hasClass("hide")) {
		 	 						if (parseFloat($mval.text()) < parseFloat(value.mval)) {
		 	 							$li.find(".master_change_img").css("top", "-14px").html("<img id='mupdown"+value.gid+"' src='../static/img/gif/odds_up.gif' style='margin:0px;'>");
		 	 						} else {
		 	 							$li.find(".master_change_img").css("top", "14px").html("<img id='mupdown"+value.gid+"' src='../static/img/gif/odds_down.gif' style='margin:0px;'>");
		 	 						}
		 	 						window.setTimeout(function() {
		 	 							$("#mupdown"+value.gid).remove();
		 	 						}, 15000);
	 	 						}

	 	 						$mval.text(value.mval);
	 	 					}
	 	 					var $gval = $li.find(".guest_val");
	 	 					if ($gval.text() != value.gval) {
	 	 						if (!$li.hasClass("hide")) {
		 	 						if (parseFloat($gval.text()) < parseFloat(value.gval)) {
		 	 							$li.find(".guest_change_img").css("top", "-14px").html("<img id='gupdown"+value.gid+"' src='../static/img/gif/odds_up.gif' style='margin:0px;'>");
		 	 						} else {
		 	 							$li.find(".guest_change_img").css("top", "14px").html("<img id='gupdown"+value.gid+"' src='../static/img/gif/odds_down.gif' style='margin:0px;'>");
		 	 						}
		 	 						window.setTimeout(function() {
		 	 							$("#gupdown"+value.gid).remove();
		 	 						}, 15000);
	 	 						}

	 	 						$gval.text(value.gval);
	 	 					}
	 	 					if (value.type == "1") {
		 	 					var $pval = $li.find(".peace_val");
		 	 					if ($pval.text() != value.pval) {
		 	 						$pval.text(value.pval);
		 	 					}
	 	 					} else {
		 	 					var $rval = $li.find(".reference_val");
		 	 					if ($rval.text() != value.rval) {
		 	 						$rval.text(value.rval);
		 	 					}
	 	 					}
	 	 					if (value.status == "2") {
		 	 					if ($li.attr("data-status") != value.status) {
	 	 							$li.attr("data-status", "2");
	 	 							$li.find("div.choice").removeAttr("onclick").css("color", "#666666").removeClass("choice_on");
	 	 							$li.find("span.gameStatus").css( "color", "red" ).text( "마감" );
		 	 					}
	 	 					}
	 	 				});
	 	 			}
	 	 		});
	 		}, 5000);