# Detailed Circuit Board Setup
* Pico set up powered by a small Li-Po battery through a buck converter
* GPS module
* Bosche BNO08x IMU

![Onboard Electronics](imgs/electronics.jpg)

* Hook up a switch to trigger collection of GPS data

![Switch Triggered GPS data collection](imgs/switch_triggered_gps.jpg)

* GPS data collected at seven spots nearby
    * Eastern-most corner of my garage
    * 2 corners of my driveway (at gutter)
    * 2 man-hole covers on Carrera (@ Santana & San Luis)
    * 2 man-hole covers at circles on Santana & San Luis

![Google map](imgs/google_map.png)

## Compare measured Lat/Lon coords with Google Map coords
* [GPS Calibration](gps-calib.ods) spreadsheet compares measured Lat/Lon coordinates with coords shown on Google Maps for several man-hole covers in the neighborhood.
    * The spreadheet converts Lat/Lon coords to X and Y values using the method explained [here](gps/notes.md)
    * Origin of the X-Y coordinates is set at the man-hole cover on Carrera at Garza.
    * Measured values are within a couple meters of map values
 

