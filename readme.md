# Solar Trike *Earth Rover* (with R/C steering control)
* Locomotion powered *Solely* by *Solar*

![R/C Solar Trike](imgs/solar_trike.jpg)

![Chassis with Solar Panels](imgs/chassis-solar_panel.jpg)
## Project goal: Replace R/C steering control with pre-programmed (waypoint to waypoint) navigation using an onboard PICO microcontroller
* Pose data comes from GPS & IMU
* Pico coordinates everything:
    * Power comes from an onboard 3S (11.7v) LiPo battery
    * Buck converter to (5V)
    * gps (X-Y location)
    * Bosch BNO08x IMU (theta-Z orientation)
    * Calculates steering to next waypoint
    * Controls steering servo to follow path to next waypoint.
        * can loop or drive to a destination

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
    

## Next I need to create a steering algorithm

* This [path folowing video tutorial](https://www.youtube.com/watch?v=2qGsBClh3hE) shows (at 7:00) a nice animation of a path following algorithm credited to [Craig Reynolds](https://www.red3d.com/cwr/steer/)

![Path Following Animation](imgs/path-following.png)
