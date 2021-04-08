# Print system
RESTful service for printing system

## To run on docker:

### Clone the project to your local machine
``` 
https://github.com/Yakovtsovevgeniy/Print-system.git
``` 

### Go to the project directory and enter (docker must be run) on the command line
```
docker-compose up
```

### Wait until the server starts.
### Then create a superuser. To do this, open a command line and enter the following
```
docker exec -it print_system_web /bin/bash
python3 manage.py createsuperuser
```
### In your browser, navigate to the localhost address and login as superuser.
In the list that appears, go to users.
The creation of users is carried out only when filling out the raw data form.
To create an administrator, change the administrator field to true. The dealer is created in the same way with changing the dealer field to true.

In api route the plotter pattern field is used to cut the allowed number of patterns on the plotter and view their statistics.
Administrator creates the ability to print templates on any plotter.
If the user has this template, then he will be able to print the allowed number of these templates on the printer.
By clicking on the id from the list provided, he will be able to enter the number of copies of templates that he wants to print.
