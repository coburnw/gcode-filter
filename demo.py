import filters as filters
import segment as segment

class Parameters():
    def __init__(self):
        self.action = ''
        self.feedRateMode = ''
        self.lengthUnits = ''

        self.params = dict()
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
        if key == 'length_units':
            return self.lengthUnits
        elif key == 'feed_rate_mode':
            return self.feedRateMode
        elif key == 'action':
            return self.action
        elif key == 'segment_length':
            return self.segment.length()
        elif key == 'segment_duration':
            return self.segment.duration()
        
        return self.params[key]

    def update(self, param_dict):
        self.params = param_dict
        self.segment.update(self.params)
        return

class FileCommand():
    def __init__(self):
        self.action = ''
        self.line_params = Parameters()
        self.line_params.lengthUnits = 'G23' #mm
        self.line_params.feedRateMode = 'G94' #mm/min
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

        param_dict = dict()
        for param in params:
            key = param[:1]
            value = param[1:]
            if key == 'F':
                value = float(value) * 60
            param_dict[key] = value

        self.line_params.update(param_dict)
        return
    
    def AppendActionFilter(self, action_filter, **kwargs):
        raise NotImplemented
    
    def AppendParameterFilter(self, new_param_filter, **kwargs):
        self.parameters = new_param_filter(self.parameters, **kwargs)
        
class FileSource(): #filters.Source?
    def __init__(self, f):
        self.f = f
        self.command = FileCommand()
        
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
        
        lines.command.AppendParameterFilter(filters.TranslateFilter, src='yzb', dst='zxc')
        lines.command.AppendParameterFilter(filters.UnitsFilter, to='in')
        lines.command.AppendParameterFilter(filters.FeedRateFilter, feed_rate_mode='G93')
        lines.command.AppendParameterFilter(filters.StringFilter, precision=4)
        lines.command.AppendParameterFilter(filters.IterFilter, order=param_order)

        for block in lines:
            print(block)

        #print('{}:{}'.format(line.action, line.parameters['X']))
