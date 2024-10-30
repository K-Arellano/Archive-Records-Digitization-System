import numpy as np
import jiwer
from IPython.display import display
import pandas as pd

def getErrorRate(temp_corrected, temp_ocr):
    output = jiwer.process_words(temp_corrected, temp_ocr)
    outputChar = jiwer.process_characters(temp_corrected, temp_ocr)

    if output and outputChar:
        WER = min(output.wer * 100, 100.0)
        CER = min(outputChar.cer * 100, 100.0)

    return {'wer': WER, 'cer': CER}

def getErrorBaseline_Corrected(corrected_data, ocr_data):
    try:
        error_rate = []
        ocr_dict = {item['id']: item for item in ocr_data}
        defaultValue = 100.00

        # Iterate over each corrected item to compare with OCR data
        for corrected_item in corrected_data:
            corrected_id = int(corrected_item['id'])
            temp_corrected = corrected_item['student_name'].strip()

            # If corrected 'student_name' field is not empty
            if temp_corrected != '':
                # Check if corrected data exists in the OCR data
                if corrected_id in ocr_dict:
                    ocr_item = ocr_dict[corrected_id]
                    temp_ocr = ocr_item['student_name'].strip()

                    # Calculate error rates between corrected and OCR 'student_name'
                    output = getErrorRate(temp_corrected, temp_ocr)

                    # Append error rates with row id from the table
                    error_rate.append({
                        'id': corrected_id,
                        'wer': output['wer'],
                        'cer': output['cer'],
                    })

                    # Delete the OCR item to prevent re-referencing
                    del ocr_dict[corrected_id]

                # If corrected data does not exist in OCR data
                else:
                    # Find the closest match in remaining OCR data based on error rates
                    if len(ocr_dict) > 0:
                        min_wer = defaultValue
                        min_cer = defaultValue
                        min_id = None

                        # Iterate over remaining OCR data to find lowest error rates
                        for ocr_id, ocr_item in ocr_dict.items():
                            temp_ocr = ocr_item['student_name'].strip()
                            output = getErrorRate(temp_corrected, temp_ocr)

                            # If exact match found (0% WER and CER), stop searching
                            if output['cer'] == 0.00 and output['wer'] == 0.00:
                                min_id = ocr_id
                                min_cer = output['cer']
                                min_wer = output['wer']
                                break
                            else:
                                # Otherwise, find the minimum error rates
                                if output['cer'] < min_cer:
                                    min_id = ocr_id
                                    min_cer = output['cer']
                                    min_wer = output['wer']

                        # Set error rates to the closest match found
                        if min_cer:
                            error_rate.append({
                                'id': corrected_id,
                                'wer': min_wer,
                                'cer': min_cer,
                            })
                            del ocr_dict[min_id]

                    else:
                        # Append the error rates for the current corrected item
                        error_rate.append({
                            'id': corrected_id,
                            'wer': defaultValue,
                            'cer': defaultValue,
                        })

            # If corrected 'student_name' field is empty
            else:
                error_rate.append({
                    'id': corrected_id,
                    'wer': defaultValue,
                    'cer': defaultValue,
                })

        # If there are remaining unmatched OCR items, add default error rates for them
        if ocr_dict and len(ocr_dict) > 0:
            remaining_count = len(ocr_dict)
            error_rate.extend([{
                'id': 9999,
                'wer': 100.00,
                'cer': 100.00,
            }] * remaining_count)

        return error_rate

    except Exception as e:
        print(f"getErrorBaseline_Corrected Error: {e}")


def benchmarkerTest(corrected_data, ocr_data):
    try:
        #get all error rate with a baseline of corrected data from manual correction of user
        error_rate = getErrorBaseline_Corrected(corrected_data, ocr_data)

        if error_rate:
            if len(error_rate) > 0:
                if len(error_rate) > 0:
                    wer_percentile = [item['wer'] for item in error_rate]
                    cer_percentile = [item['cer'] for item in error_rate]

                    average_WER = np.mean(wer_percentile) if wer_percentile else 0.0
                    average_CER = np.mean(cer_percentile) if cer_percentile else 0.0

                    final_list = [index for index in error_rate if int(index['id']) != 9999]

                    if final_list:
                        return {
                            "error_rate": final_list,
                            "average_WER": average_WER,
                            "average_CER": average_CER,
                            }
        
        return {
            "error_rate": [],
            "average_WER": 100.00,
            "average_CER": 100.00,
            }
    
    except Exception as e:
        print(f"benchmarker Error: {e}")
