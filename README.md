# SEI_Capstone

## Project Directory Structure (please not make any changes on structure)
```
capstone/
├── capstone/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
|── manage.py
|── db.sqlite3
|── SEI/
README.md
.gitignore
.git
```


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
#Issues
## Employee View (quick note for next meeting)
1. The herf of employee view seems not working, http://localhost:8000/SEI/employee not work, we need to add a / after that to make it work. which means it's http://localhost:8000/SEI/employee/
2. The allocation graph in employee view has some design issue like the start month not showing up as january but 2016.
