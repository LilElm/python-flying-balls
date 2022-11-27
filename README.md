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
   - [ ] Implement GUI
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

</sub>