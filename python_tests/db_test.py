#!/usr/bin/env python
editor_details = {"Reports" : ["/images1/Avatar/reel5/partA/1920x1080 1-5 6-9 ", "/images1/Avatar/reel3/partA/1920x1080 1-6 6-9"]}
current_folder = "/images1/Avatar/reel5/partA/1920x1080"
ranges = ['10-15','20-25']
already_exists = False
if "Reports" in editor_details:
    for value_index, value in enumerate(editor_details["Reports"]):
        if current_folder in value:
            already_exists = True
            if already_exists:
                for range in ranges:
                    editor_details["Reports"][value_index] += range + " "
            else:
                continue
    if not already_exists:
        string = current_folder + " "
        for range in ranges:
            string += range + " "
        editor_details["Reports"].append(string.rstrip())
    print()