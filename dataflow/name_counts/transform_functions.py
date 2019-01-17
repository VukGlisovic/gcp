import apache_beam as beam


class SplitAndFilterNames(beam.DoFn):

    def __init__(self):
        super(SplitAndFilterNames, self).__init__()

    def process(self, element, *args, **kwargs):
        filter_letters = kwargs['filter_letters']
        for string in element:
            if string[0] not in filter_letters:
                yield string.split(':')


class GetFirstName(beam.DoFn):

    def __init__(self):
        super(GetFirstName, self).__init__()

    def process(self, element, *args, **kwargs):
        name, age = element
        first_name = name.split(' ')[0]
        yield first_name, age


class GetLastName(beam.DoFn):

    def __init__(self):
        super(GetLastName, self).__init__()

    def process(self, element, *args, **kwargs):
        name, age = element
        last_name = name.split(' ', 1)[1]
        yield last_name, age

