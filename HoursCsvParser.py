import sys
import csv
import datetime
import os.path
import argparse

config = None
field_names = ['date', 'start', 'finish', 'pause', 'total']


def __open_file(f):
    """ Safely opens a file

    :param f: The file or path to open
    :return: A file object for reading

    :exception IOError: File does not exist or can not be read
    """
    if isinstance(f, basestring):
        is_exists = os.path.exists(f)
        is_file = os.path.isfile(f)
        if is_exists and is_file:
            return open(f, 'r')
    elif isinstance(f, file):
        return f
    raise IOError()


def __parse_year(l):
    """ Parse the year from the header line

    :param l: The header line
    :return: The year as an Integer or None if parsing failed
    """
    words = l[0].split(' ')
    return int(words[2])


def __parse_time(s):
    """ Parse s as a time object

    :param s: The string to parse
    :return: The time as a time object
    """
    return datetime.datetime.strptime(s, '%H:%M').time()


def __to_timedelta(t):
    """ Convert the time object into a timedelta

    :param t: The time to convert to a timedelta
    :return: A timedelta representing the same hours and minutes as t
    """
    return datetime.timedelta(hours=t.hour, minutes=t.minute)


def __parse_timedelta(s):
    """ Parses a string into a timedelta with minute precision

    :param s: Parse the string into a timedelta
    :return: A timedelta
    """
    return __to_timedelta(__parse_time(s))


def __parse_day(lines, project, current_line, year):
    """ Parses a single day

    :param lines: The contents of the file
    :param project: The project to filter for, will assume only one project in file if None
    :param current_line: The line number to continue parsing
    :param year: the initial year in the file
    :return: A { 'date': ..., 'start': ..., 'finish': ..., 'pause': ..., 'total': ..., 'lines': ... } dictionaries or
             None if it could not be parsed
    """
    i = current_line
    res = {}

    if len(lines[i]) == 0:
        return None
    while i + 1 < len(lines):
        if len(lines[i + 1]) == 0:
            i += 1
        elif lines[i + 1][0] == '[No entries]':
            i += 3
        elif lines[i + 1][0] == 'GRAND TOTAL':
            return None
        else:
            break
    if lines[i][0] == 'GRAND TOTAL':
        return None

    date_string = '%s %d' % (lines[i][0], year)
    res['date'] = datetime.datetime.strptime(date_string, '%A, %d %B %Y').date()
    res['pause'] = datetime.timedelta()
    i += 1

    while lines[i][0] != 'Total':
        if project is None or lines[i][0] == project:
            try:
                if 'start' not in res.keys():
                    res['start'] = __parse_time(lines[i][1])
                else:
                    tmp_start = res['finish']
                    tmp_finish = __parse_time(lines[i][1])
                    timedelta_start = __to_timedelta(tmp_start)
                    timedelta_finish = __to_timedelta(tmp_finish)
                    res['pause'] += timedelta_finish - timedelta_start
                res['finish'] = __parse_time(lines[i][2])
            except:
                if config is not None and config.verbose:
                    print 'Could not parse: %s' % lines[i]
        i += 1

    # Calculate the total time
    res['total'] = __to_timedelta(res['finish']) - __to_timedelta(res['start']) - res['pause']

    res['lines'] = i - current_line

    return res


def parse(file_or_path, project=None):
    """ Parse a file

    :param file_or_path: The file to parse or a path to the file
    :param project: The project to filter for, will assume only one project in file if None
    :return: An list of { 'date': ..., 'start': ..., 'finish': ..., 'pause': ..., 'total': ... } dictionaries

    :exception IOError: File does not exist or can not be read
    """
    with __open_file(file_or_path) as f:
        data = csv.reader(f)
        lines = []
        for line in data:
            lines.append(line)
        current_line = 1
        year = __parse_year(lines[current_line])

        current_line += 2
        res = []
        day = __parse_day(lines, project, current_line, year)
        while day is not None:
            res.append(day)
            # Add two lines to skip the gap between different days in the file
            current_line += day['lines'] + 2
            day = __parse_day(lines, project, current_line, year)

        return res


def __output(outfile, results, fields):
    with outfile:
        writer = csv.DictWriter(outfile, fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(results)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('input', type=argparse.FileType('r'), help='The input file to read from')
    parser.add_argument('output', type=argparse.FileType('w'), nargs='?', default=sys.stdout,
                        help='The output file. Will print to stdout if not specified')
    parser.add_argument('--project', default=None,
                        help='The project to filter if more than one project was exported by Hours. Will use all project is not specified')

    global config
    config = parser.parse_args()

    results = parse(config.input, config.project)
    __output(config.output, results, field_names)


if __name__ == '__main__':
    main()
