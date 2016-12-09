function getProjectInfo(){
    var PWP_num=$("#search_input").val().toLowerCase();
    var url="overview/"+PWP_num;
    d3.json(url, function(error, json) {
       if (error) return console.warn(error);
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
                console.log(d.charge);
                return d.charge                
             })
       }
    });
}

function getBudgetInfo(){
    var PWP_num=$("#search_input").val().toLowerCase();
    var url="budget/"+PWP_num;
    d3.json(url, function(error, json) {
       if (error) return console.warn(error);
       d3.select("#project_budget_balance").text(json['project_budget'])
       d3.select("#budget_balance").text(json['budget_balance'])
       d3.select("#project_spend").text(json['projected_spend'])
       d3.select("#project_remain").text(json['projected_remaining'])
       /*for(var i=0;i<json.monthly_expense.length;i++){
           d3.select("#monthly_expense_list").select("p")
             .data(json.monthly_expense)
             .enter()
             .append("p")
             .text(function(d){
                return "Year:"+d.year+"  Month:"+d.month+" Budget:"+d.budget+" Expense:"+d.expense
             })
       }*/
    });
}

function getResourceAllocationChart(){
    var PWP_num=$("#search_input").val().toLowerCase();
    var year = 2016;
    var url="resource/"+PWP_num+"/"+year;
    var dataset = []
    d3.json(url, function(error, json) {
       if (error) return console.warn(error);
       dataset = json['resource_allocation']
    });
    // draw Visavail.js chart
    var chart = visavailChart().width(800);
    //dataset=[];
    $( "#visavailchart" ).empty();
    d3.select("#visavailchart")
            .datum(dataset)
            .call(chart);
}

$(function(){
    d3.select("#search_btn").on("click",function(){

        getProjectInfo();
        getBudgetInfo();
        getResourceAllocationChart();
        var PWP_num=$("#search_input").val().toLowerCase();
        var form=$("#editform")
        form.attr('action','/SEI/edit_project/'+PWP_num)
        $("#header").show();
        $("#project_details").show();
        $("#resource_chart").show();
        $("#reporting").show();
    })
})

