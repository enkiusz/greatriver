# Secondlife cell database


## Cell entity

In the secondlife cell database system (referred to as 'celldb') a cell is a generalized component storing electrical energy. This can refer to:

- a single 18650 form-factor cell
- a high-capacity cell built using a number of smaller cells connected together in parallel
- an energy storage battery pack built out of a number of high-capacity cells connected in series
- a complete factory-made battery pack (for example a laptop battery) purchased for disassembly and individiual component cell reuse

The single property of a cell is that it can either contain or be part of other cells, therefore can serve as a kind of a container as well 
as being an individual cylindrical or pouch cell. 

The information available for each cell (be it a 18650 cell or a bigger "block" of cells) can be divided into 3 categories:

- fixed data
- log
- state

### The Fixed Data

The static data is the information without a cell that is impossible or unlikely to change during it's lifecycle. Typically this would 
include properties specified during manufacturing:

- manufacturer brand and model
- form factor
- chemistry
- nominal, maximum and discharge cutoff voltages
- operating temperature ranges
- manufacturing date and plant
- serial numbers
- designed maximum and average internal resistance
- designed nominal and minimum capacity together with tolerance specifications for those
- maximum continuous and peak charge/discharge currents
- cycle characteristics
- nominal discharge curves
- the layout (in case of battery packs)
- any other label information
- etc.

Typically all of these are sourced from a datasheet, labels and markings on the cells themselves and do not change during the lifetime of a cell. 

### The Log

The log aims to record the conditions found during cell refurbishment processing and service life in order to judge the cell's health and performance. This includes measurements commonly taken for refurbished cells, such as:

- internal resistance and open-circuit voltage measurements
- charge-discharge-charge cycle used to measure useable capacity
- temperature measurement during charge and/or discharge to check maximum temperature
- cell discharge curve logging

and may also include for example maximum current and temperature found in a cell during service life. In a more extreme example, 
a BMS system can constantly measure and log the cell's voltage and current in order to provide a precise estimate of the energy
level in the cell.

### The State

The state corresponds to the properties of a cell which change over time. A prime example of this is the cell's usable 
capacity. This measure decreases as the cell degrades over time. The most important point about the cell's state is that it is
rarely measureable or specified directly. Most of the time the information contained in the Log and Fixed Data together allow
the calculation of state characteristics. 

A "usable capacity" of a cell is typically calculated from a full charge-discharge cycle measurement stored in the log. When, 
after a while of use the cell's capacity is measured again in this manner the "usable capacity" is likely to be lower. This new 
lower measurements needs to be reflected in the "usable capacity" state variable of a cell.

In a similar manner a "State of Health" indicator can be calculated for a cell depending on it's usable capacity in relation to
the nominal (design) capacity.

Another state variable worth consideration is the rate of self-discharge. This state variable requires measurements of the cell
open-cirtuit voltage a certain time after being fully charged and stored. Both of these events can be obtained from the cell's log
and used to produce a self-discharge rate.

As can be seen the state variables for a cell are inferred based on observations (in the log) and expectations (in the fixed data) about the particular cell. As such they are not stored anywhere (except for the purposes of keeping a cache) but calculated on demand from other information.

