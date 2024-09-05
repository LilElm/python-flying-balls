### python-flying-balls
<sub>
  A Python program to control, measure and analyse levitating spheres of superconducting lead submerged in superfluid helium in real-time.


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

   - [X] Debug force profiles
   - [ ] Extend force profile options
     - [X] Ramp 
     - [X] Half-sine
     - [ ] Half-sine pulses
     - [X] Sine
     - [X] Custom
   - [ ] Configure output files
   - [ ] Reconnect the database
   - [X] Reimplement the 'Preferences' page
   - [ ] Write documentation
   - [ ] Configure error signals for threads
   - [ ] Assign spring constant box group to the ramp profile
   - [X] Disable double-clicking of buttons


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

 * Oscillator parameter inputs added to GUI

 * Ramp profile discontinuity fixed

 **15-Feb-23**

 * Freezing issue sorted by replacing 'break' with sys.exit() in processes

 * Database and output folder format modified to allow backups to occur at a later date

 **16-Feb-23**

 * All pipes cleared when stopped - allows spamming of start button

 * restore_files.py added to resort files from /out_processed/

   * Means that files can be reuploaded to database (with run number) if database is corrupted

 **10-Jun-23**

 * VBScript wrapper added to hide terminal whilst running

 * Text display added to GUI to replace terminal output

 **11-Jun-23**

 * Text display functionality improved

 * LED image added to signal state of program (functionality not yet added)

 **12-Jun-23**

 * Pipes have replaced signal_start so that the program can stop automatically

 **13-Jun-23**

 * Toolbar added (without much functionality)

 **16-Jun-23**

 * Splash screen added

 **17-Jun-23**

 * Preferences widget added (not connected)

 **19-Jun-23**

 * Preferences widget functionality added for all parameters

 **21-Jun-23**

 * GraphLayout() checks if the display is on before resetting the display on the start button

 * The stop button now sends a signal to stop the data acquisition as well as the GUI

 * More info sent to GUI console

 **19-Jul-23**

 * Fixed bug with clearing the plots before data had been plotted

   * 'done' signal sent from 'mainpulate_data' in main to 'update_plots' in GUI

   * Signal sent via data pipe once all data has been sent

 **04-Sep-23**

 * get_data() changed to have one buffer using np.memap and a view

 * store_data() deprecated

 * Real-time position data was successfully recorded today via a transmitter coil and LC circuit

   * Lock-in amplifier settings will need to be added in the future

 **05-Sep-23**

 * Program neatened

 * Unnecessary branches deleted

 * New branch (lock-in) created

 **11-Dec-23**

 * Camera settings working

 **01-Feb-24**

 * Output time interval fixed at 1/sampling_rate

 **21-Feb-24**

 * get_data() pipeline to GUI streamlined

 **02-Jun-24**

 * Branch restructure created to restructure the program around the GUI

 **05-Jun-24**

 * Class CoilChannel() contains parameters related to the control coils

 * Threads used to generate ramp/half-sine profiles

 **12-Jun-24**

 * Data acquisition running in thread (QRunnable)

 * GUI plots data using multiple threads (QRunnables)

 **13-Jun-24**

 * DAQ output works

 * Coil input data is plotted using GraphLayout

 * Compare textboxDict[textbox].textbox.text() to textboxDict[textbox].val

   * Is .val needed?

 **14-Jun-24**

 * Supervisor thread starts and waits for force profile threads, after which it starts the daq thread

 * Graph QRunnables are started continuously through a QTimer

 * Data is sampled before being piped

 * If there's too much data, data is sampled at time of plotting

 * Lines added to daq.py to stop if the main thread is not running, but have been commented out

 * DAQ np.memmap buffer created as tempfile.NamedTemporaryFile()

 **15-Jun-24**

 * Graphs call update function in main thread via signal

 * QRunnables are no longer continuously called via a QTimer, but are persistently running

   * The thinking is that this frees up the main thread, as it will no longer be occupied with starting new threads

   * The efficacy has not yet been tested

 * DAQ outputs text-based data file

 **16-Jun-24**

 * DAQ function samples data based on a 'pipe_rate' i.e. samples per second to be piped and plotted

 * Basic camera functionality added

 **17-Jun-24**

 * The camera signals are sent in separate threads

   * The camera will listen for a reply from camera.py

 * A Console() class has been added and integrated into the program

   * The console, like the graphs, can only update in the main thread

 * The stop button stops the DAQ and camera by piping signals and listening for replies in threads

 * Bug noticed in evaluating the ramp profiles

   * DAQ input array dimensions do not match for time inputs: (1, 1, 1, 6) and (2, 2, 2, 2) at 20,000 Hz

   * Fix from previous code edited and implemented

 * Custom force profiles reimplemented

 * Degrees converted to radians in generate_sine_profile() function

 * Temporary solution for output directory created in daq.py

   * Will need to read path from GUI in future

 **18-Jun-24**

 * Half-sine pulses profile redesigned and draft version implemented into GUI

 **21-Jun-24**

 * Shared textbox replaces shared parameters

 * generate_circular_motion_profile() added

 **28-Aug-24**

 * Camera checkbox added

 * Preferences tab reinstated

   * Connect/disconnect/record/stop camera buttons wired

 **29-Aug-24**

 * Preferences buttons wired

 * Duplicate start/stop camera functions merged

 **03-Sep-24**

 * GUI tab created in preferences menu

 * GUI refresh rate added into preferences menu

   * Evaluates sampling based on textbox entry and number of samples sent to GUI from DAQ

 **04-Sep-24**

 * Maximum time window displayed (plot) implemented

   * N.B. Some graphs occasionally freeze. Why?

 **05-Sep-24**

 * Start button checks self.daq_running == False before running

 * line.setData() removed from receive_data() in GraphLayout

   * This seems to have fixed the freezing

   * Occasionally, graphs are wiped once the plotting has finished


</sub>