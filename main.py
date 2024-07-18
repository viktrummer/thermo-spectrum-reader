import sys
import os
import traceback
import matplotlib.pyplot as plt
from fisher_py.raw_file_reader import RawFileReaderAdapter, RawFileAccess
from fisher_py.data import Device
from fisher_py.data.business import Scan


# Get spectrum from file and return x (mass) and y (intensity)
def get_spectrum_data(raw_file: RawFileAccess, scan_number: int):
    # Get the scan from the raw file
    scan = Scan.from_file(raw_file, scan_number)

    mass_list = []
    intensity_list = []

    # Check if the scan contains centroid data or profile data
    if scan.has_centroid_stream and scan.centroid_scan.length > 0:
        for i in range(scan.centroid_scan.length):
            mass = scan.centroid_scan.masses[i]
            intensity = scan.centroid_scan.intensities[i]
            mass_list.append(mass)
            intensity_list.append(intensity)
    else:
        for i in range(len(scan.preferred_masses)):
            mass = scan.preferred_masses[i]
            intensity = scan.preferred_intensities[i]
            mass_list.append(mass)
            intensity_list.append(intensity)
    return mass_list, intensity_list


# Plot spectrum data and save to an image
def plot_spectrum(mass_list, intensity_list, output_path):
    plt.figure(figsize=(10, 6))
    plt.plot(mass_list, intensity_list, linestyle="-", color="b")
    plt.xlabel("Mass-to-Charge Ratio (m/z)")
    plt.ylabel("Intensity")
    plt.title("Mass Spectrum")
    plt.grid(True)
    plt.savefig(output_path)
    plt.close()


if __name__ == "__main__":
    try:
        # Define the raw file name
        fileindex = input("Enter the raw file index (1, 2, 3, ...): ")
        fileindex = int(fileindex)
        filename = f"Raw/{fileindex}.raw"
        args = sys.argv[1:]
        if len(args) > 0:
            filename = args[0]
        if filename == "":
            print("No raw file specified")
            sys.exit(0)

        # Check if the specified RAW file exists
        if not os.path.exists(filename):
            print(f"File does not exist in {filename}")
            sys.exit(0)

        # Create RawFileAccess object
        raw_file = RawFileReaderAdapter.file_factory(filename)
        if not raw_file.is_open or raw_file.is_error:
            print(f"Cant access the file, probably bad module")
            sys.exit(0)

        # Check if the raw file is being acquired
        if raw_file.in_acquisition:
            print(f"acquiring {filename}...")
            sys.exit(0)

        # Select the MS instrument, 1st instance of it
        raw_file.select_instrument(Device.MS, 1)

        # Get the specific spectrum (scan number X)
        scan_number = input("Enter the spectrum (may be called scan number): ")
        scan_number = int(scan_number)
        mass_list, intensity_list = get_spectrum_data(raw_file, scan_number)

        # Plot and save the spectrum data as an image
        if not os.path.exists("Output"):
            os.makedirs("Output")
        output_path = f"Output/spectrum_{fileindex}_{scan_number}.png"
        plot_spectrum(mass_list, intensity_list, output_path)
        print(f"Spectrum image saved to {output_path}")

        # Close the raw file
        print(f"Closing {filename}")
        raw_file.dispose()

        print(f"\n(C) Viktor Trummer, 2024")

    except Exception as e:
        print(e)
        print(traceback.print_exc())
        pass
