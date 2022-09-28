import tempfile
from unittest import case
import pytesseract    # ======= > Add
import cv2
import pandas as pd
try:
    from PIL import Image
except:
    import Image
from django.views.decorators.csrf import csrf_exempt
import json
from .preprocess import *
import re
#  function exports
from .ocrAlgorithms.pan_read import pan_read_data
from .ocrAlgorithms.naiveOCR import image_preprocess, mrz_selection, mrz_postprocess, ocr_on_selection


def naiveOCR(image):
    # image = request.data['image']
    # a new file which is a temp file.
    fp = tempfile.NamedTemporaryFile()

    # we write the uploaded image in temp file
    for chunk in image.chunks():
        fp.write(chunk)

    # OpenCV read file
    img = cv2.imread(fp.name)

    # New method
    # # img, height, width = read_image(img_src)
    # img_roi = image_preprocess(img)
    # img_mrz = mrz_selection(img_roi)
    # dim_mrz = mrz_selection(img_roi)
    # mrz = ocr_on_selection(dim_mrz, img_roi, '--psm 12')
    # lastname, firstname, pp_no = mrz_postprocess(mrz)
    # print(lastname, firstname, pp_no)
    # Old method
    custom_config = r'-l eng --psm 6'
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = thresholding(gray)
    content = pytesseract.image_to_string(
        thresh, config=custom_config)
    # print(pan_read_data(content))
    response_data = {}
    response_data['content'] = content
    return response_data
# pytessaract-> draw output-> recreate text char by char


def boxOCR(response):
    image = response['image']
    content = response['content']
    # print(content)
    # a new file which is a temp file.
    fp = tempfile.NamedTemporaryFile()

    # we write the uploaded image in temp file
    for chunk in image.chunks():
        fp.write(chunk)

    # OpenCV read file
    img = cv2.imread(fp.name)
    custom_config = r'-l eng --psm 6'
    config_digits = r'--oem 3 --psm 6 outputbase digits'
    # preprocess image -> OCR -> draw output -> recreate text char by char
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = thresholding(gray)
    openingimg = opening(gray)
    cannyimg = canny(gray)
    bboxes = pytesseract.image_to_boxes(thresh, config=custom_config)
    # thresh = image_preprocess(img)
    data = pytesseract.image_to_data(
        thresh, config=custom_config, output_type=pytesseract.Output.DATAFRAME)

    # lines = formatdataframe(data)
    response = documentMapping(content, data)
    return response


def documentMapping(content, data):
    if content == 'AadharFront':
        return extractAadharFront(data)
    elif content == 'AadharBack':
        return extractAadharBack(data)
    elif content == 'PAN':
        return extractPAN(data)
    elif content == 'DrivingLicense':
        return extractDrivingLicense(data)
    elif content == 'Passport':
        return extractPassport(data)

# format the existing text


def formatdataframe(df, conf=60):
    fix = 0
    for i, row in df.iterrows():
        if i > 0 and df.at[i, 'par_num'] != df.at[i-1, 'par_num']:
            fix = df.at[i-1, 'line_num']
        if row["par_num"] > 1:
            df.at[i, 'line_num'] = df.at[i, 'line_num'] + fix
    text = df[df.conf > conf]
    lines = text.groupby('line_num')['text'].apply(list)
    # print(lines)
    lines = lines.reset_index()
    return lines
# Day 0
# Document is defined by User
# Now we extract the data from the document
# Speed and accuracy(format and size)

# Day1
# If we extract data but we are not sure about the format/document


def extractAadharFront(data):
    # print(lines)
    lines = formatdataframe(data, 60)
    data = {}
    # run search for gender
    ind = 0
    gnd = 0
    # flag for date confirmation
    dateflag = False
    # Search for gender as a hook
    for row in lines['text']:
        for item in row:
            # print(item, type(item))
            if item == 'MALE' or item == 'FEMALE':
                data['Gender'] = item
                gnd = ind
            # optimize it: aadhar ka default behaviour: '/MALE'
            elif item == '/MALE' or item == '/FEMALE':
                data['Gender'] = item[1:]
                # catch the line number
                gnd = ind
        ind += 1
    if gnd == 0:
        print('code fatgya')
        return
    # check for regex number/number/number: this is our confirmation
    rgx = '^[0-3]?[0-9].[0-3]?[0-9].(?:[0-9]{2})?[0-9]{2}$'
    dateRow = lines.loc[gnd-1, 'text']
    for item in dateRow:
        if re.search(rgx, item):
            data['Date'] = item
            dateflag = True
            # print(item, 'date milgya')
    # prepare data on basis of dateflag
    if dateflag:
        # Get name
        nameRow = lines.loc[gnd-2, 'text']
        name = ''
        for item in nameRow:
            if len(item) > 3 and item.isalpha():
                name += item + ' '
        data['Name'] = name[:-1]
        # Get aadhar number
        aadharnumRow = lines.loc[gnd+1, 'text']
        aadharNum = ''
        for item in aadharnumRow:
            if len(item) == 4:
                aadharNum += item+' '
        data['AadharNumber'] = aadharNum[:-1]
        print(data)
        return data


def extractAadharBack(data):
    lines = formatdataframe(data, 60)
    data = {}
    address = ''
    ind = 0
    addressLine = 0
    pincodeLine = 0
    for row in lines['text']:
        for item in row:
            item = item.strip()
            if item == 'Address' or item == 'Address:':
                addressLine = ind
            if item.isnumeric() and len(item) == 6:
                data['Pincode'] = item
                pincodeLine = ind
        ind += 1
    for i in range(addressLine, pincodeLine+1):
        for item in lines.loc[i, 'text']:
            if len(item) >= 3 and item != 'Address:':
                address += item + ' '
    data['Address'] = address[:-1]
    print(data)
    pass


def extractPAN(data):
    # print(lines)
    lines = formatdataframe(data)
    regexPAN = "[A-Z]{5}[0-9]{4}[A-Z]{1}"
    # check for regex number/number/number: this is our confirmation
    rgxDate = '^[0-3]?[0-9].[0-3]?[0-9].(?:[0-9]{2})?[0-9]{2}$'
    data = {}
    newPAN = False
    ind = 0
    panLine = 0
    for row in lines['text']:
        for item in row:
            item = item.strip()
            if re.search(regexPAN, item):
                data['PAN'] = item
                panLine = ind
            if re.search('Name', item):
                newPAN = True
            if re.search(rgxDate, item):
                data['DOB'] = item
        ind += 1
    # error handling
    if panLine == 0:
        return
    if newPAN:
        # Get Name from PAN
        nameRow = lines.loc[panLine+2, 'text']
        name = ''
        for item in nameRow:
            item = item.strip()
            if item.isalpha():
                name += item+' '
        data['Name'] = name[:-1]
        # Get Father's Name
        fathersNameRow = lines.loc[panLine+4, 'text']
        fathersName = ''
        for item in fathersNameRow:
            item = item.strip()
            if item.isalpha():
                fathersName += item + ' '
        data['FathersName'] = fathersName[:-1]
    else:
        # if Permanent Account Number is present in the previous line
        checkString = ['Permanent', 'Account', 'Number']
        checkLoc = lines.loc[panLine-1, 'text']
        if all(x in checkLoc for x in checkString):
            panLine -= 1
        # Get fathers name
        fathersNameRow = lines.loc[panLine-2, 'text']
        fathersName = ''
        for item in fathersNameRow:
            item = item.strip()
            if item.isalpha():
                fathersName += item + ' '
        data['FathersName'] = fathersName[:-1]
        # Get Name from PAN
        nameRow = lines.loc[panLine-3, 'text']
        name = ''
        for item in nameRow:
            item = item.strip()
            if item.isalpha():
                name += item+' '
        data['Name'] = name[:-1]
    print(data)
    pass


def extractPassport(data):
    lines = formatdataframe(data, 30)
    print(lines)
    rgxDate = '^([0-2][0-9]|(3)[0-1])(\/)(((0)[0-9])|((1)[0-2]))(\/)\d{4}$'
    rgxPassport = '^[A-Z]{1}[0-9]{7}$'
    data = {}
    dates = []
    ind = 0
    passportLine = 0
    for row in lines['text']:
        for item in row:
            item = item.strip()
            if re.search(rgxPassport, item):
                data['PassportNumber'] = item
                passportLine = ind
            if re.search(rgxDate, item):
                dates.append(item)
        ind += 1
    # Get Passport Number
    # passportNumRow = lines.loc[passportLine+1, 'text']
    # passportNum = ''
    # for item in passportNumRow:
    #     item = item.strip()
    #     if len(item) == 9:
    #         passportNum += item
    # data['PassportNumber'] = passportNum
    # Get Name
    nameRow = lines.loc[passportLine+2, 'text']
    name = ''
    for item in nameRow:
        item = item.strip()
        if item.isalpha() and item.isupper():
            name += item + ' '
    surnameRow = lines.loc[passportLine+1, 'text']
    surname = ''
    for item in surnameRow:
        item = item.strip()
        if item.isalpha() and item.isupper():
            surname += item + ' '
    data['Name'] = name[:-1] + ' ' + surname[:-1]
    # data['Name'] = name[:-1]
    # Get Date of Birth, Date of Issue, Date of Expiry
    # data['DOB'] = dates[0]
    # data['DateOfIssue'] = dates[1]
    # data['DateOfExpiry'] = dates[2]
    print(data, dates)
    pass


def extractDrivingLicense(data):
    pass
# then output it
# expose the API
