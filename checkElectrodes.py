import random 
import random

import serial 
import time
import numpy as np
import pandas as pd
import csv
from datetime import datetime

import pathlib
from Generic.Model.Data.File.lib.MatlabFile import MatlabFile

from PyQt5.QtWidgets import QApplication, QMessageBox
import asyncio

from sciopy import (
    SystemMessageCallback,
    conf_n_el_16_adjacent,
    conf_n_el_32_adjacent,
    connect_COM_port,
    StartStopMeasurement,
    reshape_full_message_in_bursts,
    del_hex_in_list,
    split_bursts_in_frames,
    ResetMeasurementSetup,
    SoftwareReset
)

from sciopy.sciopy_dataclasses import ScioSpecMeasurementConfig

# IMPEDANCE_MAX= 500
# AMPLITURE = 0.001

FILENAME = 'electrode_1_1.eit' #### redundent 



def generate_electrodes(IMPEDANCE_MAX, AMPLITUDE, num_electrodes):
    
    #front= [1, 2 ,3 ,4, 5 ,6, 17, 18, 19, 20, 21, 22]
    #back = [9 , 10, 11, 12, 13, 14 ,25, 26, 27, 28 ,29 ,30]
    #right = [15, 16, 31, 32] 
    #left = [7, 8 , 23 ,24]

    #old
    #electrodes_to_adjust = check_electrode(filename = FILENAME)
    ch_group = []
    if num_electrodes == 16:
        ch_group = [1]
    else:
        ch_group = [1, 2]
    return return_eletrodes(get_impedances(IMPEDANCE_MAX, AMPLITUDE, num_electrodes, ch_group), num_electrodes)

    #return  {
    #"front" : [random.randint(1, 20) for i in range(0, 12)],# 1, 2 ,3 ,4, 5 ,6, 17, 18, 19, 20, 21, 22
    #"back" : [random.randint(1, 20) for i in range(0, 12)],# 9 , 10, 11, 12, 13, 14 ,25, 26, 27, 28 ,29 ,30
    #"right" : [random.randint(1, 20) for i in range(0, 4)],# 15, 16, 31, 32
    #"left" : [random.randint(1, 20) for i in range(0, 4)],# 7, 8 , 23 ,24
#}


def adjust_electrodes(IMPEDANCE_MAX, AMPLITUDE,num_electrodes):
   # electrodes_to_adjust = check_electrode(filename = 'setup_00001.eit')################ loaded file from the sciospec device

    ch_group = []
    if num_electrodes == 16:
        ch_group = [1]
    else:
        ch_group = [1, 2]
    return return_eletrodes(get_impedances(IMPEDANCE_MAX, AMPLITUDE, num_electrodes, ch_group), num_electrodes)
    #return  {
    #"front" : [random.randint(1, 20) for i in range(0, 12)],
    #"back" : [random.randint(1, 8) for i in range(0, 12)],
    #"right" : [random.randint(1, 8) for i in range(0, 4)],
    #"left" : [random.randint(1, 8) for i in range(0, 4)],
#}



def return_eletrodes(electrodes_to_adjust, num_electrodes):
    electrode_values = {
        "front": [],
        "back": [],
        "right": [],
        "left": []
    }
    adjusted = 0
    if not electrodes_to_adjust:
        adjusted = 1
		
    if num_electrodes == 16:
        front_indices = [1, 2, 3, 4, 5, 6, 7, 8,9,10,11,12]
        back_indices = [17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28]
        right_indices = [13, 14, 15, 16]
        left_indices = [29, 30, 31, 32]
    else:
        # front_indices = [1, 2, 3, 4, 5, 6, 17, 18, 19, 20, 21, 22]
        # back_indices = [9, 10, 11, 12, 13, 14, 25, 26, 27, 28, 29, 30]
        # right_indices = [15, 16, 31, 32]
        # left_indices = [7, 8, 23, 24]
        front_indices = [1, 2, 3, 4, 5, 6, 7, 8,9,10,11,12]
        back_indices = [17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28]
        right_indices = [13, 14, 15, 16]
        left_indices = [29, 30, 31, 32]

    # Assign values to front electrodes
    for index in front_indices:
        value = 15 if index in electrodes_to_adjust else 5
        electrode_values["front"].append(value)

    # Assign values to back electrodes
    for index in back_indices:
        value = 15 if index in electrodes_to_adjust else 5
        electrode_values["back"].append(value)

    # Assign values to right electrodes
    for index in right_indices:
        value = 15 if index in electrodes_to_adjust else 5
        electrode_values["right"].append(value)
        # electrode_values["right"].append(5)

    # Assign values to left electrodes
    for index in left_indices:
        value = 15 if index in electrodes_to_adjust else 5
        electrode_values["left"].append(value)
        # electrode_values["left"].append(5)

    return (electrode_values, adjusted)


# only for the generic sciospec program files (.eit)
def check_electrode(filename):
    #filename = 'electrode_1_1.eit'
    eit_data, amplitude, min_frequency, gain_setting, adc_range = read_eit_file(filename)
    print(amplitude, ' (mA) ', min_frequency, ' (hz) ' , ' gain: ', gain_setting, ' ', adc_range, ' V')
    AMPLITURE = amplitude

    # Create a new DataFrame with InjectionSetting and impedance values
    impedance_data = pd.DataFrame()
    impedance_data['InjectionSetting'] = eit_data['InjectionSetting']

    # Calculate impedance values for each row
    impedance_values = eit_data.apply(calculate_impedance, axis=1)

    # Expand impedance_values dictionary into separate columns
    impedance_data = pd.concat([impedance_data, impedance_values.apply(pd.Series)], axis=1)

    electrodes_to_adjust = []
    impedance_columns = [f'Impedance{i}' for i in range(1, 33)]

    for count, col in enumerate(impedance_columns):
        impedance_value = float(impedance_data[col][count])
        if impedance_value > IMPEDANCE_MAX:
            electrodes_to_adjust.append(count + 1)

    print("Electrodes to adjust:", electrodes_to_adjust)
    
    return electrodes_to_adjust

#Need the function to request 1 measurement from the Sciospec device and store it in a file
#def create_file():
 #   print('Need the function to request 1 measurement from the Sciospec device and store it in a file')


# Function that calculates the imdedance from the eit Dataframe
def calculate_impedance(row):
    real_columns = [f'reE{i}' for i in range(2, 65, 2)]
    imaginary_columns = [f'imE{i}' for i in range(1, 64, 2)]
    impedance_values = {}
    for i, (real_col, imaginary_col) in enumerate(zip(real_columns, imaginary_columns), 1):
        real_value = float(row[real_col])
        imaginary_value = float(row[imaginary_col])
        impedance = ((real_value ** 2 + imaginary_value ** 2) ** 0.5)/AMPLITURE
        impedance_values[f'Impedance{i}'] = "{:.13f}".format(impedance)
    return impedance_values


# Function to read the EIT file and extract the data
def read_eit_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
        
        ############################# Header part  ######################################
        # Read the header information ------------  return which ever header info may be needed 
        num_header_rows = int(lines[0])
        dataset_name = lines[2].strip()
        timestamp = lines[3].strip()
        min_frequency = float(lines[4]) # Minimum frequency [Hz]
        max_frequency = float(lines[5]) # Maximum frequency [Hz]
        frequency_scale = int(lines[6]) # Maximum frequency [Hz]
        frequency_count = int(lines[7]) # Frequency count
        amplitude = float(lines[8]) # Amplitude [A]
        frame_rate = float(lines[9])
        phase_correction_param = float(lines[10])
        gain_setting = float(lines[11]) # Gain-Setting (0...1; 1...10; 2...100; 3...1000)
        adc_range = int(lines[12]) # Gain-Setting (0...1; 1...10; 2...100; 3...1000)
        measure_mode = int(lines[13]) # Measure Mode (1...Single Ended; 2...Diff Skip-0; 3...Diff Skip-2; 4...Diff Skip-4)
        boundary = int(lines[14])
        switch_type = int(lines[15]) # Switch Type (1... Reed Relais, 2... Semicondutor Switches)
        measurement_channels = list(map(int, lines[16].split(':')[1].strip().split(',')))
        measurement_channels_independent = list(map(int, lines[17].split(':')[1].strip().split(',')))
        
        ############################# Main part  ######################################
        
        # Read the measurement data into a DataFrame
        data = []
        injection_settings = []
        for i in range(num_header_rows, len(lines)):
            if lines[i].strip() != '':
                if len(lines[i].strip().split()) == 2:
                    injection_settings.append(list(map(int, lines[i].strip().split())))
                else:
                    values = list(map(lambda x: "{:.13f}".format(float(x)), lines[i].strip().split('\t')))
                    data.append(values)


        # Adjust the length of injection settings
        if len(injection_settings) < len(data):
            injection_settings.append([injection_settings[-1][1], injection_settings[-1][1] + 1])

        df = pd.DataFrame(data, columns=[f'reE{i}' if i % 2 == 0 else f'imE{i}' for i in range(1, len(data[0]) + 1)])
        df['InjectionSetting'] = injection_settings
        
        # Returning a data frame that holders the injection pair electrodes and Every electrode real part and its imaginary part
        return df, amplitude, min_frequency, gain_setting, adc_range


##### create the function to read data from 32 system and make file like notebook


def get_impedances(IMPEDANCE_MAX, AMPLITUDE, num_electrodes, ch_group):
    scio_spec_measurement_config = ScioSpecMeasurementConfig(
    com_port="COM3",
    burst_count=1,
    n_el=num_electrodes,
    channel_group=ch_group,
    actual_sample=0,
    s_path="",
    object="circle",
    size=0.1,
    material="PLA",
    saline_conductivity=(0.0, "mS"),
    temperature=20.0,
    water_lvl=20.0,
    exc_freq=10000.0,
    datetime=datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
    )

    # Connect ScioSpec device
    COM_ScioSpec = connect_COM_port(port=scio_spec_measurement_config.com_port)

    # if reset:
    #     # Create an information message box
    #     # Perform a Soft Reset
    #     print ("Rebooting Device. Please Wait...")
    #     SoftwareReset(COM_ScioSpec)        
    #     time.sleep(10.0)
    #     return
    #     # Reconnect ScioSpec device
    #     COM_ScioSpec = connect_COM_port(port=scio_spec_measurement_config.com_port)

        # ResetMeasurementSetup(COM_ScioSpec)

    # Send configuration
    if num_electrodes == 16:
        scio_spec_measurement_config = conf_n_el_16_adjacent(
        COM_ScioSpec, scio_spec_measurement_config
        )
    else: #if num_electrodes == 32:
        scio_spec_measurement_config = conf_n_el_32_adjacent(
        COM_ScioSpec, scio_spec_measurement_config
        )


# Read out system callback
    SystemMessageCallback(COM_ScioSpec, prnt_msg=True)

# Start and stop single measurement
    measurement_data_hex = StartStopMeasurement(COM_ScioSpec)
# Delete hex in mesured buffer
    measurement_data = del_hex_in_list(measurement_data_hex)
# Reshape the full mesaurement buffer. Depending on number of electrodes
    split_measurement_data = reshape_full_message_in_bursts(
        measurement_data, scio_spec_measurement_config
    )
    measurement_data = split_bursts_in_frames(
        split_measurement_data, scio_spec_measurement_config
    )

    # Set to "True" to save single measurement
    save = False

    if save:
        files_offset = scio_spec_measurement_config.actual_sample
        for bursts in measurement_data:
            np.savez(
                scio_spec_measurement_config.s_path
                + "sample_{0:06d}.npz".format(files_offset),
                config=scio_spec_measurement_config,
                data=bursts,
            )
            files_offset += 1
            scio_spec_measurement_config.actual_sample = files_offset

        SystemMessageCallback(COM_ScioSpec, prnt_msg=False)
        # Load the .npz file
        tmp = np.load("sample_000000.npz", allow_pickle=True)

        # Access the 'data' key
        data = tmp['data']
    else:
        for bursts in measurement_data:
            data = bursts # since we only have one burst

    # Create lists to store the extracted data
    channel_groups = []
    excitation_stages = []
    timestamps = []
    measurements = {f'ch_{i+1}': [] for i in range(16)}

    # Iterate over the data and extract the relevant information
    for frame in data:
        channel_groups.append(frame.channel_group)
        excitation_stages.append(frame.excitation_stgs)
        timestamps.append(frame.timestamp)
        for i in range(16):
            measurement_name = f'ch_{i+1}'
            measurement_value = getattr(frame, measurement_name)
            measurements[measurement_name].append(measurement_value)

    # Create a DataFrame with the extracted data
    df = pd.DataFrame({
        'channel_group': channel_groups,
        'excitation_stages': excitation_stages,
        'timestamp': timestamps,
        **measurements
    })


    # Create a new DataFrame
    new_df = pd.DataFrame()

    if num_electrodes == 16:
        new_df['excitation_stages'] = df['excitation_stages'].reset_index(drop=True)
    else: #if num_electrodes == 32:
        # Add every second entry of excitation_stages column
        new_df['excitation_stages'] = df['excitation_stages'].iloc[::2].reset_index(drop=True)


	# Create DataFrames for channel_group 1
    channel_group_1 = df[df['channel_group'] == 1].reset_index(drop=True)
	# Create a new DataFrame for channel_group 1 with ch_1 to ch_16 columns
    df_1 = channel_group_1[['ch_1', 'ch_2', 'ch_3', 'ch_4', 'ch_5', 'ch_6', 'ch_7', 'ch_8', 'ch_9', 'ch_10', 'ch_11', 'ch_12', 'ch_13', 'ch_14', 'ch_15', 'ch_16']]

    df_2 = pd.DataFrame()
    if num_electrodes == 32:
        channel_group_2 = df[df['channel_group'] == 2].reset_index(drop=True)
        # Create a new DataFrame for channel_group 2 with ch_1 to ch_16 columns
        df_2 = channel_group_2[['ch_1', 'ch_2', 'ch_3', 'ch_4', 'ch_5', 'ch_6', 'ch_7', 'ch_8', 'ch_9', 'ch_10', 'ch_11', 'ch_12', 'ch_13', 'ch_14', 'ch_15', 'ch_16']]

    # Join new_df with df_1
    new_df = new_df.join(df_1)

    if num_electrodes == 32:
        # Rename columns of df_2
        df_2.columns = [f'ch_{i + 16}' for i in range(1, 17)]

        # Join new_df with df_2
        new_df = new_df.join(df_2)
    # Create a new DataFrame to store excitation stages and impedances
    impedance_data = pd.DataFrame()

	# Copy the excitation_stages column to the new DataFrame
    impedance_data['excitation_stages'] = new_df['excitation_stages']
	
    N = num_electrodes+1
	# Calculate the impedance for each channel
    for i in range(1, N):
        column_name = f'ch_{i}'
        real_values = new_df[column_name].apply(lambda x: np.real(x))
        imag_values = new_df[column_name].apply(lambda x: np.imag(x))
        magnitudes = np.sqrt(real_values**2 + imag_values**2)/AMPLITUDE
        impedance_data[f'impedance_{i}'] = magnitudes
    

    electrodes_to_adjust = []
    impedance_columns = [f'impedance_{i}' for i in range(1, N)]

    for count, col in enumerate(impedance_columns):
        impedance_value = float(impedance_data[col][count])
        if impedance_value > IMPEDANCE_MAX:
            electrodes_to_adjust.append(count + 1)

    print("Electrodes to adjust:", electrodes_to_adjust)
    
    return electrodes_to_adjust
        
def Create_MsgBox(msg):
    info_box = QMessageBox()
    info_box.setIcon(QMessageBox.Information)
    info_box.setWindowTitle("Info")
    info_box.setText(msg)
    info_box.setStandardButtons(QMessageBox.NoButton)
    info_box.setStyleSheet("QLabel{font-family: Poppins; font-size: 14px;}")
    info_box.show()
    return info_box
    
def reset():
    # Connect ScioSpec device
    COM_ScioSpec = connect_COM_port(port="COM3")

    # Create an information message box
    # Perform a Soft Reset
    print ("Rebooting Device. Please Wait...")
    SoftwareReset(COM_ScioSpec)        
    time.sleep(5.0)
    return