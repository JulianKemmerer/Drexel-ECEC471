#!/usr/bin/env python
import sys

#Column names
column_names = dict()
column_names[0] = "time"
column_names[1] = "in0"
column_names[2] = "in1"
column_names[3] = "sel"
column_names[4] = "out"
num_columns = len(column_names)

#Specifically indicate time index
time_index = 0
out_index = 4

#High low values
low = 0
high = 3.3
#Rising falling valiues (V/sec)


#High low switch points
low_thres = high * 0.1
high_thres = high * 0.9

#Determine is signal is high or low
def is_low(val):
	return val <= low_thres

def is_high(val):
	return val >= high_thres
	
#Return derivative of a signal, averages over window size
def deriv(x_list,t_list,window_size_n=10):
	derivatives = []
	for index in range(0,len(x_list)):
		derivatives = derivatives + [deriv_at_index(x_list,t_list,index,window_size_n)]
	return derivatives
	
#Get the derivative of a signal at index, averages over window size
def deriv_at_index(x_list,t_list,index,window_size_n=10):
	#Don't both with derivatives near start or end
	plus_minus_size = int(window_size_n/2) - 1
	if (index - plus_minus_size) < 0:
		return 0
	if (index + plus_minus_size) > (len(x_list)-1):
		return 0
		
	num = 0
	total = 0
	for i in range(index - plus_minus_size,index + plus_minus_size):
		dx = x_list[i+1] - x_list[i]
		dt = t_list[i+1] - t_list[i]
		dxdt = float(dx) / float(dt)
		total = total + dxdt
		num = num + 1
	
	return total/num

#Return map[col index] to list
def lists_from_file(f_name):
	began = False
	list_of_lists = []
	for line in open(f_name).read().split("\n"):
		#Conditions for not processing line
		if "begin" in line:
			began = True
			continue
		if "end" in line:
			continue
		if not(began):
			continue
		if line=="":
			continue
		
		#Split line on space
		num_strs = line.split(' ')
		#Convert to nums
		nums = []
		for s in num_strs:
			#Dont convert empty str
			if s!="":
				nums = nums + [float(s)]
		list_of_lists = list_of_lists + [nums]
	
	#Number of columns is assumed constant and = number of columns in first entry
	global num_columns
	num_columns = len(list_of_lists[0])
	
	#End data is list
	col_index_to_list = dict()
	#Initilize
	for column_index in range(0,num_columns):
		col_index_to_list[column_index] = []
	#Collect data	
	for l in list_of_lists:
		for column_index in range(0,num_columns):
			col_index_to_list[column_index] = col_index_to_list[column_index] + [l[column_index]]
	
	return col_index_to_list
	
#Retrun list of indicies where signal transitions
def transition_indices(signal_list):
	#Loop over all time indices
	prev_value = -1
	current_value = -1
	transition_indices = []
	for time_index in range(0,len(signal_list)):
		if prev_value == -1:
			prev_value = signal_list[time_index]
			continue
			 
		prev_value = signal_list[time_index-1]
		current_value = signal_list[time_index]
		#If rising
		if current_value >= prev_value:
			#Current val check for great than half high low and prev was not
			cur_val_high = current_value >= 0.5 * (high-low)
			prev_not_high = not( prev_value >= 0.5 * (high-low) )
			if cur_val_high and prev_not_high:
				#Trans here
				transition_indices = transition_indices + [time_index]
				
		#If falling
		else:
			#Current val check for less half high low and prev was not
			cur_val_high = current_value <= 0.5 * (high-low)
			prev_not_high = not( prev_value <= 0.5 * (high-low) )
			if cur_val_high and prev_not_high:
				#Trans here
				transition_indices = transition_indices + [time_index]
				
	return transition_indices




#Return state of signal at indices
#Returns map[time index]=state
#rising, falling, low, high (r,f,l,h)
def get_states(signal_list,time_list,indices_list):
	#Get derivative of this signal
	deriv_sig = deriv(signal_list,time_list)
	
	#Rising falling determined by percent of max
	max_deriv = max(deriv_sig)
	min_deriv = max(deriv_sig)
	
	#Build map
	state_at_index = dict()
	for index in indices_list:
		return None

#Return map[time index] = 50% time index
#-1 time index if no transition
def get_fifty_per_time(signal_list,indices_list):
	return None

#Return #[transition time sec, col0 prop time, col1 prop time ...,...]
#For a given output transition time index
#0 prop time if no transition
def get_trans_data(out_trans_time_index, fifty_per_time_indices):
	return None

def main():
	#First arg is file name
	#Get list of lists from file
	#List must be tab seperated numbers following 'begin' until 'end'
	col_index_to_list = lists_from_file(sys.argv[1])
	
	#Find trans points for out signal
	out_trans_indices = transition_indices(col_index_to_list[out_index])
	
	#At each transition of output find state of inputs
	#want map[columns index][time index] = state
	states_at_index = dict()
	for column_index in range(0,num_columns):
		print column_names[column_index]
		states_at_index[column_index] = get_states(col_index_to_list[column_index],col_index_to_list[time_index],out_trans_indices)
	
	#Collect 50% time indices at output transiton
	#map[column index][output time index] = 50% time index
	fifty_per_time_indices = dict()
	for column_index in range(0,num_columns):
		fifty_per_time_indices[column_index] = get_fifty_per_time(col_index_to_list[column_index],out_trans_indices)
	
	
	#For each output transition collect
	#map[trans time index] = [transition time sec, col0 prop time, col1 prop time ...,...]
	out_trans_data = dict()
	for out_trans_time_index in out_trans_indices:
		#Get data
		out_trans_data[out_trans_time_index] = get_trans_data(out_trans_time_index, fifty_per_time_indices)
		
	#Print the final data
	for out_trans_time_index in out_trans_data:
		to_print = ""
		#print each col state
		for col_index in range(0,num_columns):
			to_print = to_print + states_at_index[col_index][out_trans_time_index] + ","
		#Then print each info [out transition time sec, col0 prop time, col1 prop time ...,...]
		for val in out_trans_data[out_trans_time_index]:
			to_print = to_print + str(val) + ","
		
		print to_print

main()
