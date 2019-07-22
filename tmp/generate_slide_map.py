#!/usr/bin/env python3.7

# Author: Jake Cariello
# Date: June 18, 2019
# General Purpose:
#       Parse through directory of UW-Madison Pig slides and find all slide numbers.
#       With these numbers, find positions of all slides wrt start of first cassette.
#       Then, format and print out results. Should be useful for finding slides in 3D
#       space (and selecting the correct slide).
#
# Modified and expanded: June 26, 2019

import csv  # for writing data to file
import datetime  # for output file naming
import os  # for basic filesystem navigation
import re  # regular expression tools (for recognizing slide number)

import numpy  # convenience
import xlwt  # for saving to xls


# %% quick class to keep track of slides
class Slide:
    def __init__(self, cassette, number, position):
        self.cassette = cassette
        self.number = number
        self.position = position

    @staticmethod
    def get(from_list, cassette, number):
        return list(filter(lambda s: (s.cassette == cassette) and (s.number == number), from_list))[0]


# %% quick class to keep track of electrodes
class Electrode:
    """
    start: Slide whose position is start of mark (blue dye)
    end: Slide whose position is end of mark (blue dye)
    """

    def __init__(self, start: Slide, end: Slide):
        self.start: Slide = start
        self.end: Slide = end

    def position(self):
        return numpy.mean([self.start.position,
                           self.end.position])

    def abs_dist_to(self, other_electrode: 'Electrode'):  # use string to delay type eval
        return abs(self.position() - other_electrode.position())


# %% setup

printing_output = False

slides = []

# directory with slides
slides_dir = '/Users/jakecariello/Box/19P866_05292019/'

# directory with slide maps
maps_dir = '/Users/jakecariello/Box/SPARC/tmp_UWM_Scripts/helpers/slide_maps/'
if not os.path.isdir(maps_dir):
    os.makedirs(maps_dir)

# known cassettes for now (IN ORDER)
cassettes = ['VN1_A', 'VN1_B']

# allowed differences to NOT skip 100 um
allowed_diffs = [1, 2]

# recognizes '#.', '##.', '###.', etc.
number_regex = re.compile('([0-9]*)[.]')

# use this number as the start position for each cassette
cassette_start_pos = 20000 # i.e. 20mm

# store running total of position
position = cassette_start_pos

# allowed livanova center-to-center distance [um]
allowed_e_dist = 6000

# skipping specifics [um]
normal_skip = -5
large_skip = -120
cassette_skip = -100

#some output
if printing_output:
    print('Parameters:\n'
          '\tslice skip\t{:6} um\n'
          '\tgrouping skip\t{:6} um\n'
          '\tcassette skip\t{:6} um\n'.format(normal_skip, large_skip, cassette_skip))



# function to init livanova electrodes
def livanova_setup():
    return [Electrode(Slide.get(slides, 'VN1_A', 145), Slide.get(slides, 'VN1_A', 175)),
            Electrode(Slide.get(slides, 'VN1_B',  66), Slide.get(slides, 'VN1_B', 117))]

# get files (assumes first iteration of os.walk)
# files are always the 3rd item in a tuple returned by each iteration of os.walk
files = [result for result in os.walk(slides_dir)][0][2]

# %% master loop for finding positions
for k, cassette_code in enumerate(cassettes):
    cassette = []
    # find all files from this cassette
    filtered_files = list(filter(lambda f: re.search(cassette_code, f), files))
    for i, file in enumerate(filtered_files):
        # we know that there MUST be a match now because it matched to the cassette name
        match = number_regex.search(file).group(0)
        # get the number from that match
        number = int(match[:len(match) - 1])

        # if first slide in cassette
        if i == 0:
            position = cassette_start_pos

        else:
            # if only a difference of 1 between this slide's number and the last's
            diff = abs(number - int(cassette[i - 1].number))
            if diff in allowed_diffs:
                position += diff * normal_skip  # rule: move 5um for consecutive slice (multiplied by number of skips)
            else:
                position += large_skip  # rule: move 100um for skip in slides

            # if last slide in cassette, set next cassette start position and offset indices
            if (i + 1) == len(filtered_files):
                cassette_start_pos = position + cassette_skip  # account for trimming
        # add this to the current 'row' of slides
        cassette.append(Slide(cassette_code,
                              number,
                              position))
    # add this cassette to the total list of slides
    slides += cassette


# %% postprocessing
offset = slides[len(slides) - 1].position
slides = [Slide(slide.cassette, slide.number, slide.position - offset) for slide in slides]

livanova = livanova_setup()
init_e_dist = livanova[1].abs_dist_to(livanova[0])

#  scale!!
ratio = allowed_e_dist / init_e_dist
slides = [Slide(slide.cassette, slide.number, slide.position * ratio) for slide in slides]

livanova = livanova_setup()
final_e_dist = livanova[1].abs_dist_to(livanova[0])

# more output
if printing_output:
    print('scaling by:\t\t{:6.4f}\t\t({:.3f}% shrinkage)\n'
          'init LN distance:\t{:6.1f} um\n'
          'final LN distance:\t{:6.1f} um'.format(ratio, 100 / ratio, init_e_dist, final_e_dist))

    # %% mapping electrode sanity check
    mapping = Electrode(Slide.get(slides, 'VN1_A', 10), Slide.get(slides, 'VN1_A', 66))
    print('mapping to cranial LN:\t{:6.1f} um\t(should be ~3000)'.format(mapping.abs_dist_to(livanova[0])))


# %% output results to csv file with date stamp
os.chdir(maps_dir)
filename = 'slide_map_{}.csv'.format(datetime.datetime.now().strftime('%m%d%Y'))
with open(filename, 'w') as file:
    writer = csv.writer(file)
    writer.writerow(['CASSETTE', 'NUMBER', 'POS [um]'])
    for slide in slides:
        writer.writerow([slide.cassette, slide.number, slide.position])




# %% for converting to xls
# downloaded from https://superuser.com/questions/301431/how-to-batch-convert-csv-to-xls-xlsx
wb = xlwt.Workbook()
ws = wb.add_sheet('data')
with open(filename, 'r') as f:
    reader = csv.reader(f)
    for r, row in enumerate(reader):
        for c, val in enumerate(row):
            ws.write(r, c, val)
wb.save(filename.split('.')[0] + '.xls')
print(os.getcwd() + '/' + filename.split('.')[0] + '.xls')
