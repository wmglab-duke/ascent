#!/usr/bin/env python3.7

"""
The copyrights of this software are owned by Duke University.
Please refer to the LICENSE and README.md files for licensing instructions.
The source code can be found on the following GitHub repository: https://github.com/wmglab-duke/ascent
"""
from PIL import Image, ImageDraw, ImageFont
# builtins
import itertools
import os
from typing import List, Union, Tuple
import random

# packages
from shapely.geometry import LineString, Point
from shapely.affinity import scale
import numpy as np
import matplotlib.pyplot as plt

# ascent
from .fascicle import Fascicle
from .nerve import Nerve
from .trace import Trace
from src.utils import Exceptionable, NerveMode, SetupMode, ReshapeNerveMode, WriteMode


class Slide(Exceptionable):

    def __init__(self, fascicles: List[Fascicle], nerve: Nerve, nerve_mode: NerveMode, exception_config: list,
                 will_reposition: bool = False):
        """
        :param fascicles: List of fascicles
        :param nerve: Nerve (effectively is a Trace)
        :param nerve_mode: from Enums, indicates if the nerve exists or not (PRESENT, NOT_PRESENT)
        :param exception_config: pre-loaded configuration data
        :param will_reposition: boolean flag that tells the initializer whether or not it should be validating the
        geometries - if it will be reposition then this is not a concern
        """

        # init superclasses
        Exceptionable.__init__(self, SetupMode.OLD, exception_config)

        self.nerve_mode = nerve_mode

        self.nerve: Nerve = nerve
        self.fascicles: List[Fascicle] = fascicles

        if not will_reposition:
            self.validation()
        else:
            if self.nerve_mode == NerveMode.NOT_PRESENT:
                self.throw(39)

        self.orientation_point: Union[Tuple[float, float], None] = None
        self.orientation_angle: Union[float, None] = None

    def monofasc(self) -> bool:
        return self.nerve_mode == NerveMode.NOT_PRESENT and len(self.fascicles) == 1

    def fascicle_centroid(self) -> Tuple[float, float]:
        area_sum = x_sum = y_sum = 0.0

        for fascicle in self.fascicles:
            x, y = fascicle.centroid()
            area = fascicle.area()

            x_sum += x * area
            y_sum += y * area
            area_sum += area

        return (x_sum / area_sum), (y_sum / area_sum)
    def validation(self, specific: bool = True, die: bool = True, tolerance: float = None, plotpath='') -> bool:
        """
        Checks to make sure nerve geometry is not overlapping itself
        :param specific: if you want to know what made it fail first
        :param die: if non-specific, decides whether or not to throw an error if it fails
        :param tolerance: minimum separation distance for unit you are currently in
        :return: Boolean for True (no intersection) or False (issues with geometry overlap)
        """

        def debug_plot():
            plt.figure()
            self.plot(final=False, fix_aspect_ratio='True', axlabel=u"\u03bcm",
                       title='Debug sample which failed validation.')
            plt.savefig(plotpath + '/sample_final')
            plt.clf()
            plt.close()

        if self.monofasc():
            return True

        if specific:
            if self.fascicle_fascicle_intersection():
                debug_plot()
                self.throw(10)

            if self.fascicle_nerve_intersection():
                debug_plot()
                self.throw(11)

            if self.fascicles_outside_nerve():
                debug_plot()
                self.throw(12)

        else:
            if any([self.fascicle_fascicle_intersection(), self.fascicle_nerve_intersection(),
                    self.fascicles_outside_nerve(), self.fascicles_too_close(tolerance)]):
                if die:
                    debug_plot()
                    self.throw(13)
                else:
                    return False
            else:
                return True

    def fascicles_too_close(self, tolerance: float = None) -> bool:
        """
        :param tolerance: Minimum separation distance
        :return: Boolean for True for fascicles too close as defined by tolerance
        """

        if self.monofasc():
            self.throw(41)

        if tolerance is None:
            return False
        else:
            pairs = itertools.combinations(self.fascicles, 2)
            return any([first.min_distance(second) < tolerance for first, second in pairs]) or \
                   any([fascicle.min_distance(self.nerve) < tolerance for fascicle in self.fascicles])

    def fascicle_fascicle_intersection(self) -> bool:
        """
        :return: True if any fascicle intersects another fascicle, otherwise False
        """

        if self.monofasc():
            self.throw(42)

        pairs = itertools.combinations(self.fascicles, 2)
        return any([first.intersects(second) for first, second in pairs])

    def fascicle_nerve_intersection(self) -> bool:
        """
        :return: True if any fascicle intersects the nerve, otherwise False
        """

        if self.monofasc():
            self.throw(43)

        return any([fascicle.intersects(self.nerve) for fascicle in self.fascicles])

    def fascicles_outside_nerve(self) -> bool:
        """
        :return: True if any fascicle lies outside the nerve, otherwise False
        """

        if self.monofasc():
            self.throw(44)

        return any([not fascicle.within_nerve(self.nerve) for fascicle in self.fascicles])

    def move_center(self, point: np.ndarray):
        """
        :param point: the point of the new slide center
        """

        if self.monofasc():
            # get shift from nerve centroid and point argument
            shift = list(point - np.array(self.fascicles[0].centroid())) + [0]
        else:
            # get shift from nerve centroid and point argument
            shift = list(point - np.array(self.nerve.centroid())) + [0]

            # apply shift to nerve trace and all fascicles
            self.nerve.shift(shift)

        for fascicle in self.fascicles:
            fascicle.shift(shift)

    def reshaped_nerve(self, mode: ReshapeNerveMode, buffer: float = 0.0) -> Nerve:
        """
        :param buffer:
        :param mode: Final form of reshaped nerve, either circle or ellipse
        :return: a copy of the nerve with reshaped nerve boundary, preserves point count which is SUPER critical for
        fascicle repositioning
        """

        if self.monofasc():
            self.throw(45)

        if mode == ReshapeNerveMode.CIRCLE:
            return self.nerve.to_circle(buffer)
        elif mode == ReshapeNerveMode.ELLIPSE:
            return self.nerve.to_ellipse()
        elif mode == ReshapeNerveMode.NONE:
            return self.nerve
        else:
            self.throw(16)

    def plot(self,
             title: str = None,
             final: bool = True,
             inner_format: str = 'b-',
             fix_aspect_ratio: bool = True,
             fascicle_colors: List[Tuple[float, float, float, float]] = None,
             ax: plt.Axes = None,
             outers_flag: bool = True,
             inner_index_labels: bool = False,
             show_axis: bool = True,
             axlabel: str = None):
        """
        Quick util for plotting the nerve and fascicles
        :param show_axis:
        :param inner_index_labels:
        :param outers_flag:
        :param fascicle_colors:
        :param ax:
        :param title: optional string title for plot
        :param final: optional, if False, will not show or add title (if comparisons are being overlayed)
        :param inner_format: optional format for inner traces of fascicles
        :param fix_aspect_ratio: optional, if True, will set equal aspect ratio
        """

        if ax is None:
            ax = plt.gca()

        if not show_axis:
            ax.axis('off')

        # if not the last graph plotted
        if fix_aspect_ratio:
            ax.set_aspect('equal', 'datalim')

        # loop through constituents and plot each
        if not self.monofasc():
            self.nerve.plot(plot_format='k-', ax=ax,linewidth=1.5)

        if fascicle_colors is not None:
            if not len(self.fascicles) == len(fascicle_colors):
                self.throw(65)
        else:
            fascicle_colors = [None] * len(self.fascicles)

        inner_index = 0
        for fascicle, color in zip(self.fascicles, fascicle_colors):
            fascicle.plot(
                inner_format,
                color,
                ax=ax,
                outer_flag=outers_flag,
                inner_index_start=inner_index if inner_index_labels else None
            )
            inner_index += len(fascicle.inners)

        if title is not None:
            ax.title.set_text(title)
            
        if axlabel is not None:
            ax.set_xlabel(axlabel)
            ax.set_ylabel(axlabel)

        # if final plot, show
        if final:
            plt.show()

    def scale(self, factor: float):
        """
        :param factor: scale factor, only knows how to scale around its own centroid
        """

        if self.monofasc():
            center = list(self.fascicles[0].centroid())
        else:
            center = list(self.nerve.centroid())
            self.nerve.scale(factor, center)

        for fascicle in self.fascicles:
            fascicle.scale(factor, center)
            
    def smooth_traces(self, n_distance, i_distance):
        """
        Smooth traces for the slide
        :param n_distance: distance to inflate and deflate the nerve trace
        :param i_distance: distance to inflate and deflate the fascicle traces        """
        
        if i_distance is None: self.throw(113)
        for trace in self.trace_list():
            if isinstance(trace,Nerve):
                trace.smooth(n_distance)
            else:
                trace.smooth(i_distance)

    def generate_perineurium(self,fit: dict):
        for fascicle in self.fascicles:
            fascicle.perineurium_setup(fit=fit)
        
    def rotate(self, angle: float):
        """
        :param angle: angle in radians, only knows how to rotate around its own centroid
        """

        if self.monofasc():
            center = list(self.fascicles[0].centroid())
        else:
            center = list(self.nerve.centroid())
            self.nerve.rotate(angle, center)

        for fascicle in self.fascicles:
            fascicle.rotate(angle, center)

        self.validation()

    def bounds(self):
        """
        :return: check bounds of all traces and return outermost bounds
        """
        allbound = np.array([trace.bounds() for trace in self.trace_list() if trace is not None])
        return (min(allbound[:,0]),min(allbound[:,1]),max(allbound[:,2]),max(allbound[:,3]))
    
    def trace_list(self):
        """
        :return: list of all traces in the slide
        """
        if self.monofasc():
            trace_list = [f.outer for f in self.fascicles]
        else:
            trace_list = [self.nerve] + [f.outer for f in self.fascicles]
        return trace_list
    
    def write(self, mode: WriteMode, path: str):
        """
        :param mode: Sectionwise for now... could be other types in the future (STL, DXF)
        :param path: root path of slide
        """

        start = os.getcwd()

        if not os.path.exists(path):
            self.throw(26)
        else:
            # go to directory to write to
            os.chdir(path)

            # keep track of starting place
            sub_start = os.getcwd()

            # write nerve (if not monofasc) and fascicles
            if self.monofasc():
                trace_list = [(self.fascicles, 'fascicles')]
            else:
                trace_list = [([self.nerve], 'nerve'), (self.fascicles, 'fascicles')]

            for items, folder in trace_list:
                # build path if not already existing
                if not os.path.exists(folder):
                    os.makedirs(folder)
                os.chdir(folder)

                # write all items (give filename as i (index) without the extension
                for i, item in enumerate(items):
                    if isinstance(item, Trace):  # not Nerve bc it is buffer class!
                        if not os.path.exists(str(i)):
                            os.mkdir(str(i))
                        item.write(mode, os.path.join(os.getcwd(), str(i), str(i)))
                    else:
                        # start to keep track of position file structure
                        index_start_folder = os.getcwd()

                        # go to indexed folder for each fascicle
                        index_folder = str(i)
                        if not os.path.exists(index_folder):
                            os.makedirs(index_folder)
                        os.chdir(index_folder)
                        item.write(mode, os.getcwd())

                        # go back up a folder
                        os.chdir(index_start_folder)

                # change directory back to starting place
                os.chdir(sub_start)

        os.chdir(start)
    
    def saveimg(self, path: str,dims,separate:bool = False,colors = {'n':'red','i':'green','p':'blue'}, buffer = 0,nerve = True, outers = True,inners = True,outer_minus_inner = False,ids = []):
        #comments coming soon to a method near you
        def prep_points(points):
            #adjusts plot points to dimensions and formats for PIL
            points = (points-dim_min+buffer)[:,0:2].astype(int)
            points = tuple(zip(points[:,0],points[:,1]))
            return points
        fnt = ImageFont.truetype("arial.ttf", 60)       
        dim_min = [min(x) for x in dims]
        dim = [max(x) for x in dims]
        imdim = [dim[0]+abs(dim_min[0])+buffer*2,dim[1]+abs(dim_min[1])+buffer*2]
        self.move_center
        if not separate: #draw contours and ids if provided
            img = Image.new('RGB',imdim)
            draw = ImageDraw.Draw(img)
            if nerve: 
                draw.polygon(prep_points(self.nerve.points[:,0:2]), fill = colors['n'])
            for fascicle in self.fascicles:
                if outers: 
                    draw.polygon(prep_points(fascicle.outer.points[:,0:2]),fill = colors['p'])
            for fascicle in self.fascicles:
                for inner in fascicle.inners:
                    draw.polygon(prep_points(inner.points[:,0:2]),fill = colors['i'])
            img = img.transpose(Image.FLIP_TOP_BOTTOM)
            iddraw = ImageDraw.Draw(img)
            if len(ids)>0: #prints the fascicle ids
                for i,row in ids.iterrows():
                    location = (row['x']-dim_min[0]+buffer,img.height-row['y']+dim_min[1]-buffer)
                    iddraw.text(location,str(int(row['id'])),font = fnt,fill='white')
            img.save(path)
        elif separate: #generate each image and save seperately
            if nerve:
                img = Image.new('1',imdim)
                draw = ImageDraw.Draw(img)
                draw.polygon(prep_points(self.nerve.points[:,0:2]), fill = 1)
                img = img.transpose(Image.FLIP_TOP_BOTTOM)
                img.save(path['n'])
            if outers:
                imgp = Image.new('1',imdim)
                draw = ImageDraw.Draw(imgp)
                for fascicle in self.fascicles:
                    draw.polygon(prep_points(fascicle.outer.points[:,0:2]),fill = 1)
                    if outer_minus_inner:
                        for fascicle in self.fascicles:
                            for inner in fascicle.inners:
                                draw.polygon(prep_points(inner.points[:,0:2]),fill = 0)    
                imgp = imgp.transpose(Image.FLIP_TOP_BOTTOM)
                imgp.save(path['p'])
            if inners:
                imgi = Image.new('1',imdim)
                draw = ImageDraw.Draw(imgi)
                for fascicle in self.fascicles:
                    for inner in fascicle.inners:
                        draw.polygon(prep_points(inner.points[:,0:2]),fill = 1)
                imgi = imgi.transpose(Image.FLIP_TOP_BOTTOM)  
                iddraw = ImageDraw.Draw(imgi)
                if len(ids)>0: #prints the fascicle ids
                    for i,row in ids.iterrows():
                        location = (row['x']-dim_min[0]+buffer,img.height-row['y']+dim_min[1]-buffer)
                        iddraw.text(location,str(int(row['id'])),font = fnt,fill=0)
                imgi.save(path['i'])
                
    # %% DISCLAIMER: this is depreciated and not well documented
    def reposition_fascicles(self, new_nerve: Nerve, minimum_distance: float = 10, seed: int = None):
        """
        :param new_nerve: Nerve conte
        :param minimum_distance:
        :param seed:
        :return:
        """

        self.plot(final=False, fix_aspect_ratio=True)

        # seed the random number generator
        if seed is not None:
            random.seed(seed)

        def random_permutation(iterable, r: int = None):
            """
            :param iterable:
            :param r: size for permutations (defaults to number of elements in iterable)
            :return: a random permutation of the elements in iterable
            """

            pool = tuple(iterable)
            r = len(pool) if r is None else r
            return tuple(random.sample(pool, r))

        def jitter(first: Fascicle, second: Union[Fascicle, Nerve], rotation: bool = False):
            """
            :param rotation: whether or not to randomly rotate
            :param first:
            :param second:
            :return:
            """

            # create list of fascicles to jitter, defaulting to just the first fascicle
            fascicles_to_jitter = [first]

            # is second argument is a Fascicles, append it to list of fascicles to jitter
            # also, use second argument's type to decide how to find angle between arguments
            if isinstance(second, Fascicle):
                fascicles_to_jitter.append(second)
                angle = first.angle_to(second)
            else:
                _, points = first.min_distance(second, return_points=True)
                angle = Trace.angle(*[point.coords[0] for point in points])

            # will be inverted on each iteration to move in opposite directions
            factor = -1
            for f in fascicles_to_jitter:
                step_scale = 1

                # if the second elements is a Fascicle, and this fascicle is within the other, grow step size
                # this helps fascicles that were moved into others move out quickly
                if isinstance(second, Fascicle) and [f.outer.within(h.outer) for h in (first, second) if h is not f][0]:
                    step_scale *= -20

                # find random step magnitude and build a step vector from that
                step_magnitude = random.random() * minimum_distance
                step = list(np.array([np.cos(angle), np.sin(angle)]) * step_magnitude)

                # apply rigid transformations
                f.shift([step_scale * factor * item for item in step] + [0])
                if rotation:
                    f.rotate(factor * ((random.random() * 2) - 1) * (2 * np.pi) / 100)

                # if just moved out of nerve, move back in
                if not f.within_nerve(new_nerve):
                    f.shift([step_scale * -factor * item for item in step] + [0])

                # invert factor for next fascicle
                factor *= -1

        # Initial shift - proportional to amount of change in the nerve boundary and distance of
        # fascicle centroid from nerve centroid

        for i, fascicle in enumerate(self.fascicles):
            # print('fascicle {}'.format(i))

            fascicle_centroid = fascicle.centroid()
            new_nerve_centroid = new_nerve.centroid()
            r_fascicle_initial = LineString([new_nerve_centroid, fascicle_centroid])

            r_mean = new_nerve.mean_radius()
            r_fasc = r_fascicle_initial.length
            a = 3
            exterior_scale_factor = a * (r_mean / r_fasc)
            exterior_line: LineString = scale(r_fascicle_initial,
                                              *([exterior_scale_factor] * 3),
                                              origin=new_nerve_centroid)

            # plt.plot(*new_nerve_centroid, 'go')
            # plt.plot(*fascicle_centroid, 'r+')
            # new_nerve.plot()
            # plt.plot(*np.array(exterior_line.coords).T)
            # plt.show()

            new_intersection = exterior_line.intersection(new_nerve.polygon().boundary)
            old_intersection = exterior_line.intersection(self.nerve.polygon().boundary)
            # nerve_change_vector = LineString([new_intersection.coords[0], old_intersection.coords[0]])

            # plt.plot(*np.array(nerve_change_vector.coords).T)
            # self.nerve.plot()
            # new_nerve.plot()

            # get radial vector to new nerve trace
            r_new_nerve = LineString([new_nerve_centroid, new_intersection.coords[0]])

            # get radial vector to FIRST coordinate intersection of old nerve trace
            if isinstance(old_intersection, Point):  # simple Point geometry
                r_old_nerve = LineString([new_nerve_centroid, old_intersection.coords[0]])
            else:  # more complex geometry (MULTIPOINT)
                r_old_nerve = LineString([new_nerve_centroid, list(old_intersection)[0].coords[0]])

            fascicle_scale_factor = (r_new_nerve.length / r_old_nerve.length) * 0.8

            r_fascicle_final = scale(r_fascicle_initial,
                                     *([fascicle_scale_factor] * 3),
                                     origin=new_nerve_centroid)

            shift = list(np.array(r_fascicle_final.coords[1]) - np.array(r_fascicle_initial.coords[1])) + [0]
            fascicle.shift(shift)
            # fascicle.plot('r-')

            # attempt to move in direction of closest boundary
            _, min_dist_intersection_initial = fascicle.centroid_distance(self.nerve, return_points=True)
            _, min_dist_intersection_final = fascicle.centroid_distance(new_nerve, return_points=True)
            min_distance_length = LineString([min_dist_intersection_final[1].coords[0],
                                              min_dist_intersection_initial[1].coords[0]]).length
            min_distance_vector = np.array(min_dist_intersection_final[1].coords[0]) - \
                                  np.array(min_dist_intersection_initial[1].coords[0])
            min_distance_vector *= 1

            # fascicle.shift(list(-min_distance_vector) + [0])

        # NOW, set the slide's actual nerve to be the new nerve
        self.nerve = new_nerve

        # Jitter
        iteration = 0
        print('start random jitter')
        while not self.validation(specific=False, die=False, tolerance=None):

            # USER OUTPUT
            iteration += 1
            plt.figure()
            self.plot(final=True, fix_aspect_ratio=True, inner_format='r-')
            plt.title('iteration: {}'.format(iteration - 1))
            plt.show()
            print('\titeration: {}'.format(iteration))

            # loop through random permutation
            for fascicle in random_permutation(self.fascicles):
                while fascicle.min_distance(self.nerve) < minimum_distance:
                    jitter(fascicle, self.nerve)

                for other_fascicle in random_permutation(filter(lambda item: item is not fascicle, self.fascicles)):
                    while any([fascicle.min_distance(other_fascicle) < minimum_distance,
                               fascicle.outer.within(other_fascicle.outer)]):
                        jitter(fascicle, other_fascicle)

        print('end random jitter')

        # validate again just for kicks
        self.validation()

        self.plot('CHANGE', inner_format='r-')
