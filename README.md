A simple parser for exports generated by [https://hourstimetracking.com](https://hourstimetracking.com/) to translate into standard CSV files

# Usage
It has a simple command line interface with the following arguments

```
HoursCsvParser.py [-h] [-v] [--project PROJECT] input [output]

positional arguments:
  input              The input file to read from
  output             The output file. Will print to stdout if not specified

optional arguments:
  -h, --help         show this help message and exit
  -v, --verbose
  --project PROJECT  The project to filter if more than one project was
                     exported by Hours. Will use all project is not specified
```

# Example
```bash
$ cat input.txt
"Daily Time Detail -- All Projects"
"12 October 2015 to 12 October 2015"

"MONDAY, 12 OCTOBER"
"project1","9:00","12:00",3:00,""
"project1","13:00","18:00",5:00,""
"project2","18:00","18:30",0:30,""
Total,8:30


GRAND TOTAL,8:30

$ python HoursCsvParser.py input.txt --project=project1
date,start,finish,pause,total
2015-10-12,09:00:00,18:00:00,1:00:00,8:00:00

$ python HoursCsvParser.py input.txt --project=project2
date,start,finish,pause,total
2015-10-12,18:00:00,18:30:00,0:00:00,0:30:00

$ python HoursCsvParser.py input.txt
date,start,finish,pause,total
2015-10-12,09:00:00,18:30:00,1:00:00,8:30:00
```

