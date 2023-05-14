# This script gives the reflectance vs wavelengths plot for a distributed
# Bragg reflector or a quarter-wave stack of high and low refractive index
# materials on a substrate and in a medium like air. You can change
# the parameters like refractive index, pairs, etc. The script asks for a central
# wavelength, where the reflection coatings are required to perform the
# best and the number of pairs of high-low refractive index materials. The
# model works with lossless dielectrics.

__author__ = "Amit Raj Dhawan"
__copyright__ = "Copyright 2023, Amit Raj Dhawan"
__credits__ = ["Amit Raj Dhawan"]
__version__ = 1.0
__maintainer__ = "Amit Raj Dhawan"
__email__ = "amitrajdhawan@gmail.com"
__status__ = "Stable release"
__licence__ = "Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)"



####### Load modules ###########################
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import win32api
import tkinter as tk
from tkinter import messagebox
import webbrowser
from PIL import Image, ImageTk
################################################


# Create the graphical user interface window using Tkinter and add a title.
root = tk.Tk()
root.title("Bragg reflector at normal incidence (v1.0)")

# Add image in GUI
image = Image.open("dbr2.png")
# Convert the image to a Tkinter-compatible format
tk_image = ImageTk.PhotoImage(image)
# Create a label to display the image
image = tk.Label(root, image=tk_image)
image.grid(rowspan=12, column=0, padx=10, pady=10,  sticky='w')

# Add message to the window
message = tk.Label(root, text="Enter real refractive indices", font=('Source Sans Pro', 13), fg='green')
message.grid(row=0, column=1, padx=10, pady=10,  sticky='e')

# Add another message with a clickable hyperlink.
message = tk.Label(root, text="Refractive index database:", font=('Source Sans Pro', 13), fg='blue')
message.grid(row=1, column=1, padx=10, pady=10,  sticky='e')
#Define a callback function
def callback(url):
   webbrowser.open_new_tab(url)
# 
link_button = tk.Button(root, text='https://refractiveindex.info', fg='blue')
link_button.grid(row=1, column=2)
link_button.bind("<Button-1>", lambda e:
    callback("https://refractiveindex.info"))



# Add input labels and entry boxes (with default values)
# Text labels to boxes
labels = [\
                'Refractive index of the medium (default: air): ', \
                'Refractive index of the substrate (default: SiO\u2082), n\u209B: ', \
                'Refractive index of the low index material (default: SiO\u2082), n\u2097: ', \
                'Refractive index of the high index material (default: Ta\u2082O\u2085), n\u2095: ', \
                'Is high refractive index material the last layer? (y/n): ', \
                'Central wavelength in nm: ', \
                'Number of pairs: ']

# Default value in each box.
default_values = ['1.000278','1.46', '1.4432', '2.1469', 'y', '532', '8']

# Declare a global variable called 'input_values' which will take values from each of the boxes.
global input_values
input_values = [] 

# Create the text labels, boxes, enter values, and append the values to "input_values"
for i, label in enumerate(labels):
    name = tk.Label(root, text=label, font=('Source Sans Pro', 13))
    name.grid(row=i+2, column=1, padx=10, pady=5, sticky='e') # sticky='e' makes text east-aligned.
    user_inputs = tk.StringVar(value = default_values[i]) # Add 'default_values' to 'user_inputs' as Tkinter class StringVar.
    # Enter the 'user_input' in entry boxes.
    my_entry = tk.Entry(root, textvariable=user_inputs) 
    my_entry.grid(row=i+2, column=2, padx=1, pady=5)
    # Append variable "input_values" using the default or updated user_inputs for use latter.
    input_values.append(user_inputs)


def ok():
    ########   Convert input string to numerical values   #########
    global n_0, n_s, n_L, n_H, input1, input2, lambda_0, pairs
    n_0 = float(input_values[0].get()) # Refractive index of the medium, usually air.
    n_s = float(input_values[1].get()) # Refractive index of the substrate. SiO2 here.
    n_L = float(input_values[2].get()) # Refractive index of the low index material Si02 at 540nm. https://refractiveindex.info/?shelf=main&book=SiO2&page=Kischkat
    n_H = float(input_values[3].get()) # Refractive index of the high index material. For Ta2O5 at 540nm. https://refractiveindex.info/?shelf=main&book=TiO2&page=Siefke
    input2 = input_values[4].get() # Is the top dielectric coating of high or low refractive index?
    lambda_0 = float(input_values[5].get()) # Central vacuum wavelength
    pairs = int(input_values[6].get()) # Number of pairs


    ### "lambda_0" is the central or vacuum wavelength declared by the user.
    ### "pairs" is the number of pairs of high-low or HL material stack declared by the user.
    h = lambda_0*1e-9 / 4  # Optical thickness of each thin film layer in 'm'
    lambda_begin = lambda_0 - 400 + 1e-6 # Starting wavelength on plot in natural numbers. Add 1e-6 to avoid 0, which becomes a problem in division.
    lambda_end = lambda_0 + 400 + 1e-6 # Last wavelength on plot in natural numbers. Add 1e-6 to avoid 0, which becomes a problem in division.
    # Consider wavelength range in pm, when lambda_0<400nm and leads to negative "lambda_begin". Convert negative 'lambda_begin' to pm.
    if lambda_begin < 0: 
        lambda_begin = (1000 + lambda_begin)/1000
    else:
        pass

    resolution_factor = 1 # Resolution factor > 1 if higher resolutions is required when zooming in.
    wavelength = np.zeros(round(lambda_end - lambda_begin)*resolution_factor)  # Preallocate "wavelength" vector.
    Reflectance = np.zeros(round(lambda_end - lambda_begin)*resolution_factor)  # Preallocate "Reflectance" vector.
    Transmittance = np.zeros(round(lambda_end - lambda_begin)*resolution_factor)  # Preallocate "Transmittance" vector.
    Absorbance = 0; # 5e-4; # From "Layertec planar 690nm mirrors_Batch_O119A031_Order_152469_Measurement report.pdf"



    for k in range(int(lambda_end - lambda_begin)*resolution_factor):  # Set loop for wavelengths.
        lambda_m = (k + lambda_begin) * 1e-9/resolution_factor  # Wavelength loop runs from "lambda_begin-400nm". Multiply by 1e-9 to convert nm to m.
        wavelength[k] = (k + lambda_begin)/resolution_factor
        phi = (2 * np.pi / lambda_m) * h  # Phase term.

        
        # Matrix of high index material single layer.
        M_H = np.array([[np.cos(phi),                   (1j / n_H) * np.sin(phi)],
                            [1j * n_H * np.sin(phi),        np.cos(phi)             ]])

        # Matrix of low index material single layer.
        M_L = np.array([[np.cos(phi),                   (1j / n_L) * np.sin(phi)],
                            [1j * n_L * np.sin(phi),        np.cos(phi)             ]])

            
        # Matrix of all the pairs, and another high index terminal layer to increase maximum reflectance.
        if input2 == 'y':
            M = (np.linalg.matrix_power( (M_H @ M_L), pairs ))  @  M_H  # The last term is due to a high index material termination: Glass--(HL)^pairs--H--Air
        else: # Matrix of all the pairs
            M = np.linalg.matrix_power( (M_H @ M_L), pairs)


        # Reflectance
        Reflectance[k] = (np.abs( (n_0*M[0,0] - n_s*M[1,1] + n_0*n_s*M[0,1] - M[1,0]) /
                               (n_0*M[0,0] + n_s*M[1,1] + n_0*n_s*M[0,1] + M[1,0])  )) ** 2
        
        # Transmittance
        Transmittance[k] = (n_s/n_0) * ( np.abs( (2*n_0) / 
                                                 (n_0*M[0,0] + n_s*M[1,1] + n_0*n_s*M[0,1] + M[1,0])) )**2
                            

    ########### Plot ###########
    plt.style.use('ggplot')
    plt.rcParams['axes.titlesize'] = 10
    plt.figure('Reflectance')
    # plt.plot(wavelength, 1-Transmittance, '.')
    plt.plot(wavelength, Reflectance)
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Reflectance')
    # Find wavelength at which Reflectance is maximum
    max_wavelength_index = np.where(Reflectance == max(Reflectance))
    min_wavelength_index = np.where(Transmittance == min(Transmittance))
    max_reflectance_wavelength = float(np.round(wavelength[max_wavelength_index],0)) # float works only when there is only 1 element.
    min_transmittance_wavelength = float(np.round(wavelength[min_wavelength_index],0)) # float works only when there is only 1 element.
    plt.title( '$R_{max} = $'+ str(np.round(max(Reflectance)*100,2)) + '% ' + \
                    'at ' + str(max_reflectance_wavelength) + 'nm\n' + \
                str(pairs) + ' pairs of $n_H/n_L = $' + str(np.round((n_H),2)) + '/' + str(np.round((n_L),2)))
    
    plt.figure('Reflectance logscale')
    plt.semilogy(wavelength, Reflectance)
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Reflectance')
    plt.title( '$R_{max} = $'+ str(np.round(max(Reflectance)*100,2)) + '% ' + \
                    'at ' + str(max_reflectance_wavelength) + 'nm\n' + \
                str(pairs) + ' pairs of $n_H/n_L = $' + str(np.round((n_H),2)) + '/' + str(np.round((n_L),2)))
    
    plt.figure('Transmittance logscale')
    plt.semilogy(wavelength, Transmittance)
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Transmittance')
    plt.title( '$T_{min} = $'+ str(np.round(min(Transmittance)*100,2)) + '% ' + \
                    'at ' + str(min_transmittance_wavelength) + 'nm\n' + \
                str(pairs) + ' pairs of $n_H/n_L = $' + str(np.round((n_H),2)) + '/' + str(np.round((n_L),2)))
    
    plt.figure('Transmittance')
    plt.plot(wavelength, Transmittance)
    plt.xlabel('Wavelength (nm)')
    plt.ylabel('Transmittance')
    plt.title( '$T_{min} = $'+ str(np.round(min(Transmittance)*100,2)) + '% ' + \
                    'at ' + str(min_transmittance_wavelength) + 'nm\n' + \
                str(pairs) + ' pairs of $n_H/n_L = $' + str(np.round((n_H),2)) + '/' + str(np.round((n_L),2)))

    
    # Arrange figures on monitor screen
    # Get_fignums gets the numbers of all the active figures. If the figure has a declared name like plt.figure('Name'), a number is assigned to it in ascending order.
    fig_nums = plt.get_fignums() 
    # Find the screen size in pixels so that the plots to arange from the right of the screen
    screen_s_realize = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
    # Arrange the figures side-by-side
    fig_width, fig_height, d_horizontal, d_vertical = 700,500,0,0
    inter_fig_h_padding = 1
    inter_fig_v_padding = 30
    # Arange figures from the right of the screen
    for i in fig_nums[0:2]:
       plt.figure(i).canvas.manager.window.wm_geometry("%dx%d+%d+%d" % (fig_width, fig_height, screen_s_realize[0]-fig_width, d_vertical))
       d_vertical = d_vertical + fig_height + inter_fig_v_padding
    # 
    d_vertical = 0 # Reset vertical displacement value to zero
    # 
    for i in fig_nums[2:4]:
       plt.figure(i).canvas.manager.window.wm_geometry("%dx%d+%d+%d" % (fig_width, fig_height, screen_s_realize[0]-2*fig_width-inter_fig_h_padding, d_vertical))
       d_vertical = d_vertical + fig_height + inter_fig_v_padding

    plt.show()
    


# Create the "About" button
def readme_message():
    messagebox.showinfo("Some info", "This app plots the reflectance and transmittance response of a distributed Bragg reflector or a quarter-wave stack of high and low refractive index materials on a substrate and in a medium like air. All the parameters can be changed. The app asks for a central wavelength, where the reflecor performs the best, and the number of pairs of high-low refractive index materials. The plots do not include absorption and scattering losses.")

about_button = tk.Button(root, text="Some info", font=('Source Sans Pro', 11), command=readme_message)
about_button.grid(row=0, column=2)


# Add graphical buttons and execute the corresponding definitions
def cancel():
    root.destroy()
cancel_button = tk.Button(root, text="Cancel", command=cancel, font=12, fg='red')
cancel_button.grid(row=len(labels)+2, column=1, padx=10, pady=10)


ok_button = tk.Button(root, text="OK", command=ok, font=12, fg='green')
ok_button.grid(row=len(labels)+2, column=2, padx=10, pady=10)

def clear_figure():
    plt.close('all')
clear_figure_button = tk.Button(root, text="Close figures", font=('Source Sans Pro', 11), command=clear_figure)
clear_figure_button.grid(row=len(labels)+3, column=2)


# Create the "About" button
def about_message():
    messagebox.showinfo("About", "Bragg reflector at normal incidence v1.0 \n Copyright© by Amit Raj Dhawan")
about_button = tk.Button(root, text="About", font=('Source Sans Pro', 11), command=about_message)
about_button.grid(row=len(labels)+3, column=1)



# Run the dialog box
root.mainloop() 