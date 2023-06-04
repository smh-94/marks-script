#!/usr/bin/env python
#Place above so you don't have to call python from commandline
#cd command
# python3 project2.py <filename>  
# example run: python3 project2.py -f Flame_DFlowers_20230326.txt -x Xytech_20230326.txt -o db -v
# python3 project2.py -f <filename> -x <filename> -v (optional) -o <csv/db>
import csv
import getpass
import argparse
import re
import pymongo
import datetime
import subprocess
import math
import xlsxwriter
import os
from ffmpeg.video import video_trans_img
print()
this_user = getpass.getuser()
parser = argparse.ArgumentParser(description= 'Command line interface for Project 2')
parser.add_argument('-f','--files',nargs='+', help= 'the filename to process')
parser.add_argument('-x', '--xytech', help = 'xytech file to process')
parser.add_argument('-v', '--verbose', action='store_true',help='verbose')
parser.add_argument('-c','--clear',action ='store_true',help = 'clear duplicates in db')
parser.add_argument('--process', help='process video')
parser.add_argument('-o','--output', help= 'output to csv,db or xlsx')
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["mydatabase"]
col1 = mydb["col1"]
col2 = mydb["col2"]
def extractFrames(frameRanges):
    frame_array = frameRanges.split()
    frame_range_array = []
    for frame_range in frame_array:
        if '-' not in frame_range:
            inner_array =[int(frame_range),int(frame_range)]
            frame_range_array.append(inner_array)
            continue
        working_range = frame_range.split('-')
        # to integers
        inner_array = [int(working_range[0]),int((working_range[1]))]
        frame_range_array.append(inner_array)
    return frame_range_array
def convertToTime(frame, fps):
    if len(frame) > 1:
        start_frame = frame[0]
        end_frame = frame[1]
        
        start_seconds = start_frame / fps
        end_seconds = end_frame / fps
        
        start_minutes = int(start_seconds // 60)
        start_seconds %= 60
        start_hours = int(start_minutes // 60)
        start_minutes %= 60
        
        end_minutes = int(end_seconds // 60)
        end_seconds %= 60
        end_hours = int(end_minutes // 60)
        end_minutes %= 60
        
        start_timestamp = "{:02d}:{:02d}:{:06.3f}".format(start_hours, start_minutes, start_seconds)
        end_timestamp = "{:02d}:{:02d}:{:06.3f}".format(end_hours, end_minutes, end_seconds)
        
        if start_frame == end_frame:
            timestamp = start_timestamp
        else:
            timestamp = "{} - {}".format(start_timestamp, end_timestamp)
    else:
        if frame:
            lazy_array = [frame[0], frame[0]]
            return convertToTime(lazy_array, fps)
        else:
            return ""  # Handle the empty frame list case

    return timestamp
def extract_screen_cap(video_path, frame, output_path):
    #shell command
    #ffmpeg -ss 15 -i twitch_nft_demo.mp4 -vf "scale=96:74" -vframes 1 images3.jpg
    #input_file, out_path, img_prefix, category="png"
    try:
        command = ['ffmpeg', '-ss', frame, '-i', video_path, '-vf','scale=96:74', '-vframes', '1', output_path]
        subprocess.check_output(command, stderr=subprocess.STDOUT)
        print("Screenshot extracted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error outputting frames: {e}")
        return None

def get_total_frames(video_path):
    command = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=nb_frames', '-of', 'default=nokey=1:noprint_wrappers=1', video_path]

    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode('utf-8')
        total_frames = int(output)
        return total_frames
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving total frames: {e}")
        return None
def get_video_fps(video_path):
    command = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate', '-of', 'default=noprint_wrappers=1:nokey=1', video_path]
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode('utf-8').strip()
        numerator, denominator = re.match(r'(\d+)/(\d+)', output).groups()
        fps = float(numerator) / float(denominator)
        return fps
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving video FPS: {e}")
        return None
def ver(file, filename):
    print("File:", filename)
    for key, value in file.items():
        if key == 'Locations':
            mydict = file['Locations']
            for location,frames in mydict.items():
                print(location,': ', frames)
        else:
            print(key, ':', value)
def dbcall(max_range):
    results = {}
    for document in col2.find():
        for path, ranges in document.items():
            if isinstance(ranges, list):
                filtered_ranges = [range_str for range_str in ranges if is_valid_range(range_str, max_range)]
                if filtered_ranges:
                    if path not in results:
                        results[path] = filtered_ranges
                    else:
                        results[path].extend(filtered_ranges)
    return results
def middle_frame(frame_range):
    #['1045-1046', '1166-1168']
    middle_frames = []
    items = frame_range.split('-')
    temp = math.floor(((int(items[0]) + int(items[1]))/2))
    middle_frames.append(temp)
    return middle_frames
def extract_screen_cap(frame, output_path):
    try:
        command = ['ffmpeg', '-ss', str(frame), '-i', 'twitch_nft_demo.mp4', '-vf', 'scale=96:74', '-vframes', '1', output_path]
        subprocess.check_output(command, stderr=subprocess.STDOUT)
        print("Screenshot extracted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error outputting frames: {e}")
        return None 
def export_dict_to_xlsx(data, filename):
    workbook = xlsxwriter.Workbook(filename)
    sheet = workbook.add_worksheet('Sheet1')
    headers = ['Thumbnail','Location','Frame Range','Timestamps']
    sheet.set_column(0, 0, 15)
    sheet.set_column(1, 1, 46)
    sheet.set_column(2, 2, 10)
    sheet.set_column(3, 3, 25) 
    for row in range(1, 30):
        sheet.set_row(row, 70)
    for i, header in enumerate(headers):
        sheet.write(0, i, header)
    row_index = 1
    for file_path, inner_array in data.items():
        frame_ranges, timestamps = inner_array
        for i in range(len(frame_ranges)):
            sheet.write(row_index, 1, file_path)
            sheet.write(row_index, 2, frame_ranges[i])
            sheet.write(row_index, 3, timestamps[i])
            middle_frame_value = middle_frame(frame_ranges[i])
            thumbnail_path = f"thumbnail_{file_path}_{middle_frame_value}.jpg"
            extract_screen_cap(middle_frame_value, thumbnail_path)
            sheet.insert_image(row_index, 0, thumbnail_path, {'x_scale': 0.5, 'y_scale': 0.5})

            row_index += 1
    workbook.close()
def is_valid_range(range_str, max_range):
    range_parts = range_str.split('-')
    start_frame = int(range_parts[0])
    end_frame = int(range_parts[-1])
    return start_frame <= max_range or end_frame <= max_range
def get_video_fps(video_path):
    command = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate', '-of', 'default=noprint_wrappers=1:nokey=1', video_path]
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode('utf-8').strip()
        numerator, denominator = re.match(r'(\d+)/(\d+)', output).groups()
        fps = float(numerator) / float(denominator)
        return fps
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving video FPS: {e}")
        return None
def get_total_frames(video_path):
    command = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=nb_frames', '-of', 'default=nokey=1:noprint_wrappers=1', video_path]
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT).decode('utf-8')
        total_frames = int(output)
        return total_frames
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving total frames: {e}")
        return None
def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"File deleted: {file_path}")
    except OSError as e:
        print(f"Error deleting file: {e}")
args = parser.parse_args()
#Open Xytech file
if args.xytech:
    xytech_file_location = args.xytech
    xytech_folders = []
    #retrieve date
    date_string = args.xytech.split("_")[1].split(".")[0]
    file_date = datetime.datetime.strptime(date_string,'%Y%m%d').date()
    file_date = f"{file_date.month:02d}-{file_date.day:02d}-{file_date.year}"
    read_xytech_file = open(args.xytech, "r")
    xytech_details = {"Machine" : "Xytech"}
    notes_section = False
    names = []
    for line in read_xytech_file:
        if "Xytech Workorder" in line:
            xytech_details["Workorder"] = line.split(" ")[2].strip()
            xytech_details["Date"] = file_date
        if "Producer:" in line:
            xytech_details["Producer"] = re.search(fr"(?<=\b{'Producer: '}\b)(.*)", line).group(0)
        if "Operator:" in line:
            details = line.split(" ")
            xytech_details["Operator"] = re.search(fr"(?<=\b{'Operator: '}\b)(.*)", line).group(0)
        if "Job:" in line:
            details = line.split(" ")
            xytech_details["Job"] = re.search(fr"(?<=\b{'Job: '}\b)(.*)", line).group(0)
        if "/" in line:
            if "Avatar" not in line:
                continue
            xytech_folders.append(line.strip())
        if "Notes:" in line:
            notes_section = True
        elif notes_section:
            extracted_names = re.findall(r'\b[A-Z][a-zA-Z]{1}[a-z]+\b', line)
            capitalized_names = [name for name in extracted_names if len(name) >= 3 and name[:2].isupper()]
            names.extend(capitalized_names)
    xytech_details["Name on file"] = names
    editor_details_list = []
    if args.files:   
        for file in args.files:
            reports = {}
            #Open baselight/flame file
            file_location = file
            #retrieve users and date
            get_date = datetime.datetime.strptime(file.split("_")[2].split(".")[0],'%Y%m%d').date()
            get_date = f"{get_date.month:02d}-{get_date.day:02d}-{get_date.year}"
            editor_details = {
                "Editor": file.split("_")[1][1:],
                "Date": get_date,
                "Machine": file.split("_")[0],
            }
            
            read_file = open(file_location, "r")
            for line in read_file:
                #removing space in filepath
                correct_folder = False
                correct_folder_path = ''
                if "flame" in line:
                    line = re.sub(r"\s", "/", line, count=1)
                line_parse = line.split(" ", 1)
                slides = line_parse[1].split(" ")
                importfile_folder = line_parse.pop(0)
                importfile_folder = re.sub(r'^.*?(avatar.*)', r'\1', importfile_folder, flags=re.IGNORECASE)
                current_folder = ''
                for file in xytech_folders:
                    if importfile_folder in file:
                        current_folder = file
                        break
                first=""
                pointer=""
                last=""
                ranges = []
                for numeral in slides:
                    #Skip <err> and <null>
                    if not numeral.strip().isnumeric():
                        continue
                    #Assign first number
                    if first == "":
                        first = int(numeral)
                        pointer = first
                        continue
                    #Keeping to range if succession
                    if int(numeral) == (pointer+1):
                        pointer = int(numeral)
                        continue
                    else:
                        #Range ends or no sucession, output
                        last = pointer
                        if first == last:
                            ranges.append(str(first))
                        else:
                            ranges.append("%s-%s" % (first, last))
                        first= int(numeral)
                        pointer=first
                        last="" 
                #Working with last number each line 
                last = pointer
                if first != "":
                    if first == last:
                        ranges.append(str(first))
                    else:
                        ranges.append("%s-%s" % (first,last))
                if current_folder not in reports:
                    reports[current_folder] = ranges
                elif current_folder in reports:
                    for rangex in ranges:    
                        reports[current_folder].append(rangex)
            editor_details['Locations'] = reports
            editor_details_list.append(editor_details)
        if args.verbose:
            ver(xytech_details,args.xytech)
            print()
            ver(editor_details,file)
        if args.output == "db":
            data1 = {
                "ran by": this_user,
                "machine": xytech_details["Machine"],
                "Name on file": xytech_details["Name on file"],
                "date": xytech_details["Date"],
            }
            duplicate_workorder = col1.find_one(data1)

            if duplicate_workorder:
                print("Duplicate workorder found. Data not inserted.")
            else:
                col1.insert_one(data1)
        for editor_details in editor_details_list:
                data2 = {
                    "User on file": editor_details["Editor"],
                    "file_date": editor_details["Date"],
                }
                mydict = editor_details['Locations']
                for location, frames in mydict.items():
                    data2[location] = frames
                # Remove submitted_date from the query data
                # Check for duplicate in File Collection
                duplicate_editor = col2.find_one(data2)
                if duplicate_editor:
                    print("Duplicate editor data found. Data not inserted.")
                else:
                    col2.insert_one(data2)
                    print("Data inserted successfully.")

    if args.output == "csv":
        csv_filename = f"{xytech_details['Date']}.csv"
        if os.path.exists(csv_filename):
            print(f"File '{csv_filename}' already exists. Skipping CSV file creation.")
        else:
            fieldnames = set()
            for editor_details in editor_details_list:
                fieldnames.update(editor_details.keys())
            fieldnames.update(xytech_details.keys())
            fieldnames = list(fieldnames)

            with open(csv_filename, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for editor_details in editor_details_list:
                    editor_details.update(xytech_details)
                    writer.writerow(editor_details)
if args.process:
    input_video_path = args.process
    total_frames = get_total_frames(input_video_path)
    fps = int(get_video_fps(input_video_path))
    list = dbcall(total_frames)
    #creating one giant dictionary so we hash each middleframe to its image
    #for easy export
    
    frames_to_capture = {}
    for key,value in list.items():
        #LIST IS A DICTIONARY CONTAINING {FOLDER : LIST OF RANGES}
        both_arrays = []
        frame_ranges = []
        time_ranges = []
        for rangex in value:
            #VALUE IS A LIST OF STRINGS ['60-62','75-80']
            #RANGE IS A STRING
            #SAMPLE : ('60-62')
            if '-' not in rangex:
                continue
            else:
                #ONLY ADDS TO LIST WHEN A HYPHEN IS IN
                frame_ranges.append(rangex)
                frame_range_split = rangex.split('-')
                #switches from string to int
                temp = [int(frame_range_split[0]),int(frame_range_split[1])]
                #TEMP IS NOW ['60','62']
                time_ranges.append(convertToTime(temp,fps))
        both_arrays.append(frame_ranges)
        both_arrays.append(time_ranges)
        #frames_to_capture is now ready to export
        frames_to_capture[key] = both_arrays
if args.output == 'xlsx':
    headers = {'Thumbnail', 'Location','Frame Range', 'Time Range'}
    #clean data
    frames_to_capture = {k: v for k, v in frames_to_capture.items() if any(v)}
    export_dict_to_xlsx(frames_to_capture, 'output.xlsx')