import apache_beam as beam
import logging


class SplitAndFilterNames(beam.DoFn):

    def __init__(self):
        super(SplitAndFilterNames, self).__init__()

    def process(self, element, *args, **kwargs):
        filter_letters = kwargs['filter_letters']
        for string in element:
            if string[0] not in filter_letters:
                yield string.split(':')
