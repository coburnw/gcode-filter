import filters as filters
import segment as segment

class Parameters():
    def __init__(self):
        self.action = ''
        self.params = dict()
        self.p_iter = None
        self.p_items = []
        
        firstmove = {"X": -1, "Y": -1, "Z": -1, "F": 0.0}
        self.segment = segment.Segment()
        self.segment.update(firstmove)

    def __iter__(self):
        self.p_items = iter(self.params.items())
        return self

    def __next__(self):
        item = next(self.p_items)
        return item
            
    def __contains__(self, key):
        return key in self.params

    def __getitem__(self, key):
        if key == 'action':
            return self.action
        elif key == 'segment_length':
            return self.segment.length()
        elif key == 'segment_duration':
            return self.segment.duration()
        
        return self.params[key]

    def update(self, params):
        self.params.clear()
        for param in params:
            key = param[:1]
            value = param[1:]
            self.params[key] = value
        self.segment.update(self.params)
        return

class Command():
    def __init__(self):
        self.action = ''
        self.line_params = Parameters()
        self.parameters = self.line_params

    def __repr__(self):
        str = self.action
        for param, value in self.parameters:
            str = "{} {}{}".format(str, param, value)
        return str
        
    def update(self, line):
        params = line.split()
        self.action = params.pop(0)
        self.line_params.action = self.action
        self.line_params.update(params)
        return
    
    def AppendActionFilter(self, action_filter, **kwargs):
        raise NotImplemented
    
    def AppendParameterFilter(self, new_param_filter, **kwargs):
        self.parameters = new_param_filter(self.parameters, **kwargs)
        
class FileSource(): #filters.Source?
    def __init__(self, f):
        self.f = f
        self.command = Command()
        
    def __iter__(self):
        return self

    def __next__(self):
        line = next(self.f)
        self.command.update(line)
        return self.command


if __name__ == '__main__':
    param_order = ['X', 'Z', 'C', 'F']

    with open('demo.ngc') as f:
        feed_rate_mode = 'G93'
        
        lines = FileSource(f)
        #lines = FeedRateFilter(lines, feed_rate_mode)
        lines.command.AppendParameterFilter(filters.TranslateFilter, src='yzb', dst='zxc')
        lines.command.AppendParameterFilter(filters.UnitsFilter, to='in')
        lines.command.AppendParameterFilter(filters.FeedRateFilter, feed_rate_mode='G93')
        lines.command.AppendParameterFilter(filters.StringFilter, precision=4)
        lines.command.AppendParameterFilter(filters.IterFilter, order=param_order)

        for block in lines:
            print(block)

        #print('{}:{}'.format(line.action, line.parameters['X']))
