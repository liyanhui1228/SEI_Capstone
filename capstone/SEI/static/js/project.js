function getProjectInfo(PWP_num){
    // var PWP_num=$("#search_input").val().toLowerCase();
    var url="/SEI/overview/"+PWP_num;
    d3.json(url, function(error, json) {
       //if (error) return console.warn(error);
       d3.select("#PWP_num").text(json['PWP_num'])
       d3.select("#project_description").text(json['project_description'])
       d3.select("#project_budget_overview").text(json['project_budget'])
       d3.select("#isExternal").text(json['isExternal'])
       d3.select("#start_date").text(json['start_date'])
       d3.select("#end_date").text(json['end_date'])
       d3.select("#organization_name").text(json['organization_name'])
       d3.select("#team_name").text(json['team_name'])
       $("#charge_string_list").empty();
       for(var i=0;i<json.charge_string.length;i++){
           d3.select("#charge_string_list").selectAll("p")
             .data(json.charge_string)
             .enter()
             .append("p")
             .text(function(d){
                return d.charge                
             })
       }
    });
}

function getBudgetInfo(PWP_num){
    //var PWP_num=$("#search_input").val().toLowerCase();
    var url="/SEI/budget/"+PWP_num;
    d3.json(url, function(error, json) {
       //if (error) return console.warn(error);
       d3.select("#project_budget_balance").text(json['project_budget'])
       d3.select("#budget_balance").text(json['budget_balance'])
       d3.select("#project_spend").text(json['projected_spend'])
       d3.select("#project_remain").text(json['projected_remaining'])
    });
}

function openResourceAllocation(project_date,PWP_num){
  var PWP_num=$("#search_input").val().toLowerCase();
  var parts = project_date.split('/');
  var month = parts[0];
  var year = parts[2];
  var url="/SEI/add_resources/"+PWP_num+"/"+year+"/"+month;
  window.location.replace(url);
}

function getResourceAllocationChart(year,PWP_num){
    //var PWP_num=$("#search_input").val().toLowerCase();
    var url="/SEI/resource/"+PWP_num+"/"+year;
    var dataset = [];
    $( "#visavailchart" ).empty();

    $.get(url).done(function(data){
      var dataset = [];
      var json = JSON.parse(data);
      if (json['resource_allocation'] != null && json['resource_allocation'].length > 0){
        dataset = json['resource_allocation']
      }
          // draw Visavail.js chart
    var chart = visavailChart().xaxis_link(openResourceAllocation).chart_year(year);
    //dataset=[];
    d3.select("#visavailchart")
            .datum(dataset)
            .call(chart);

    });
}

function renderContent(PWP_num){
  $("#last_year").click(function(){
    var last_year = parseInt($("#year").text()) - 1;
    $("#year").text(last_year);
    getResourceAllocationChart(last_year,PWP_num);
  });

    $("#next_year").click(function(){
    var next_year = parseInt($("#year").text()) + 1;
    $("#year").text(next_year);
    getResourceAllocationChart(next_year,PWP_num);
  });
  getProjectInfo(PWP_num);
  getBudgetInfo(PWP_num);
  var year=new Date().getFullYear();
  $("#year").text(year);
  getResourceAllocationChart(year,PWP_num);
  var form=$("#editform")
  form.attr('action','/SEI/edit_project/'+PWP_num)
  $("#header").show();
  $("#project_details").show();
  $("#resource_chart").show();
  $("#reporting").show();
  var repform=$("#reportform")
  repform.attr('action','/SEI/report_project/'+PWP_num)
}

$(function(){
    
    d3.select("#search_btn").on("click",function(){
      var PWP_num=$("#search_input").val().toLowerCase();
      renderContent(PWP_num); 
    });

  function reloadResourceAllocationChart(year){
      var PWP_num = d3.select("#PWP_num").text();
      var url="resource/"+PWP_num+"/"+year;
      var dataset = [];
      $.get(url).done(function(data){
        var json = JSON.parse(data);
        if (json['resource_allocation'] != null && json['resource_allocation'].length > 0){
          dataset = json['resource_allocation']
        }
            // draw Visavail.js chart
      //var chart = visavailChart().xaxis_link(openResourceAllocation);
      //dataset=[];
      d3.select("#visavailchart")
              .datum(dataset)
              .call(redraw);
      });
  }

  if($("#PWP_num").val()!=""){
      renderContent($("#PWP_num").val());
  }

})
