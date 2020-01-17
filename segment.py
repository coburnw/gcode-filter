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

import math

class Point:
    def __init__(self, coords=None):
        self.axes = ['F', 'X', 'Y', 'Z', 'A', 'B', 'C']
        if coords is None:
            coords = dict()
        self.coords = coords
        return
    
    def __repr__(self):
        return "{}".format(self.coords)

    def update(self, coords):
        for axis in self.axes:
            if axis in coords:
                self.coords[axis] = float(coords[axis])
            
        return
    
class Segment:
    def __init__(self, p0=None ,p1=None):
        self.p0 = p0
        self.p1 = p1
        
        if self.p0 is None:
            self.p0 = Point()

        if self.p1 is None:
            self.p1 = Point()    

    def __repr__(self):
        return "{} {}".format(self.p0, self.p1)
    
    def update(self, coords):
        self.p0.update(self.p1.coords)
        self.p1.update(coords)

    def delta(self, axis_name):
        return self.p1.coords[axis_name] - self.p0.coords[axis_name]
        
    def cart_length(self, axis_name):
        if axis_name not in ['X', 'Y', 'Z']:
            return None
        if axis_name not in self.p1.coords or axis_name not in self.p0.coords:
            return 0

        length = self.p1.coords[axis_name] - self.p0.coords[axis_name]
        return length
    
    def arc_length(self, axis_name):
        # here we asume the axis rotates around axis_name with Z being the radius
        if axis_name not  in ['A', 'B', 'C']:
            return None
        if axis_name not in self.p1.coords or axis_name not in self.p0.coords:
            return 0    

        theta = self.p1.coords[axis_name] - self.p0.coords[axis_name]
        length = 2 * math.pi * self.p1.coords['Z'] * theta/360
        
        return length
    
    def length(self, axis_name='R'):
        # and here the B axis is the rotary, Z is radius, and Y the length
        if axis_name in ['X', 'Y', 'Z']:
            result = self.cart_length(axis_name)
        elif axis_name in ['A', 'B', 'C']:
            result = self.arc_length(axis_name)
        elif axis_name == 'R': #resultant
            # this is a pretty simplistic view of the problem...
            da = self.arc_length('B')
            dc = math.sqrt(self.cart_length('X')**2 + self.cart_length('Y')**2 + self.cart_length('Z')**2)
            r_len = math.sqrt((da)**2 + (dc)**2)
            result = r_len
            
        return result
    
    def velocity(self):
        if 'F' in self.p1.coords:
            velocity = self.p1.coords['F']
        elif 'F' in self.p0.coords:
            velocity = self.p0.coords['F']
        else:
            velocity = 0.0

        return velocity
    
    def duration(self):
        if self.velocity() == 0:
            return 0
        
        return self.length() / self.velocity()


