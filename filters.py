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
        if mode in ['G93', 'G94']:
            self.fmode = mode
        elif mode == 'G95':
            raise NotImplementedError
        else:
            raise NameError
        return
    
    def get_feed_rate(self, value):
        if self.inner['feed_rate_mode'] == self.fmode:
            f_value = value
        elif (self.fmode == 'G93') and (self.inner['action'] in ['G1', 'G2', 'G3']):
            duration = self.inner['segment_duration']
            if duration < 0.00016667:
                duration = 0.00016667
            f_value = 1 / duration
        else:
            f_value = value

        return f_value

    
class TranslateFilter(Filter):
    def _init(self, **kwargs):
        self.translate = dict()

        try:
            src_str = kwargs['src']
            dst_str = kwargs['dst']
        except:
            src_str = None
            dst_str = None
        finally:
            if src_str and dst_str:
                for i, dst in enumerate(dst_str):
                    src = src_str[i]
                    self.translate[dst.upper()] = src.upper()
        return

    def _key_filter(self, key):
        if key in self.translate:
            key = self.translate[key]
        return key

    
class UnitsFilter(Filter):
    def _init(self, **kwargs):
        if 'to' not in kwargs:
            self.distance_factor = 1.0
        elif kwargs['to'] == 'mm':
            self.distance_factor = 25.4
        elif kwargs['to'] == 'in':
            self.distance_factor = 1/25.4
        return
    
    def _value_filter(self, key, value):
        if key in ['X', 'Y', 'Z']:
            value = float(value) * self.distance_factor
        elif key in ['A', 'B', 'C']:
            value = float(value)
        elif key in ['F']:
            if self.inner['feed_rate_mode'] == 'G94':
                value = float(value) * self.distance_factor        
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
        for key in self.key_order:
            if key in self.inner:
                return key, self.inner[key]
        raise StopIteration

class StringFilter(Filter):
    def _init(self, **kwargs):
        self.precision_string = '.' + str(kwargs['precision']) + 'f'

    def _value_filter(self, key, value):
        if key in ['X', 'Y', 'Z']:
            value = format(float(value), self.precision_string)
        elif key in ['A', 'B', 'C']:
            value = format(float(value), self.precision_string)
        elif key in ['F']:
            value = format(float(value), self.precision_string)
        elif key in ['T', 'H', 'D', 'S']:
            value = str(int(value))
        else:
            pass
        return value

    
