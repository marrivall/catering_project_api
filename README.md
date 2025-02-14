1)  the guide to load test data from your fixtures files. 
- Create new directory named 'fixtures' by the command 'mkdir fixtures' or in the Explorer
- Create test data file inside of the 'fixtures', foe example 'file_name.json'
- Open 'file_name.json' file and add test data to it
- If the encoding is not UTF-8, change it and save the file.
- Save file and enter the command in the terminal 'python manage.py loaddata file_name.json'

2) Explain why you chose either JSON or CSV format.
I chose JSON because it makes model relationships easier to manage, it is also suitable for working with complex and diverse data and structures. It makes it easier to process in web applications that often need to process different types of information