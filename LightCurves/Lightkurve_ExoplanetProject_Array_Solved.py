import pandas as pd
import lightkurve as lk
import numpy as np
import matplotlib.pyplot as plt
import sys
import astropy
from datetime import *

# If you want to start analysis from somewhere in the middle
mid_break = int(input("Enter the index from which u wish to analyse: "))


# Change the download_dir to the directory where you saved your excel sheet in
# input_dir = "{folder directory in your pc}" + "\\StarData_" + str(file_no) + ".csv"
# Note that you have to only change the text in the { } brackets, below is an example of my input_dir
input_dir = "LightCurves\StarData_1.csv"
print(f"Analysing File-1")

# Change the output_dir to the directory where you want the figures to be saved
# Below is an example of my output_dir:
output_dir = "D:\\test export"

# Note that we skip the first 4 rows from any of the excel sheets as they are not important
df = pd.read_csv(input_dir, skiprows=4)

for i in range(mid_break, df.shape[0]):

    starstr = "TIC " + str(df.iloc[i][0])
    print(f"Analysing index - {i}")

    try:
        initial = lk.search_lightcurve(starstr)  # Searching the data for the a given "starstr"
        rows = len(initial)
    except KeyboardInterrupt:
        sys.exit(print(f"Last file analysed is - 1, on index {i}"))
    except:
        print(f"{starstr}[all] skipped")
        continue

    # This is the program to analyse each subset data of a particular "starstr"
    for row in range(rows):

        try:
            file1 = initial[row].download(quality_bitmask="default").remove_nans()
            temporary_file = file1.remove_outliers(sigma=4).flatten()
        except KeyboardInterrupt:
            sys.exit(print(f"Last file analysed is - 1, on index {i}"))
        except:
            print(f"{starstr}[{rows}] skipped")
            continue

        # We use two seperate files to be analysed, as a result we get 2 figures for every subset
        # This is because the "to_periodogram" function does not do a good job in finding the accurate time period
        # The method we use does not guarentee a 100% accuracy either
        periodogram_file_1 = temporary_file.to_periodogram(method="bls")
        periodogram_file_2 = temporary_file.to_periodogram(method="bls", period=np.arange(1, 16, 0.01))

        time_period_file1 = periodogram_file_1.period_at_max_power
        time_period_file2 = periodogram_file_2.period_at_max_power

        final_file_1 = temporary_file.fold(period=time_period_file1)
        final_file_2 = temporary_file.fold(period=time_period_file2)

                    
        x1 = final_file_1["time"]
        y1 = final_file_1["flux"]
        x2 = final_file_2["time"]
        y2 = final_file_2["flux"]

        def timecorr(timearr):
            l = []
            for i in timearr: 
                i = i.to_datetime()
                i = i.total_seconds()
                l.append(i)
            return l
            
        x1 = timecorr(x1) 
        x2 = timecorr(x2)

        def fluxcorr(fluxarr):
            l = []
            for i in fluxarr:
                i = i.to_value()
                l.append(i)
            return l 
        
        y1 = fluxcorr(y1)
        y2 = fluxcorr(y2)

        z1=np.polyfit(x1,y1,18)
        f1=np.poly1d(z1)
        z2=np.polyfit(x2,y2,18)
        f2=np.poly1d(z2)

        x1_new=np.linspace(x1[1],x1[-1],10)
        y1_new=f1(x1_new)

        x2_new=np.linspace(x2[1],x2[-1],10)
        y2_new=f2(x2_new)
        
        
        plt.plot(x1, y1, 'o', x1_new,y1_new)
        plt.xlim(x1[0]-1,x1[-1]+1)
        plt.show
        plt.savefig(output_dir + "\\" + starstr + f"[{row}][normal][index {i}].png")  # Plot 1
        plt.close('all')
        
        plt.plot(x2, y2, 'o', x2_new,y2_new)
        plt.xlim(x2[0]-1,x2[-1]+1)
        plt.show
        plt.savefig(output_dir + "\\" + starstr + f"[{row}][arange][index {i}].png")  # Plot 1
        plt.close('all')