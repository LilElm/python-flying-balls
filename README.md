### python-flying-balls
<sub>
  A Python program to analyse real-time data from a DAQ board in order to process information on levitating spheres of superconducting indium.


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

 * Code:

   - [X] Implement parallel processing
   - [ ] Send trigger signal to power supply unit
   - [X] Acquire live data
   - [X] Pipe live data to new process
   - [ ] Manipulate data
   - [ ] Plot data
   - [X] Pipe manipulated data to new process
   - [X] Store manipulated data in a MySQL database


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

</sub>