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
    $("#showchart").click(getChart);
  })


//code to call stackedbarchart if we decide to use
function getChart(){
  team_id = $("#team_id").val()
  if (team_id != ""){
    var urlChart="/SEI/chart_team/"+team_id
    $.get(urlChart).done(function(data){
      var json = JSON.parse(data);
      var chart = stackedBarChart().ygroups(["person", "subcontractor", "travel", "equipment"]);
      dataset=[];
      if (json['resource_allocation'] != null && json['resource_allocation'].length > 0){
        dataset = json['resource_allocation']
      }
      else
        dataset = []
    //dataset=[];

    $( "#stackedbarchart" ).empty();
    d3.select("#stackedbarchart")
    .datum(dataset)
    .call(chart);
  });
  }
}

$(document).ready(function () {
 // code here
  team_id = $("#team_id").val()
  if (team_id != "")
  {
    $("#team").show();
    $("#reporting").show();
    $("#team_details").show();
    $("#budget_resource_chart").show();

   getChart();
  }
});