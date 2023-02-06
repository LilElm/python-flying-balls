### python-flying-balls
<sub>
  A Python program to control, measure and analyse levitating spheres of superconducting indium submerged in superfluid helium in real-time.


</sub>

#### Aims
<sub>

 * To send signals via a DAQ board to manipulate the position of the levitating sphere

 * To acquire real-time data from the DAQ board

 * To physically interpret this data

 * To store this data in a MySQL database


</sub>

#### To Do
<sub>

 * Main Program:

   - [X] Evaluate force profile (via force_profile.py)
   - [X] Store force profile in MySQL database
   - [X] Implement multiprocessing
   - [X] Listen to user input and Process 3 for kill signal
   - [X] Implement GUI
   - [X] Implement customisable number of input channels

 * Process 1:

   - [X] Output force profile
   - [X] Acquire live data from relevant channels
   - [X] Synchronise output and input
   - [X] Pipe live data to Process 2 for manipulation
 
 * Process 2:

   - [X] Manipualte data for storage
   - [ ] Evaluate position of sphere
   - [X] Pipe unbuffered data to Process 3 for storing
   - [X] Pipe buffered data to Process 4 for plotting

 * Process 3:

   - [X] Store manipulated data in a MySQL database
   - [X] Send signal to main program once finished

 * Process 4:
   
   - [X] Plot real-time data using Qt

 * Process 5:
   
   - [X] Record automatically via Bluetooth camera


</sub>

#### Log
<sub>

 **01-Nov-22**

 * Ported previous code to Windows

 **03-Nov-22**

  * Created GitHub repository and uploaded previous work

 **08-Nov-22**

 * Multiple tasks (which would have allowed multiple sample rates) didn't work due to single clock

   * Multiple channels within single task added

 * Real-time plot added using pyqt package

 * Output signal added

 * Acquisition type changed to finite

   * Still allows for continuous acquisition, but with much higher sample rates

 **16-Nov-22**

 * Increased multiprocessing.connection.BUFSIZE to allow large pipe 'queue'

   * Need to wait until after data acquisition for MySQL database to be fully updated

 * Program successfully closes when store_data() recieves no more data to store

 **19-Nov-22**

 * Plotted stored data using Pyplot

 * MySQL query selects every nth row (method will be deprecated in future release)

   * Significant delay (~0.025 sec) between output and measured signals with trigger

   * Reduced delay (~0.009 sec) between output and measured signals without trigger

 * MySQL database INSERT statements found to be bottleneck

   * Entire force_profile.py script takes ~5.4 seconds including writing all data to text file for 100k sampling rate

   * Writing same data to MySQL database takes ~95.2 seconds via .executemany() statement

   * Perhaps print to .CSV during acquisition, then database post-acquisition?

 **22-Nov-22**

 * Morse code implemented in 'led_test.py' and 'morse.py'

 * makefile.bat added

 * MySQL bottleneck researched

   * Current insert method (cur.executemany()) is already optimal for real-time 

   * To optimise further, data can be output to .CSV and imported into MySQL post-acquisition

 * New branch 'csv-output' created

 * .CSVs created

 * Data uploaded to MySQL database post-acquisition

 **24-Nov-22**

 * Added channelDict to hold Channel objects

   * Allows customisable number of (and names for) channels

   * Will need to import this into mysql_update.py to configure table columns (could also be read from .CSV)

 **27-Nov-22**

 * mysql_update.py reads .CSV headers and adds columns into the relevant database tables if necessary

 * Merged csv-output branch into analog-output and master branches

 * Created branch 'gui'

 **12-Jan-23**

 * GUI progress uploaded

 * GUI can plot real-time data

 * GUI needs to automatically stop once data acquisition is over

   * If GUI tries to receive data and no data is sent, the program will not respond

 **13-Jan-23**

 * GUI can stop/start, even after many stop button presses

 * GUI needs stop button pressed before starting again

 * GUI checks if there is data to be received before trying to receive it

 * Checks added to GUI input parameters

 * force_profile.py slightly optimsed (derivative function applied only to non-zero part of profile)

 * Added output coil plot functionality to GUI

 **17-Jan-23**

 * force_profile.py changed to ramp_profile.py

 * gui.py reads and sends the profile (ramp, sine, half-sine, custom)

 * Half-sine profile works

 * Ramp/Half-sine profiles return inconsistent lengths

   * These must consistently be the same for the data acquisition to run smoothly

 * A start signal clears the plots

 **19-Jan-23**

 * ramp_profile.py and halfsine_profile.py changed to give exact profile lengths

 * store_data() updated to output measured channels to data.csv 

 * Position labels added to GUI plots

 **23-Jan-23**

 * camera.py added and controls the camera

 * The camera automatically begins recording on 'START'

 * 'STOP' must be pressed for the camera to stop recording

 * Buffer size increased to avoid data loss

 * mysql_update.py modified to work with current data output

 * shutil module and mysql_update.py are both incompatible with camera.py

   * Only rmtree has been imported from shutil in effort to work around any disfunction

   * mysql_update.py is called using the os module to keep the environments separate

 * Future work: keep camera connected until the program closes

 **25-Jan-23**

 * mysql_update.py changes file permissions to allow 'NETWORK SERVICE' as this automatically reverts

 * mysql_update.py moves files from ./tmp/ to ./dat/ and renames them according to their timestamp

 * Camera connection maintained

 * 'Save to File' button works

 * Icon and title added

 * Program neatened

 * pg.PlotWidget.setLabel() replaced by pg.LabelItem()

 * Save checkbox ticked by default

 * Invalid frequencies are rounded in halfsine_profile.py

   * Idle and rest times still flag errors in gui.py

 **01-Feb-23**

 * GUI no longer checks sampling rate / time compatibility

   * This was originally to ensure that profile array lengths were identical, but this is now adjusted during the program

 * GUI automatically updates 'rest' times to be equal, but due to the above adjustment, this is now not strictly necessary

 **02-Feb-23**

 * Custom profile functional

 * .env textbox functional

 * path textbox functional (outfolder)

 * Processes end cleaner (pipe stop signals)

 * Fixed camera (...again)

   * The camera doesn't like utf-8

 **04-Feb-23**

 * GUI plot pipes cleared if not self.signal_start.signal to avoid plotting data from previous runs

 * Master/GUI branches merged to update Master

 * Ramp branch created to configure the ramp profile

 **06-Feb-23**

 * Ramp profile scaled to reflect drive as opposed to velocity

</sub>