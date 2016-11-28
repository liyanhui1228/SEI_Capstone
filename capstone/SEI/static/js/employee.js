function getEmployeList(){
  var input=$("#search_input").val().toLowerCase().split(/\s+/g);
  var first_name=input[0];
  var last_name=input[1];
  var url="/SEI/get_employee/"+first_name+"/"+last_name;
  $.get(url)
  .done(function(data) {
      for(var i=0;i<data.length;i++){
        var employee_list=$("#employee_list");
        employee=data[i];
        var employee_name=employee["first_name"]+" "+employee["last_name"];
        var team_name=employee.team_name;
        var employee_id=employee.id;
        employee_list.append("<li class='list-group-item' id=\""+employee_id+"\">Name:"+employee_name+"\tTeam:"+team_name+"</li>");
      }
      $('#myModal').modal({show:true});
  });
}

function showContent(e){
  var employee_id=$(e.target).attr("id");
  var employee_name=$(e.target).text();
  $("#header").show()
  $("#employee_name").text(employee_name)
  $("#morris-donut-chart").empty()
  $("#morris-line-chart").empty()
  var url="/SEI/get_employee_project/"+employee_id;
  $.get(url)
   .done(function(data){
      renderDonutChart(data);
      renderLineChart(data);
      renderAllocationChart(data);
   });
}

function removeModal(){
  var employees=$("#employee_list").children("li");
  for(var i=0;i<employees.length;i++){
    $(employees[i]).remove();
  }
}

function renderDonutChart(data){
    var json=JSON.parse(data)
    var donut_chart=$("#donut_chart")
    donut_chart.hide()
    var d = new Date();
    var currentmonth = d.getYear()+1900+"-"+(d.getMonth()+1)+"-01";
    donut_data=[]
    if(currentmonth in json){
      month_data=json[currentmonth]
      for(var i=0;i<month_data.length;i++){
        donut_data.push({label:month_data[i].PWP_num,value:month_data[i].time_use})
      }
    }
    donut_chart.show()
    if(donut_data.length!=0){
        Morris.Donut({
            element: 'morris-donut-chart',
            data: donut_data,
            resize:true
      });
   }
}

function renderLineChart(data){
    var json=JSON.parse(data)
    var line_chart=$("#line_chart");
    line_chart.hide();
    var linechart_data=[]
    var PWP_nums=[]
    for(var month in json){
        var dict=[]
        dict['d']=month;
        var month_project=json[month];
        for(var i=0;i<month_project.length;i++){
          var PWP_num=month_project[i]["PWP_num"];
          var percentage=month_project[i]["percentage"];
          dict[PWP_num]=percentage;
          if(PWP_nums.indexOf(PWP_num)==-1){
             PWP_nums.push(PWP_num);
          }
        }
        linechart_data.push(dict);
    }
    line_chart.show();
    if(linechart_data.length!=0){
      var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    // Line Chart
    Morris.Line({
        // ID of the element in which to draw the chart.
        element: 'morris-line-chart',
        // Chart data records -- each entry in this array corresponds to a point on
        // the chart.
        data: linechart_data,
        // The name of the data record attribute that contains x-visitss.
        xkey: 'd',
        // A list of names of data record attributes that contain y-visitss.
        ykeys: PWP_nums,
        // Labels for the ykeys -- will be displayed when you hover over the
        // chart.
        labels: PWP_nums,
        // Disables line smoothing
        smooth: false,
        resize: true,
        xLabelFormat: function (x) { return x.getYear()-100+"-"+months[x.getMonth()];}
    });
    }
}

  function renderAllocationChart(data){
        var resourcerow=$("#resource_chart");
        resourcerow.show();

  }


$(function(){
    $("body").on('hidden.bs.modal', '.modal', function () {
       removeModal();
    });
    $("#search_btn").click(getEmployeList);
    $("#employee_list").on("click","li",showContent);
})