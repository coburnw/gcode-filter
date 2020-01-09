# ***************************************************************************
# *   (c) Coburn Wightman 2019                                              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This software is distributed in the hope that it will be useful,      *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Lesser General Public License for more details.                   *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with FreeCAD; if not, write to the Free Software        *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************/

class Filter(object):
    def __init__(self, inner, **kwargs):
        self.inner = inner
        self._init(**kwargs)

    ## itering the objects themselves skips the key filter.  not good.
    ## use the IterFilter
    ##
    # def __iter__(self):
    #     self.i_inner = iter(self.inner)
    #     return self

    # def __next__(self):
    #     key, value = next(self.i_inner)
    #     return key, self._value_filter(key, value)

    def __contains__(self, key):
        key = self._key_filter(key)
        return key in self.inner

    def __getitem__(self, key):
        key = self._key_filter(key)
        value = self.inner[key]
        return self._value_filter(key, value)
        
    def _init(self, **kwargs):
        self.kwargs = kwargs
        return
    
    def _key_filter(self, key):
        return key
    
    def _value_filter(self, key, value):
        return value
    

class FeedRateFilter(Filter):
    def _init(self, **kwargs):
        self.feed_rate_mode(kwargs['feed_rate_mode'])
        
    def _value_filter(self, key, value):
        if key == 'F':
            value = self.get_feed_rate(value)
        return value
    
    def feed_rate_mode(self, mode):
        if mode in ['G93', 'G94', 'G95']:
            self.fmode = mode
        else:
            raise NameError

    def get_feed_rate(self, value):
        if self.fmode == 'G95':
            raise NotImplementedError
        elif self.fmode == 'G93' and self.inner['action'] in ['G1', 'G2', 'G3']:
            duration = self.inner['segment_duration']
            if duration == 0:
                duration = 1.0
            f_value = 1 / duration
        else: #assume g94
            f_value =  value

        return f_value

    
class TranslateFilter(Filter):
    def _key_filter(self, key):
        matrix = dict()
        if 'src' in self.kwargs and 'dst' in self.kwargs:
            i = 0
            dst_str = self.kwargs['dst']
            src_str = iter(self.kwargs['src'])
            for dst in dst_str:
                src = next(src_str)
                matrix[dst.upper()] = src.upper()

        if key in matrix:
            key = matrix[key]
        return key

    
class UnitsFilter(Filter):
    def _value_filter(self, key, value):
        if 'to' not in self.kwargs:
            distance_factor = 1
        elif self.kwargs['to'] == 'mm':
            distance_factor = 24.4
        elif self.kwargs['to'] == 'in':
            distance_factor = 1/24.5
            
        if key in ['X', 'Y', 'Z']:
            value = float(value) * distance_factor
        elif key in ['A', 'B', 'C']:
            value = float(value)
        elif key in ['F']:
            value = float(value)
        
        return value

        
class IterFilter(Filter):
    def _init(self, **kwargs):
        self.param_order = kwargs['order']
        self.key_order = None
        return
    
    def __iter__(self):
        self.key_order = iter(self.param_order)
        return self

    def __next__(self):
        while True:
            key = next(self.key_order)
            if key in self.inner:
                return key, self.inner[key]


class StringFilter(Filter):
    def _value_filter(self, key, value):
        precision_string = '.' + str(self.kwargs['precision']) + 'f'
        if key in ['X', 'Y', 'Z']:
            string = format(float(value), precision_string)
        elif key in ['A', 'B', 'C']:
            string = format(float(value), precision_string)
        elif key in ['F']:
            string = format(float(value), precision_string)
        elif key in ['T', 'H', 'D', 'S']:
            string = str(int(value))
        else:
            string = value
        return string

    
