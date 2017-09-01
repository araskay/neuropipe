def addniigzext(filename):
    if (filename[-4:len(filename)] == '.nii'):
        print('Input is a file with .nii extension. Cannot add .nii.gz extension')
        return(filename)
    elif (filename[-7:len(filename)] != '.nii.gz'):
        return(filename+'.nii.gz')
    else:
        return(filename)

def removeniftiext(filename):
    if (filename[-4:len(filename)] == '.nii'):
        return(filename[0:-4])
    elif (filename[-7:len(filename)] == '.nii.gz'):
        return(filename[0:-7])
    else:
        return(filename)
    