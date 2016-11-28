function getTeamList(){
  var team_name=$("#search_input").val().toLowerCase();
  var url="/SEI/get_team/"+team_name;
  $.get(url)
  .done(function(data) {
      for(var i=0;i<data.length;i++){
        var team_list=$("#team_list");
        team=data[i];
        var team_name=team.team_name;
        var team_id=team.id;
        team_list.append("<li class='list-group-item' id=\""+team_id+"\">Team:"+team_name+"</li>");
      }
      if(data.length == 1)
        showContent(this, team_id);
      else
        $('#myModal').modal({show:true});
  });
}

function showContent(e, team_id){
  if (!team_id)
    team_id=$(e.target).attr("id");
  var url="/SEI/team/"+team_id;
  window.location.replace(url);
}

function redirectProject(e){
    PWP_num=$(this).find('td:first').text();


}

$(function(){
    $("#search_btn").click(getTeamList);

    // $("#myModal").on("show.bs.modal", getEmployeList);
    $("#team_list").on("click","li",showContent);
    $("#project_list").on("click","tr",redirectProject);
})



//code for stackedbarchart if we decide to youse
/*




*/