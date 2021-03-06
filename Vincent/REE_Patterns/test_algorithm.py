﻿import spectral as sp
import os 
import numpy as np 
import Classifier_SAM as SAM
from glob import glob

testOxi = 1
normalize_button = 0
# do nothing to testing data SP array.
def dataProcess_alg_pass(SP):
    return SP

#exclude the background pixel, into an array(spectrum) and return T/F, True: background; False: not a background
def exclude_BG(pixel_array):
    if sum(pixel_array) == 0:
        return True
    else:
        return False
		
#cal the average spectrum of a img. Input a img and return an array (the same format as Spectral lib's )
def cal_avg_SP(img):
    width, height, deepth = img.shape
    sum_SP = 0
    count = 0
    for i in range(width):
        for j in range(height):
            pixel_SP = img[i,j]
            if exclude_BG(pixel_SP):
                continue
            else:
                sum_SP += pixel_SP
                count += 1

    return sum_SP / count
    

# input testing data type, input index number and file type. (both manually or UI). This could input one data file and return img_testing
def input_testing_data(index = '10',type = 'oxido', check_all = 0):

    filePath =  'data/'
    if not check_all :
        num = input("input the index number of your testing oxido file(01-41)\n")
        type = input("input the file type you want to test, oxido/ sulfuro or  1/2\n")

        if type == 'oxido':
            fileName_testing = 'oxidos/EscOx'+ num + 'B1_rough_SWIR.hdr'
        elif type == 'sulfuro':
            fileName_testing = 'sulfuros/EscSulf' + num + '_Backside_SWIR_Subset_Masked.hdr'
    elif check_all:
       if type == 'oxido':
            fileName_testing = 'oxidos/EscOx'+ index + 'B1_rough_SWIR.hdr'
       elif type == 'sulfuro':
            fileName_testing = 'sulfuros/EscSulf' + index + '_Backside_SWIR_Subset_Masked.hdr'

    try:
        img_testing = sp.open_image(filePath + fileName_testing)
    except Exception as err:
        print('Cannot open your testing file.\n Error info:' + str(err.args), end = '\n')
        exit(0)
    return img_testing

# input SP_reference_oxido, sulfuro, check_all =1 if you want to check all files and got accuracy file. and dataProcess_alg to process your testing sp array 
def check(SP_ref_oxido, SP_ref_sulfuro, check_all = 0, dataProcess_alg = dataProcess_alg_pass, classifier = SAM.classifier_SAM,file_acc_name = 'acc_res.txt'):
    if check_all == 1:    
        filePath = 'data/'
        files_list_oxi = glob(filePath + 'oxidos/'+"*.hdr")
        files_list_sul = glob(filePath + 'sulfuros/'+'*.hdr')
        num_oxi = len(files_list_oxi)
        num_sul = len(files_list_sul)
    
        #accuracy dict, the index is testing files' name and values is a list [single_SP, all_SP]
        acc_dict_oxi = {}
        acc_dict_sul = {}
    
        #switch
        global testOxi
        #check all the oxidos.
        for i in range(num_oxi):
            if testOxi == 0:
                break 
            index0 = files_list_oxi[i].split('Esc')[-1].split('Ox')[-1][0:2]
            img_testing = input_testing_data(index = index0, type = 'oxido', check_all = check_all)

            #core alg of check
            # ////////SP_ref_oxido, SP_ref_sulfuro = input_training_data(use_multi_SP_as_reference = 1)
            res, accurarcy = Tranversing(SP_ref_oxido, SP_ref_sulfuro, img_testing, testingType = 'oxido', dataProcess_alg = dataProcess_alg,classifier = classifier)
            acc_dict_oxi.setdefault(str(img_testing).split('/')[2].split('_')[0] + '_res.bmp',accurarcy)
            #acc_dict_oxi[str(img_testing).split('/')[2].split('_')[0] + '_res.bmp'].append(accurarcy)

            #showing the progress
        
            acc_key = str(img_testing).split('/')[2].split('_')[0] + '_res.bmp'
            print('%s   %f   \n' % (acc_key, acc_dict_oxi[acc_key] ))


        #check all the sulfuros  
        for i in range(num_sul):
        
            index0 = files_list_sul[i].split('Esc')[-1].split('Sulf')[-1][0:2] # attention: debug err? after split('Esc'), u got a list containing only one element.... x[0] == x[-1]
            img_testing = input_testing_data(index = index0, type = 'sulfuro', check_all = check_all)

            #core alg of check
            # /////SP_ref_oxido, SP_ref_sulfuro = input_training_data(use_multi_SP_as_reference = 0)
            res, accurarcy = Tranversing(SP_ref_oxido, SP_ref_sulfuro, img_testing,  testingType = 'sulfuro', dataProcess_alg = dataProcess_alg,classifier = classifier)
            acc_dict_sul.setdefault(str(img_testing).split('/')[2].split('_')[0] + '_res.bmp',accurarcy)
            #acc_dict_sul[str(img_testing).split('/')[2].split('_')[0] + '_res.bmp'].append(accurarcy)

            #showing the progress
            acc_key = str(img_testing).split('/')[2].split('_')[0] + '_res.bmp'
            print('%s   %f   \n' % (acc_key, acc_dict_sul[acc_key] ))

        #write the results into txt
        file_res = open(filePath +file_acc_name, 'w')
        file_res.write('fileName \t \t Accuracy\n')

        acc_dict_oxi = sorted(acc_dict_oxi.items(), key = lambda d: d[0])
        acc_dict_sul = sorted(acc_dict_sul.items(), key = lambda d: d[0])
        for i in range(len(acc_dict_oxi)):
            file_res.write("%s \t %f\n" % (acc_dict_oxi[i][0],acc_dict_oxi[i][1]))
        for i in range(len(acc_dict_sul)):
            file_res.write("%s \t %f\n" % (acc_dict_sul[i][0],acc_dict_sul[i][1]))

    elif check_all == 0:
    
        #input testing data
        img_testing = input_testing_data()
    
        # tranversing the img and cal spectral angle between testImg and refImg. 
        #Input: testing img and reference img.
        if 'Sulf' in str(img_testing): 
            res, accurarcy = Tranversing(SP_ref_oxido,SP_ref_sulfuro, img_testing, testingType = 'sulfuro', dataProcess_alg = dataProcess_alg)
        
        else:
            res, accurarcy = Tranversing(SP_ref_oxido,SP_ref_sulfuro, img_testing, testingType = 'oxido',dataProcess_alg = dataProcess_alg)

        width, height, deepth = img_testing.shape
    
        resName = str(img_testing).split('/')[2].split('_')[0] + '_res.bmp'
        filePath = 'data/'
        show_res(res,accurarcy, width, height, filePath, resName, showImg = 0)

# Tranverse the whole image and return its' pixel record list and checking accuracy
def Tranversing(SP_reference1, SP_reference2, img_testing, testingType = 'oxido', dataProcess_alg = dataProcess_alg_pass, classifier = SAM.classifier_SAM):
    
    width, height, deepth = img_testing.shape
    deepth = len(SP_reference1)
    #res is a list that would save the classification result, 2 is background, 1 is right, 0 is wrong.
    res = []
    # the pixel number of background
    count_bg = 0
    count_right = 0
    for i in range(width):
        for j in range(height):
            SP_testing = img_testing[i,j]
                
            # if this pixel is background, res = 2
            if exclude_BG(SP_testing):
                res.append(2)
                count_bg += 1
                continue
            
            # pre-algorithm process data.
            SP_testing = dataProcess_alg(SP_testing)

            #testing, debugging
            if normalize_button == 1:
                import SP_paras
                SP_testing, SP_reference1, SP_reference2 = SP_paras.normalize(SP_reference1,SP_reference2,SP_testing)
            
            # compute spectrum angles.
            class_type = classifier(SP_reference1,SP_reference2,SP_testing)
                        
            # attention please: this is the red mark code, maybe u could add more barriers here.
            # attention please: now ref1 is oxido, ref2 is sulfuro, testing img is a oxido
            if testingType == 'oxido' or testingType == 1:
                if class_type == 1:
                    res.append(1)
                    count_right += 1
                else:
                    res.append(0)
            elif testingType == 'sulfuro'or testingType == 2:
                if class_type == 2:
                    res.append(1)
                    count_right += 1
                else:
                    res.append(0)
    accurarcy = count_right / (width * height - count_bg)       
    return [res,accurarcy]

#load average sulfuros data, return a spectrum array. 
def load_training_SP(type = 'sulfuro'):
    filePath = 'data/'
    # fileName = 'sulfuros/'

    fileNameList =  os.listdir(filePath + type +'s/') #  glob(filePath + 'sulfuros/' + '*.hdr')
    
    fileName_aver = 'spectrum_average.txt'
    if fileName_aver in fileNameList :
        file_temp = open(filePath + type + 's/' + fileName_aver)
        sp_average = file_temp.read()
        sp_average = sp_average.replace('[', '')
        sp_average = sp_average.replace(']', '')
        sp_average = sp_average.split()
        file_temp.close()
        return np.array(sp_average ,dtype = np.float)
    else:
        file_temp = sp.open_image(filePath + type + 's/' + fileNameList[1])
        file_temp.close()
        pass
    sp.open_image(filePath + fileName)

    #attention: other choices to input a training spectrum

def load_image(type = 'oxido',index = '01', filePath = None):	
    if filePath == None:
        if type == 'oxido':
            filePath = 'data/oxidos/'
            fileName = 'EscOx' + index + 'B1_rough_SWIR.hdr'
        elif type == 'sulfro':
            filePath = 'data/sulfuros/'
            fileName = 'EscSulf' + index + '_Backside_SWIR_Subset_Masked.hdr'
        
        image = sp.open_image(filePath + fileName)
    else:
        image = sp.open_image(filePath)
    return image
