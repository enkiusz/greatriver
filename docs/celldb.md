# Secondlife cell database


## Cell entity

In the secondlife cell database system (referred to as 'celldb') a cell is a generalized component storing electrical energy. This can refer to:

- a single 18650 form-factor cell (sometimes called a "core")
- a high-capacity cell built using a number of smaller cells connected together in parallel
- an energy storage battery pack built out of a number of high-capacity cells connected in series
- a complete factory-made battery pack (for example a laptop battery) purchased for disassembly and individiual component cell reuse, can contain other components
  besides the individual cells themselves, such as a BMS

The single common property of all of the above items is that it can either contain or be part of other cells, therefore can serve as a kind of a container as well as being an individual cylindrical or pouch cell. In the general sense the "cell" can also contain things other than individual cells, for example a BMS, wires, temperature sensors, connectors and cooling equipment. These auxillary items are not restricted from being included as "cells" contained within even though they do not strictly store electrical energy. Their inclusion is a decision made for a particular use-case, for example servicing or end-to-end supply chain tracking.

The information available for each cell (be it a 18650 cell, a bigger "block" of cells) can be divided into 3 categories:

- a unique identifier
- a container cell identifier (if cell is contained within a bigger cell)
- fixed data
- log
- state

### Cell containment

Example hierarchy (physical placement)

/ < root >
/STRING~478239472389 << the string ( a series of serial connected cells )>>
/STRING~478239472389/CELL~1 << The individual cell withing the string (number counted from load being the lowest number )>>
/STRING~478239472389/CELL~1/BLOCK~4832428947238 << Individual parallel block within the cell >>
/STRING~478239472389/CELL~1/BLOCK~4832428947238/CTRL~4248923473 << the block controller board >>
/STRING~478239472389/CELL~1/BLOCK~4832428947238/SLOT~1-57 << an individual slot (for example with a core that can be replaced) >>
/STRING~478239472389/CELL~1/BLOCK~4832428947238/SLOT~1-57/C~2423784927489237 << a specific individual 18650 cell (aka core) in a cell slot >>

Example hierarchy (pool & functional)

/POOL~472894723 << the pool of cells >>
/POOL~734897389/incoming << incoming cells >>
/POOL~734897389/incoming/CELL~573897389753489 << individual incoming cell (aka core) >>
/POOL~734897389/incoming/PACK~5734895734589347 << an individual laptop pack incoming for disassambly >>

After initial sorting:
/POOL~734897389/precharge_pool << cells with voltage too low to charge normally, need to precharge >>
/POOL~734897389/junk << corroded, punctured or otherwise damaged beyond refurbishing >>

After full charge
/POOL~734897389/self_discharge_wait << cells having been charged and waiting for self-discharge to present itself >>

After self-discharge assessment

/POOL~734897389/storage << cells in long-term storage >>

### The Properties (aka props)

The static data is the information without a cell that is impossible or unlikely to change during it's lifecycle. Typically this would 
include properties specified during initial manufacturing:

- manufacturer brand and model
- form factor
- chemistry
- nominal, maximum and discharge cutoff voltages
- operating temperature ranges
- manufacturing plant, batch and date codes
- serial numbers
- designed maximum and average internal resistance
- designed nominal and minimum capacity together with tolerance specifications for those
- maximum charge/discharge currents
- cycle characteristics
- nominal discharge curves
- the layout (in case of battery packs)
- any other label information
- pack layout (nS x xP) for battery packs

These values can sometimes be subdivided further, for example discharge current is commonly specified as continuous and peak separately. Typically all of these are sourced from a datasheet, labels and markings on the cells themselves and do not change during the lifetime of a cell. One commonly reported piece of information is not included in this list: the cell wrap and ring colors. Although these are often used for quick visual identification they are prone to change as cells are often rewrapped during refurbishing.

The above list is not exhaustive nor authoritative but indicates the typical pieces of data specified for energy storage systems. It can be extended when required.

### The  (aka log)

The log aims to record the conditions found during cell refurbishment processing and service life in order to judge the cell's health and performance. This includes measurements commonly taken for refurbished cells, such as:

- internal resistance and open-circuit voltage measurements
- charge-discharge-charge cycle used to measure useable capacity
- temperature measurement during charge and/or discharge to check maximum temperature
- cell discharge curve logging

and may also include for example maximum current and temperature found in a cell during service life. In a more extreme example, a BMS system can constantly measure and log the cell's voltage and current in order to provide a precise estimate of the energy level in the cell.

The log contains an ordered list of entries, each entry has the following list of minimal fields:
{
    // reserved - for possible future implementation of JSON Schema
    "$schema":
    "$id":

    "ts": 13281789.121, // The timestamp of log entry being created, UNIX epoch
    "type": <ENTRY TYPE>
}

As you can see, only the only required fields are the timestamp which records the UNIX time when the log entry was created and the 
type which records the type of event. There is only one defined type currently:

- lifecycle

#### Standard log entries (type lifecycle)

These are standard log entries which cover the basics of a cell lifecycle. The only ones which is mandatory to be in the log is the
cell created which records the timestamp 

- cell created
- cell junked


Cell created
- manufactured
{
    // reserved - for possible future implementation of JSON Schema
    "$schema":
    "$id":

    "ts": 13281789.121, // The timestamp of log entry being created, UNIX epoch
    "type": "lifecycle",
    "event": "created",
    "path": ": "/FACTORY~3/BATCH~242" // Initial path
}

- obtained for refurbishing
{
    // reserved - for possible future implementation of JSON Schema
    "$schema":
    "$id":

    "$ctime": 13281789.121, // The timestamp of log entry being created, UNIX epoch
    "type": "lifecycle",
    "event": "created",
    "path": ": "/PURCHASE~5237895"
}

Cell junked:
- passing on to mineral recycling due to corrosion or other irreversible damage
- rapid unscheduled disassembly (for example thermal runawawy and fire)
{
    // reserved - for possible future implementation of JSON Schema
    "$schema":
    "$id":

    "ts": 13281789.121, // The timestamp of log entry being created, UNIX epoch
    "type": "lifecycle",
    "event": "junked"
    "tags": [       // these are optional to describe
        "fire",
        "recycled"
    ]
}

Change path:
- removal of cell from a diassembled pack into the cell pool
{
    // reserved - for possible future implementation of JSON Schema
    "$schema":
    "$id":

    "ts": 13281789.121, // The timestamp of log entry being created, UNIX epoch
    "type": "lifecycle",
    "event": "move",
    "path":{
        "old": "/POOL~734897389/incoming/PACK~5734895734589347",
        "new" : "/POOL~734897389/precharge_pool"
    }
}

- remanufacturing of cells from the cell pool into a new pack
{
    // reserved - for possible future implementation of JSON Schema
    "$schema":
    "$id":

    "ts": 13281789.121, // The timestamp of log entry being created, UNIX epoch
    "type": "lifecycle",
    "event": "move",
    "path":{
        "old": "/POOL~734897389/storage",
        "new" : "/STRING~478239472389/CELL~1/BLOCK~4832428947238/SLOT~1-57"
    }
}

- replacement of a damaged or misbehaving cell from a bigger battery or pack
removal of damaged cell:
{
    // reserved - for possible future implementation of JSON Schema
    "$schema":
    "$id":

    "ts": 13281789.121, // The timestamp of log entry being created, UNIX epoch
    "type": "lifecycle",
    "event": "move",
    "path":{
        "old": "/STRING~478239472389/CELL~1/BLOCK~4832428947238/SLOT~1-57",
        "new" : "/POOL~734897389/junk"
    }
}
addition of a replacement cell
{
    // reserved - for possible future implementation of JSON Schema
    "$schema":
    "$id":

    "ts": 13281789.121, // The timestamp of log entry being created, UNIX epoch
    "type": "lifecycle",
    "event": "move",
    "path":{
        "old": "/POOL~734897389/storage",
        "new" : "/STRING~478239472389/CELL~1/BLOCK~4832428947238/SLOT~1-57"
    }
}

### The State (aka state)

The state corresponds to the properties of a cell which change over time. A prime example of this is the cell's usable capacity. This measure decreases as the cell degrades over time. The most important point about the cell's state is that it is rarely measureable or specified directly. Most of the time the information contained in the Log and Fixed Data together allow the calculation of state characteristics.

A "usable capacity" of a cell is typically calculated from a full charge-discharge cycle measurement stored in the log. When, after a while of use the cell's capacity is measured again in this manner the "usable capacity" is likely to be lower. This new lower measurements needs to be reflected in the "usable capacity" state variable of a cell.

In a similar manner a "State of Health" indicator can be calculated for a cell depending on it's usable capacity in relation to the nominal (design) capacity.

Another state variable worth consideration is the rate of self-discharge. This state variable requires measurements of the cell open-cirtuit voltage a certain time after being fully charged and stored. Both of these events can be obtained from the cell's log and used to produce a self-discharge rate.

As can be seen the state variables for a cell are inferred based on observations (in the log) and expectations (in the fixed data) about the particular cell. As such they are not stored anywhere (except for the purposes of keeping a cache) but calculated on demand from other information.


### The Extras (aka extra)

The extra items for a cell are binary blobs which can serve a multitude of purposes and are usually handled as a whole and not parsed further. As an example, a photo of the cell will be an extra item. The extra items have only two elements:

{
    name:
    data:
}

### Query examples

Select all "likely fake" no-name Samsung cells that can still be re-used.

.props.brand == "SAMSUNG" and .state.self_discharge.assessment == "PASS" and .props.tags.likely_fake == true and (.props.tags.corrosion == true | not) and (.props.tags.precharge_fail == true | not) and (.props.tags.excessive_heat_charging == true | not)

