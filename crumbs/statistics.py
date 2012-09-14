# Copyright 2012 Jose Blanca, Peio Ziarsolo, COMAV-Univ. Politecnica Valencia
# This file is part of seq_crumbs.
# seq_crumbs is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# seq_crumbs is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR  PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with seq_crumbs. If not, see <http://www.gnu.org/licenses/>.

from __future__ import division
from array import array

from crumbs.settings import MAX_BINS, MIN_BINS, MEAN_VALUES_IN_BIN

class IntsStats(object):
    '''This is an array that counts the values.
    a = IntsStats()
    print (a)
    []
    a.append(5)
    print a
    a= [0,0,0,0,1]

    '''
    def __init__(self, iterable=None, init_len=None, max_len=None):
        'the initiator'
        if init_len is None:
            init_len = 10
        self._array = array('I', [0] * init_len)
        if max_len is None:
            max_len = 100000000
        if iterable is not None:
            self.extend(iterable)

    def extend(self, values):
        'It adds all the values from an iterable'
        for value in values:
            self.append(value)

    def append(self, value):
        'It appends a value to the array'
        try:
            self._array[value] += 1
        except IndexError:
            new_len = value * 2
            new_array = array('I', [0] * new_len)
            for index, value_ in enumerate(self._array):
                new_array[index] = value_

            self._array = new_array
            del(new_array)
            self._array[value] += 1

    def _get_flat(self):
        'It yields all integers counted'
        for val, count in enumerate(self._array):
            # pylint: disable=W0612
            for i in range(count):
                yield val
    flat = property(_get_flat)

    def _get_min(self):
        'Get minimun value'
        for index, value in enumerate(self._array):
            if value != 0:
                return index
    min = property(_get_min)

    def _get_max(self):
        'get_maxvalue'
        for index in xrange(len(self._array) - 1, 0, -1):
            if self._array[index] != 0:
                return index
        return 0
    max = property(_get_max)

    def _get_count(self):
        'It returns the count of the values appended'
        return sum(self._array)
    count = property(_get_count)

    def _get_median(self):
        'It calculates the median of the values appended'
        median_positions = self._get_quartile_positions()['median']
        return self._get_value_of_position(median_positions)
    median = property(_get_median)

    def _calculate_average(self):
        'It calculates the average'
        count = self.count
        sum_ = self.sum
        return sum_ / count
    average = property(_calculate_average)

    def _get_sum(self):
        'It gets the sum of the values'
        sum_ = 0
        for index, value in enumerate(self._array):
            sum_ += (index * value)
        return int(sum_)
    sum = property(_get_sum)

    def _get_variance(self):
        'It gets the variance of the values'
        mean = self.average
        sum_ = 0
        for index, counts in enumerate(self._array):
            sum_ += ((index - mean) ** 2) * counts
        return sum_ / self.count
    variance = property(_get_variance)

    def _count(self):
        'It returns the number of values that there are in the array'
        return int(sum(self._array))
    count = property(_count)

    def _get_quartile_positions(self):
        'It returns the positions of the quartiles and the median'
        def _get_median_position(num_len):
            'It calculates the center position of the array'
            quotient, remainder = divmod(num_len, 2)
            if remainder == 0:
                position = (quotient, quotient + 1)
            else:
                position = (quotient + 1, quotient + 1)
            return position

        quartiles = {}
        num_values = self.count
        median_position = _get_median_position(num_values)

        quartiles['median'] = median_position
        quartiles['quartile_1'] = _get_median_position(median_position[0])
        quartiles['quartile_2'] = _get_median_position(median_position[0] +
                                                                    num_values)
        return quartiles

    def _get_value_of_position(self, positions):
        '''It takes a tuple as a position and it returns the value
        of the given position'''
        def _next_position_with_value(index):
            '''Giving a position in the array, it returns the next position
            with a value

                a = [8,4,0,0,2]
                4 = _next_position_with_value(1)
            '''
            for i, values  in enumerate(self._array):
                if i > index and values != 0:
                    return i
        value_pos = 0
        for index, values in enumerate(self._array):
            value_pos += values
            if positions[0] == value_pos:
                pos1 = index
                pos2 = _next_position_with_value(index)
                return (pos1 + pos2) / 2
            if positions[0] < value_pos:
                return index

    def _get_iqr(self):
        'It gets the inter quartil range'
        quart_pos = self._get_quartile_positions()
        quart_1 = self._get_value_of_position(quart_pos['quartile_1'])
        quart_2 = self._get_value_of_position(quart_pos['quartile_2'])
        iqr = quart_2 - quart_1
        return iqr
    irq = property(_get_iqr)

    def _get_outlier_limits(self):
        'It returns the intercuartile'
        quart_pos = self._get_quartile_positions()
        quart_1 = self._get_value_of_position(quart_pos['quartile_1'])
        quart_2 = self._get_value_of_position(quart_pos['quartile_2'])

        iqr = self.irq
        limit_distance = round(iqr * 1.5)

        start = int(quart_1 - limit_distance)
        end = int(quart_2 + limit_distance)
        return (start, end)
    outlier_limits = property(_get_outlier_limits)

    def _calculate_dist_range(self, min_, max_, remove_outliers):
        'it calculates the range for the histogram'
        if min_ is None:
            min_ = self.min
        if max_ is None:
            max_ = self.max

        if remove_outliers:
            left_limit = self.count * remove_outliers / 100
            rigth_limit = self.count - left_limit
            left_value = self._get_value_of_position((left_limit, left_limit))
            rigth_value = self._get_value_of_position((rigth_limit,
                                                       rigth_limit))

            if min_ < left_value:
                min_ = left_value
            if max_ > rigth_value:
                max_ = rigth_value
        return min_, max_

    def calculate_bin_edges(self, min_, max_, n_bins=None):
        'It calculates the bin_edges'
        if n_bins is None:
            num_values = max_ - min_
            if num_values == 0:
                n_bins = 1
            elif num_values < MIN_BINS:
                n_bins = num_values
            else:
                n_bins = int(self.count / MEAN_VALUES_IN_BIN)
                if n_bins < MIN_BINS:
                    n_bins = MIN_BINS
                if n_bins > MAX_BINS:
                    n_bins = MAX_BINS
                if n_bins > num_values:
                    n_bins = num_values

        #now we can calculate the bin edges
        distrib_span = max_ - min_ if max_ != min_ else 1

        if distrib_span % n_bins:
            distrib_span = distrib_span + n_bins - (distrib_span % n_bins)
        bin_span = distrib_span // n_bins
        bin_edges = [min_ + bin_ * bin_span for bin_ in range(n_bins + 1)]
        return bin_edges

    def calculate_distribution(self, bins=None, min_=None, max_=None,
                               remove_outliers=None):
        'It returns an histogram with the given range and bin'
        distrib = []
        min_, max_ = self._calculate_dist_range(min_, max_, remove_outliers)
        if min_ is None or max_ is None:
            return None
        bin_edges = self.calculate_bin_edges(min_, max_, bins)
        for bin_index, left_edge in enumerate(bin_edges):
            try:
                rigth_edge = bin_edges[bin_index + 1]
            except IndexError:
                break
            sum_values = 0
            for index2, value in enumerate(self._array):
                if index2 > rigth_edge:
                    break

                elif (left_edge <= index2  and index2 < rigth_edge or
                     left_edge <= index2 and index2 == max_):
                    sum_values += value

            distrib.append(sum_values)
        return {'distrib': distrib, 'bin_edges': bin_edges}

    def _prepare_labels(self, labels=None):
        'It prepares the labels for output files'
        default_labels = {'title': 'histogram', 'xlabel': 'values',
                          'ylabel': 'count', 'minimum': 'minimum',
                          'maximum': 'maximum', 'average': 'average',
                          'variance': 'variance', 'sum': 'sum',
                          'items': 'items', 'quartiles': 'quartiles'}
        if labels is None:
            labels = default_labels
        else:
            for label, value in default_labels.items():
                if label not in labels:
                    labels[label] = value
        return labels

    def __str__(self):
        'It writes some basic stats of the values'
        if self.count != 0:
            labels = self._prepare_labels()
            #now we write some basic stats
            format_num = lambda x: str(x) if isinstance(x, int) else '%.4f' % x
            text = '%s: %s\n' % (labels['minimum'], format_num(self.min))
            text += '%s: %s\n' % (labels['maximum'], format_num(self.max))
            text += '%s: %s\n' % (labels['average'], format_num(self.average))
            text += '%s: %s\n' % (labels['variance'],
                                  format_num(self.variance))
            text += '%s: %s\n' % (labels['sum'], format_num(self.sum))
            text += '%s: %s\n' % (labels['items'], self.count)
            return text
        return ''
