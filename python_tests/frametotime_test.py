import math
#********working********
sample_frames = ("80-90")
sample_frames2 = ("40-45 50-60 61-62")
sample_frames3 = ("70 73-74")
sample_array = [sample_frames,sample_frames2,sample_frames3]
def extractFrames(frameRanges):
    #returns a frame range array from a string containing frame ranges
    frame_array = frameRanges.split()
    #frame_array = ("40-45","50-60","61-62")
    frame_range_array = []
    for frame_range in frame_array:
        if '-' not in frame_range:
            inner_array =[int(frame_range),int(frame_range)]
            frame_range_array.append(inner_array)
            continue
        working_range = frame_range.split('-')
        #convert to integers
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
        lazy_array = [frame[0],frame[0]]
        timestamp = convertToTime(lazy_array,fps)
    return timestamp
def middle_frame(frame_range):
    return math.floor((frame_range[0]+frame_range[1])/2)
ranges = extractFrames(sample_frames)
for range in ranges:
    print('start frame: ', range[0], 'end frame: ', range[1])
    print('middle frame: ' + str(middle_frame(range)) + ' @ ' + str(convertToTime([middle_frame(range)],24)) + '\n')  
    print(range)
    print(type(range[0]),type(range[1]))
    print(convertToTime(range,60))