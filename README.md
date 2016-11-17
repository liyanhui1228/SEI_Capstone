# SEI_Capstone

(1) JSON required from the front end for add_employee:

```
{  
   "PWP_num":12,
   "project_date":"2016-11-01",
   "emp_chosen_list":{  
      "3":{  
         "time_to_use":20,
         "is_external":1,
         "month_cost":500
      }
   }
}
```
(2) JSON returned from view_employee_list:
```
{
   "employee_available":{
      "3":{
         "name":"jamie stein",
         "percentage_used":30.0
      },
      "4":{
         "name":"sakir yucel",
         "percentage_used":60.0
      }
   },
   "employee_in_this_project":{
      "1":"xiaowei li",
      "2":"dawei li"
   }
}
```

